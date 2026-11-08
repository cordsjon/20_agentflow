#!/usr/bin/env python3
"""panel_policy.py — deterministic panel resolver for the DOR gate.

    python3 scripts/panel_policy.py resolve <BACKLOG.md> <story-id | title-substring> [--json]

Decides WHICH panels a story must pass (spec: 20_agentflow docs/superpowers/specs/2026-11-08-panel-policy-design.md).
Three layers, in order; later layers only add, except track `none` which short-circuits:
  1 change type from the story text and title tags  -> track none | normal | heavy
  2 project default from panel_policy_data/projects.json (census rows; rules recomputed here)
  3 story keywords -> lenses (add-only)
No LLM, no network. Vendored byte-identical in 20_agentflow/scripts and 00_Governance/scripts — edit both.
Stdlib only. Never imports dor_gate (dor_gate imports this).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "panel_policy_data"
PROJECTS_ENV = "PANEL_POLICY_PROJECTS"  # test/ops override for the projects.json path

# --- layer 1: change type -------------------------------------------------------
AC_RE = re.compile(r"^\s*- (?:\[[ x]\] )?(?:\*\*)?AC-\d+", re.IGNORECASE | re.MULTILINE)  # same shape as dor_gate.AC_RE
TRIVIAL_RE = re.compile(
    r"\b(?:add(?:s|ed|ing)? (?:a |an |the |one )?(?:flag|option|switch)|renam(?:e|es|ing)|default value"
    r"|help text|typo|log line|wording)\b", re.IGNORECASE)
HEAVY_RE = re.compile(
    # new persistence / service / integration / queue / auth — needs a creating verb nearby.
    # The verb->noun window stops at , ; and at without/or/row(s): "new verifier without touching
    # the queue", "added or changed a service", "added as two rows to the ... table" (measured
    # false positives on 00_Governance Ready, 2026-11-08).
    r"\b(?:new|add(?:s|ed|ing)?|create(?:s|d)?|introduce(?:s|d)?|migrat(?:e|es|ing))\b"
    r"(?:(?!\b(?:without|or|rows?)\b)[^.,;\n]){0,40}"
    r"\b(?:table|schema|migration|service|daemon|integration|queue|scheduled job|cron(?:job)?"
    r"|auth(?:entication|orization)?|oauth|credentials?|secrets?|api[- ]keys?|login)\b"
    # combining two existing capabilities (bare "across" dropped: "across feature branches")
    r"|\b(?:combines?|merges?|unif(?:y|ies))\b[^.\n]{0,40}\b(?:capabilit(?:y|ies)|features?|commands?|skills?|pipelines?)\b"
    # mobile target — platform names, not the words "swift"/"ios" (adverb, path segment),
    # and not inside a hyphenated story id (US-CLIREG-ANDROID-FLUTTER-01)
    r"|(?<![\w-])(?:flutter|swiftui|kotlin|android|ios app|iphone|ipad)\b"
    # data deletion
    r"|\bdelet(?:e|es|ing)\b[^.\n]{0,30}\b(?:data|rows|records|files)\b", re.IGNORECASE)
TRIVIAL_MAX_AC = 2

# --- layer 3: keywords -> lenses (add-only) --------------------------------------
KEYWORD_LENSES = {
    "business": re.compile(r"\b(?:pricing|launch|market|customer)s?\b", re.IGNORECASE),
}

PANEL_ORDER = ["spec-panel", "architecture-panel", "test-panel"]
LENS_ORDER = ["security", "mobile", "osm", "business"]


class PolicyUnavailable(RuntimeError):
    """projects.json missing, unreadable, or hash-stale. The gate fails closed on this."""


def _rows_hash(rows: list[dict]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_projects(path: Path | None = None) -> dict:
    path = path or Path(os.environ.get(PROJECTS_ENV) or DATA_DIR / "projects.json")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise PolicyUnavailable(f"projects.json unreadable: {path}: {e}") from e
    if doc.get("rows_sha256") != _rows_hash(doc.get("rows", [])):
        raise PolicyUnavailable(f"projects.json rows_sha256 mismatch: {path} — re-run scripts/panel_census.py")
    return doc


def project_key(backlog: Path, *, use_git: bool = True) -> str | None:
    """Census key for a BACKLOG: its repo's path relative to ~/projects.
    Worktrees (…/.worktrees/<repo>/<sid>/…) map to <repo>. Outside ~/projects → None (uncensused)."""
    parts = backlog.resolve().parts if backlog.exists() else backlog.parts
    if ".worktrees" in parts:
        return parts[parts.index(".worktrees") + 1]
    top = backlog.parent
    if use_git:
        try:
            out = subprocess.run(["git", "-C", str(backlog.parent), "rev-parse", "--show-toplevel"],
                                 capture_output=True, text=True, check=True, timeout=5).stdout.strip()
            top = Path(out)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
    try:
        return str(Path(top).resolve().relative_to((Path.home() / "projects").resolve()))
    except ValueError:
        return None


def _project_defaults(row: dict, reasons: list[str]) -> tuple[set[str], set[str]]:
    panels: set[str] = set()
    lenses: set[str] = set()
    components = row["src_dirs"] >= 3 or row["compose"]
    if (components and (row["db"] >= 3 or row["svc"] >= 2)) or row["loc"] >= 15000 or row["queue"] >= 5:
        panels.add("architecture-panel"); reasons.append("project:architecture")
    if (row["svc"] >= 2 and row["cred"] >= 5) or row["hosts"] >= 10 or row["cred"] >= 15:
        lenses.add("security"); reasons.append("project:security")
    if row["test_ratio"] < 0.20:
        panels.add("test-panel"); reasons.append(f"project:test-ratio={row['test_ratio']}")
    if row["mobile"]:
        lenses.add("mobile"); reasons.append("project:mobile")
    if row["osm"]:
        lenses.add("osm"); reasons.append("project:osm")
    return panels, lenses


def _repo_declaration(repo_root: Path | None, reasons: list[str]) -> set[str]:
    """`.panel-policy.toml` [policy] <lens-or-panel> = true. Add-only: false is ignored."""
    if repo_root is None:
        return set()
    f = repo_root / ".panel-policy.toml"
    if not f.exists():
        return set()
    try:
        pol = tomllib.loads(f.read_text(encoding="utf-8")).get("policy", {})
    except (OSError, tomllib.TOMLDecodeError) as e:
        reasons.append(f"declaration-unreadable:{e}")
        return set()
    added = {k for k, v in pol.items() if v is True}
    for k in sorted(added):
        reasons.append(f"declared:{k}")
    return added


@dataclass
class Policy:
    track: str                       # none | normal | heavy
    panels: list[str] = field(default_factory=list)
    lenses: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    basis: str = "uncensused"        # census:<date> | uncensused | tag

    def as_dict(self) -> dict:
        return {"track": self.track, "panels": self.panels, "lenses": self.lenses,
                "reasons": self.reasons, "basis": self.basis}


def _change_track(text: str, tags: set[str], reasons: list[str]) -> tuple[str, bool]:
    """Returns (track, decided_by_tag)."""
    if "heavy" in tags:
        reasons.append("tag:heavy")
        return "heavy", True
    if "trivial" in tags:
        reasons.append("tag:trivial")
        return "none", True
    m = HEAVY_RE.search(text)
    if m:
        reasons.append(f"heavy:{m.group(0).strip()}")
        return "heavy", False
    m = TRIVIAL_RE.search(text)
    if m:
        n_ac = len(AC_RE.findall(text))
        if n_ac <= TRIVIAL_MAX_AC:
            reasons.append(f"trivial:{m.group(0).strip()} ac={n_ac}")
            return "none", False
        reasons.append(f"trivial-text-but-ac={n_ac}")
    return "normal", False


def resolve(story_text: str, project: str | None, *, title_tags: set[str] | frozenset[str] = frozenset(),
            projects: dict | None = None, repo_root: Path | None = None) -> Policy:
    reasons: list[str] = []
    tags = {t.lower() for t in title_tags}
    track, by_tag = _change_track(story_text, tags, reasons)
    pol = Policy(track=track, reasons=reasons, basis="tag" if by_tag else "uncensused")
    if track == "none":
        return pol
    panels = {"spec-panel"}
    lenses: set[str] = set()
    if track == "heavy":
        panels.add("architecture-panel")
    doc = projects if projects is not None else load_projects()
    row = next((r for r in doc["rows"] if r["project"] == project), None) if project else None
    if row is None:
        reasons.append("project:uncensused")
    else:
        if not by_tag:
            pol.basis = f"census:{doc.get('generated', '?')}"
        p2, l2 = _project_defaults(row, reasons)
        panels |= p2; lenses |= l2
    for name in _repo_declaration(repo_root, reasons):
        if name in ("architecture", "test"):
            panels.add(f"{name}-panel")
        elif name in LENS_ORDER:
            lenses.add(name)
    for lens, rx in KEYWORD_LENSES.items():
        if rx.search(story_text):
            lenses.add(lens); reasons.append(f"keyword:{lens}")
    pol.panels = [p for p in PANEL_ORDER if p in panels]
    pol.lenses = [l for l in LENS_ORDER if l in lenses]
    return pol


# --- CLI -------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(#{2,4}) (.*)$")
_LIST_TITLE_RE = re.compile(r"^- (?:~~)?\*\*(.+?)\*\*")
_TOP_ITEM_RE = re.compile(r"^(?:- |\d+\. )")
_TAG_RE = re.compile(r"`\[([^\]]+)\]`")
_ID_RE = re.compile(r"\bUS-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]+\b")
_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)\)")


def _find_entry(lines: list[str], selector: str) -> tuple[str, list[str]] | None:
    n = len(lines)
    for i, ln in enumerate(lines):
        h, l = _HEADING_RE.match(ln), _LIST_TITLE_RE.match(ln)
        if not (h or l):
            continue
        title = h.group(2) if h else l.group(1)
        hit = (selector in (m.group(0) for m in _ID_RE.finditer(title))) if _ID_RE.fullmatch(selector) else (selector in title)
        if not hit:
            continue
        j = i + 1
        if h:
            level = len(h.group(1))
            while j < n and not (_HEADING_RE.match(lines[j]) and len(_HEADING_RE.match(lines[j]).group(1)) <= level):
                j += 1
        else:
            while j < n and not (_HEADING_RE.match(lines[j]) or _TOP_ITEM_RE.match(lines[j])):
                j += 1
        return title, lines[i:j]
    return None


def story_input(backlog: Path, selector: str) -> tuple[str, str, set[str]] | None:
    """(story_id, text = entry + linked spec, title tags) for the CLI and for dor_gate."""
    found = _find_entry(backlog.read_text(encoding="utf-8").splitlines(), selector)
    if found is None:
        return None
    title, lines = found
    text = "\n".join(lines)
    link = _LINK_RE.search(text)
    if link:
        spec = (backlog.parent / link.group(1)).resolve()
        if spec.exists():
            text += "\n" + spec.read_text(encoding="utf-8")
    sid = next((m.group(0) for m in _ID_RE.finditer(title)), selector)
    return sid, text, {t.lower() for t in _TAG_RE.findall(lines[0])}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve", help="print the panel policy for one BACKLOG entry")
    r.add_argument("backlog", type=Path)
    r.add_argument("selector")
    r.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.backlog.exists():
        print(f"not-found: {a.backlog}", file=sys.stderr)
        return 2
    si = story_input(a.backlog, a.selector)
    if si is None:
        print("not-found: entry", file=sys.stderr)
        return 2
    sid, text, tags = si
    key = project_key(a.backlog)
    try:
        pol = resolve(text, key, title_tags=tags, repo_root=a.backlog.parent)
    except PolicyUnavailable as e:
        print(f"policy-unavailable: {e}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps({"story": sid, "project": key, **pol.as_dict()}))
    else:
        print(f"story: {sid}\nproject: {key or '(uncensused)'}\ntrack: {pol.track}\n"
              f"panels: {', '.join(pol.panels) or '-'}\nlenses: {', '.join(pol.lenses) or '-'}\n"
              f"basis: {pol.basis}\nreasons: {'; '.join(pol.reasons)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
