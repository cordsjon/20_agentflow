#!/usr/bin/env python3
"""dor_gate.py — executable Definition of Ready (20_agentflow US-SH2-02).

    python3 scripts/dor_gate.py <BACKLOG.md> <story-id | title-substring>
                                [--track normal|bug-lite|hotfix] [--json] [--skip-score]

Exit 0 pass · 1 fail (one reason per line) · 2 not-found / ambiguous.
Human mode ends with `DOR-VERDICT: PASS` or `DOR-VERDICT: FAIL: <first reason>`.
`--json` prints {story, track, pass, reasons[], counts{us,ac}} as the first line.

Entry = a title line plus its body. Title forms: a heading `^#{2,4} ` or a
top-level list item `^- **…**` (its title is the bold text only). A heading entry ends at the next heading of equal
or higher level; a list entry ends at the next top-level list item or any heading.
Entries nest: a `### US-…` story inside `## Ready` is an entry of its own.
The selector matches TITLE LINES ONLY: an id (US-XXX-NN) as a whole word, or —
when the argument is not an id — a case-sensitive substring of the title text.

Score line (normal track): `spec-panel: <score> (<YYYY-MM-DD>, body:<12-hex>)`.
The digest is SHA-256 of the linked spec's text above its first `## Duo review`
or `## Codex review` heading, recomputed from the working tree; mismatch = stale-score.
The spec is the first `](….md)` link inside the entry, resolved from the BACKLOG's dir.
An entry with no spec link is scored on its own text instead: the digest is SHA-256 of
the entry's lines minus score lines and the `**State:**` line (a state flip is not a
content change), the title's trailing age counter (`[16d]`) dropped, trailing
whitespace dropped.
When the entry body has no user story but links a spec, US/AC are counted in the spec
(a multi-story spec's per-story coverage is what the panel score attests).

`--skip-score`: structural checks only. 00_Governance/scripts/backlog_dor_pipeline.py
runs the full check and routes score-only failures to its panel stage, which writes
the score line (`score_digest()` is the shared digest).
Vendored byte-identical at 00_Governance/scripts/dor_gate.py — edit both.
Stdlib only. Never edits anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Ids have one or more segments: US-W-01, US-SH2-01, US-GOV-DEBT-41, US-SVG-W2TESTS-01.
ID_PAT = r"US-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]+"
ID_RE = re.compile(rf"\b{ID_PAT}\b")
FULL_ID_RE = re.compile(rf"^{ID_PAT}$")
HEADING_RE = re.compile(r"^(#{2,4}) (.*)$")
LIST_TITLE_RE = re.compile(r"^- (?:~~)?\*\*(.+?)\*\*")
TOP_ITEM_RE = re.compile(r"^(?:- |\d+\. )")
TAG_RE = re.compile(r"`\[([^\]]+)\]`")
SCORE_RE = re.compile(r"spec-panel: (\d+(?:\.\d+)?) \((\d{4}-\d{2}-\d{2}), body:([0-9a-f]{12})\)")
LINK_RE = re.compile(r"\]\(([^)\s]+\.md)\)")
US_ID_LINE_RE = re.compile(rf"^\s*(?:#{{2,4}} |\*\*|- \*\*)?{ID_PAT}\b")
AS_A_RE = re.compile(r"\bAs an?\**\s.*\bI want\b", re.IGNORECASE)
AC_RE = re.compile(r"^\s*- (?:\[[ x]\] )?(?:\*\*)?AC-\d+", re.IGNORECASE)
REVIEW_MARKERS = ("\n## Duo review", "\n## Codex review")
THRESHOLD = 7.0
LITE_LINES = {  # reason-suffix -> phrase that must appear (case-insensitive)
    "root-cause": "root cause",
    "fix-plan": "fix plan",
    "regression-test": "regression test",
    "no-constraint-violations": "constraint",
    "estimate": "estimate",
}


@dataclass
class Entry:
    title: str
    lines: list[str]
    start: int  # 1-based line of the title

    @property
    def body(self) -> str:
        return "\n".join(self.lines)


@dataclass
class Result:
    story: str
    track: str
    reasons: list[str] = field(default_factory=list)
    counts: dict = field(default_factory=lambda: {"us": 0, "ac": 0})

    @property
    def passed(self) -> bool:
        return not self.reasons


def _entries(lines: list[str]) -> list[Entry]:
    """Every title line starts an entry; entries nest (a ### story inside ## Ready)."""
    out: list[Entry] = []
    n = len(lines)
    for i in range(n):
        h = HEADING_RE.match(lines[i])
        l = LIST_TITLE_RE.match(lines[i])
        if not (h or l):
            continue
        if h:
            level = len(h.group(1))
            j = i + 1
            while j < n:
                h2 = HEADING_RE.match(lines[j])
                if h2 and len(h2.group(1)) <= level:
                    break
                j += 1
            title = h.group(2)
        else:
            j = i + 1
            while j < n and not (HEADING_RE.match(lines[j]) or TOP_ITEM_RE.match(lines[j])):
                j += 1
            title = l.group(1)  # the bold text only: body bullets quoting an id are not titles
        out.append(Entry(title=title, lines=lines[i:j], start=i + 1))
    return out


def _select(entries: list[Entry], selector: str) -> tuple[Entry | None, str | None]:
    if FULL_ID_RE.match(selector):
        hits = [e for e in entries if any(m.group(0) == selector for m in ID_RE.finditer(e.title))]
    else:
        hits = [e for e in entries if selector in e.title]
    if not hits:
        return None, "not-found"
    if len(hits) > 1:
        return None, "ambiguous-id"
    return hits[0], None


def _track(entry: Entry, override: str | None) -> str:
    if override:
        return override
    tags = {t.lower() for t in TAG_RE.findall(entry.lines[0])}
    if "hotfix" in tags:
        return "hotfix"
    if "bug" in tags:
        return "bug-lite"
    return "normal"


def body_digest(spec_text: str) -> str:
    for m in REVIEW_MARKERS:
        if m in spec_text:
            spec_text = spec_text.split(m)[0]
            break
    return hashlib.sha256(spec_text.encode("utf-8")).hexdigest()[:12]


STATE_LINE_RE = re.compile(r"\*\*State:\*\*")
# Governance's groomer bumps a trailing age counter (`[16d]`) on 297/299 story headings
# every day; hashed as-is it made every entry score stale overnight (2026-09-27).
AGE_COUNTER_RE = re.compile(r"\s*\[\d+d\]\s*$")


def entry_digest(lines: list[str]) -> str:
    lines = [AGE_COUNTER_RE.sub("", lines[0])] + lines[1:] if lines else lines
    kept = [ln.rstrip() for ln in lines if not (SCORE_RE.search(ln) or STATE_LINE_RE.search(ln))]
    while kept and not kept[-1]:
        kept.pop()
    return hashlib.sha256("\n".join(kept).encode("utf-8")).hexdigest()[:12]


def spec_path(entry: Entry, backlog: Path) -> Path | None:
    link = LINK_RE.search(entry.body)
    return (backlog.parent / link.group(1)).resolve() if link else None


def score_digest(entry: Entry, backlog: Path) -> str:
    """What a score line's body: field must equal — the linked spec, else the entry itself."""
    spec = spec_path(entry, backlog)
    if spec is not None and spec.exists():
        return body_digest(spec.read_text(encoding="utf-8"))
    return entry_digest(entry.lines)


def find_entry(backlog: Path, selector: str) -> tuple[Entry | None, str | None]:
    return _select(_entries(backlog.read_text(encoding="utf-8").splitlines()), selector)


def _count_us_ac(text: str) -> dict:
    lines = text.splitlines()
    # A story is marked by its id line; "As a … I want" counts only where no id line
    # exists, so a titled story's own "As a" sentence is not a second story.
    us_idx = [i for i, ln in enumerate(lines) if US_ID_LINE_RE.match(ln)] \
        or [i for i, ln in enumerate(lines) if AS_A_RE.search(ln)]
    ac_idx = [i for i, ln in enumerate(lines) if AC_RE.match(ln)]
    return {"us": len(us_idx), "ac": len(ac_idx), "_us_idx": us_idx, "_ac_idx": ac_idx}


def _check_normal(entry: Entry, backlog: Path, res: Result, skip_score: bool) -> None:
    spec = spec_path(entry, backlog)
    if spec is not None and not spec.exists():
        res.reasons.append(f"spec-missing:{LINK_RE.search(entry.body).group(1)}")
        spec = None

    counts = _count_us_ac(entry.body)
    source = "entry"
    if counts["us"] == 0 and spec is not None:
        counts = _count_us_ac(spec.read_text(encoding="utf-8"))
        source = "spec"
    res.counts = {"us": counts["us"], "ac": counts["ac"]}
    if counts["us"] == 0:
        res.reasons.append("no-user-story")
    elif counts["ac"] == 0:
        res.reasons.append("no-acceptance-criteria")
    elif source == "entry":
        # per-US coverage: every US segment (from one US line to the next) holds >= 1 AC
        us_idx, ac_idx = counts["_us_idx"], counts["_ac_idx"]
        bounds = us_idx + [10**9]
        for k, s in enumerate(us_idx):
            if not any(s < a < bounds[k + 1] for a in ac_idx):
                res.reasons.append(f"us-without-ac:{k + 1}")

    if skip_score:
        return
    m = SCORE_RE.search(entry.body)
    if not m:
        res.reasons.append("no-score")
        return
    score = float(m.group(1))
    if score < THRESHOLD:
        res.reasons.append(f"score-below-{THRESHOLD}:{score}")
    digest = body_digest(spec.read_text(encoding="utf-8")) if spec else entry_digest(entry.lines)
    if digest != m.group(3):
        res.reasons.append("stale-score")


def _check_lite(entry: Entry, res: Result, hotfix: bool) -> None:
    low = entry.body.lower()
    if hotfix and "`[hotfix]`" not in entry.lines[0]:
        res.reasons.append("missing-hotfix-tag")
    for suffix, phrase in LITE_LINES.items():
        if phrase not in low:
            res.reasons.append(f"dor-lite-missing:{suffix}")


def check(backlog: Path, selector: str, *, track: str | None, skip_score: bool) -> tuple[int, Result]:
    entry, err = find_entry(backlog, selector)
    if entry is None:
        return 2, Result(story=selector, track=track or "unknown", reasons=[err])
    story = next((m.group(0) for m in ID_RE.finditer(entry.title)), selector)
    t = _track(entry, track)
    res = Result(story=story, track=t)
    if t == "normal":
        _check_normal(entry, backlog, res, skip_score)
    elif t == "bug-lite":
        _check_lite(entry, res, hotfix=False)
    elif t == "hotfix":
        _check_lite(entry, res, hotfix=True)
    else:
        return 2, Result(story=story, track=t, reasons=[f"unknown-track:{t}"])
    return (0 if res.passed else 1), res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("backlog", type=Path)
    ap.add_argument("selector", help="US-XXX-NN, or a title substring")
    ap.add_argument("--track", choices=("normal", "bug-lite", "hotfix"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-score", action="store_true",
                    help="structural checks only (for pipelines that run the panel afterwards)")
    a = ap.parse_args(argv)
    if not a.backlog.exists():
        print(f"not-found: {a.backlog}", file=sys.stderr)
        return 2
    code, res = check(a.backlog, a.selector, track=a.track, skip_score=a.skip_score)
    if a.json:
        print(json.dumps({"story": res.story, "track": res.track, "pass": res.passed,
                          "reasons": res.reasons, "counts": res.counts}))
        return code
    for r in res.reasons:
        print(f"FAIL {r}")
    print("DOR-VERDICT: PASS" if code == 0 else f"DOR-VERDICT: FAIL: {res.reasons[0]}")
    return code


if __name__ == "__main__":
    sys.exit(main())
