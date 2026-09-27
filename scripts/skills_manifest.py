#!/usr/bin/env python3
"""skills_manifest.py — the Shepherd skill pack's promotion manifest (US-SH2-04).

    python3 scripts/skills_manifest.py check
    python3 scripts/skills_manifest.py promote <name> [--expect-runtime-sha <sha256>]   # bundle -> ~/.claude/skills/<name>
    python3 scripts/skills_manifest.py retire  <name>   # bundle -> .claude/skills-retired/<name>, runtime copy removed
    python3 scripts/skills_manifest.py record  <name>   # bundle == runtime already: record synced_sha256

Manifest: skills-manifest.json
    {"version": 1, "skills": {"<dir>": {"status": "global|repo-local|retired",
                                        "since": "YYYY-MM-DD",
                                        "synced_sha256": "<sha256 of SKILL.md at the last outward copy; global only>"}}}

Rules
- check: every dir under .claude/skills/ that holds a SKILL.md appears exactly once
  (unlisted, missing-dir, duplicate-key, empty-dir, bad-status -> exit 1). Global entries
  are compared with the runtime copy: a digest mismatch is REPORTED (runtime-diverged /
  bundle-differs), not an error — the runtime is where skills get edited, and a report
  is what turns that into a `record` or a `promote`.
- Outward copies (promote, retire's runtime removal) are guarded by synced_sha256: if the
  runtime SKILL.md digest differs from the recorded one the command refuses
  (runtime-diverged, exit 1). A global entry with no recorded digest refuses too
  (unrecorded-runtime) — run `record` first, or, when the bundle deliberately wins over a
  runtime copy that was never recorded, pass `promote --expect-runtime-sha <sha of the runtime
  SKILL.md you reviewed>`; it proceeds only while the live file still has that digest.
- Runtime dirs not named in the manifest are never read, written or reported.
- Direction of truth for already-promoted skills is the RUNTIME (design principle 5).
Stdlib only. Writes are atomic (tempfile + replace).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSES = ("global", "repo-local", "retired")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _no_dup(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"duplicate-key:{k}")
        d[k] = v
    return d


def load(manifest: Path) -> dict:
    return json.loads(manifest.read_text(encoding="utf-8"), object_pairs_hook=_no_dup)


def save(manifest: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(manifest.parent), prefix=".manifest-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    Path(tmp).replace(manifest)


class Ctx:
    def __init__(self, skills: Path, runtime: Path, retired: Path, manifest: Path):
        self.skills, self.runtime, self.retired, self.manifest = skills, runtime, retired, manifest

    def bundle_skill(self, name: str) -> Path:
        return self.skills / name / "SKILL.md"

    def runtime_skill(self, name: str) -> Path:
        return self.runtime / name / "SKILL.md"


def cmd_check(ctx: Ctx) -> int:
    errors, drift = [], []
    try:
        data = load(ctx.manifest)
    except ValueError as e:
        print(f"ERROR {e}")
        return 1
    entries = data.get("skills", {})
    on_disk = sorted(d.name for d in ctx.skills.iterdir() if d.is_dir())
    for name in on_disk:
        if not ctx.bundle_skill(name).exists():
            errors.append(f"empty-dir:{name}")
        elif name not in entries:
            errors.append(f"unlisted:{name}")
    for name, e in entries.items():
        status = e.get("status")
        if status not in STATUSES:
            errors.append(f"bad-status:{name}")
            continue
        if status != "retired" and not ctx.bundle_skill(name).exists():
            errors.append(f"missing-dir:{name}")
        if status == "global":
            r = ctx.runtime_skill(name)
            if not r.exists():
                errors.append(f"runtime-missing:{name}")
            else:
                if sha256(r) != e.get("synced_sha256"):
                    drift.append(f"runtime-diverged:{name}")
                b = ctx.bundle_skill(name)
                if b.exists() and sha256(b) != sha256(r):
                    drift.append(f"bundle-differs:{name}")
    for x in errors:
        print(f"ERROR {x}")
    for x in drift:
        print(f"DRIFT {x}")
    print(f"[skills-manifest] {len(entries)} entries, {len(on_disk)} dirs, {len(errors)} errors, {len(drift)} drift")
    return 1 if errors else 0


def _guard_runtime(ctx: Ctx, name: str, entry: dict, expect: str | None = None) -> str | None:
    r = ctx.runtime_skill(name)
    if not r.exists():
        return None
    recorded = entry.get("synced_sha256") or expect
    if not recorded:
        return f"unrecorded-runtime:{name}"
    if sha256(r) != recorded:
        return f"runtime-diverged:{name}"
    return None


def cmd_promote(ctx: Ctx, name: str, expect: str | None = None) -> int:
    data = load(ctx.manifest)
    entry = data["skills"].get(name)
    if entry is None or not ctx.bundle_skill(name).exists():
        print(f"ERROR not-in-bundle:{name}")
        return 1
    if entry.get("status") == "retired":
        print(f"ERROR retired:{name}")
        return 1
    if (err := _guard_runtime(ctx, name, entry, expect)):
        print(f"REFUSED {err}")
        return 1
    src, dst = ctx.skills / name, ctx.runtime / name
    # Overlay, never rmtree: runtime-only files (evals/, notes) are the runtime's own.
    # rmtree deleted sh-handoff/evals/evals.json on 2026-09-27. A file removed from the
    # bundle therefore lingers in the runtime copy; the list below makes it visible.
    kept = sorted(str(p.relative_to(dst)) for p in dst.rglob("*")
                  if p.is_file() and not (src / p.relative_to(dst)).exists()) if dst.exists() else []
    shutil.copytree(src, dst, dirs_exist_ok=True)
    entry.update(status="global", since=date.today().isoformat(), synced_sha256=sha256(ctx.bundle_skill(name)))
    save(ctx.manifest, data)
    print(f"promoted {name} -> {dst}")
    for k in kept:
        print(f"  kept runtime-only: {k}")
    return 0


def cmd_retire(ctx: Ctx, name: str) -> int:
    data = load(ctx.manifest)
    entry = data["skills"].get(name)
    if entry is None:
        print(f"ERROR unlisted:{name}")
        return 1
    if (err := _guard_runtime(ctx, name, entry)):
        print(f"REFUSED {err}")
        return 1
    src = ctx.skills / name
    if src.exists():
        ctx.retired.mkdir(parents=True, exist_ok=True)
        dst = ctx.retired / name
        if dst.exists():
            print(f"ERROR already-retired-dir:{name}")
            return 1
        shutil.move(str(src), str(dst))
    rt = ctx.runtime / name
    if rt.exists():
        shutil.rmtree(rt)
    entry.pop("synced_sha256", None)
    entry.update(status="retired", since=date.today().isoformat())
    save(ctx.manifest, data)
    print(f"retired {name}")
    return 0


def cmd_record(ctx: Ctx, name: str) -> int:
    data = load(ctx.manifest)
    entry = data["skills"].get(name)
    b, r = ctx.bundle_skill(name), ctx.runtime_skill(name)
    if entry is None or not b.exists():
        print(f"ERROR not-in-bundle:{name}")
        return 1
    if not r.exists() or sha256(b) != sha256(r):
        print(f"REFUSED not-identical:{name}")
        return 1
    entry.update(status="global", synced_sha256=sha256(b))
    entry.setdefault("since", date.today().isoformat())
    save(ctx.manifest, data)
    print(f"recorded {name} {entry['synced_sha256'][:12]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-dir", type=Path, default=ROOT / ".claude" / "skills")
    ap.add_argument("--runtime-dir", type=Path, default=Path.home() / ".claude" / "skills")
    ap.add_argument("--retired-dir", type=Path, default=ROOT / ".claude" / "skills-retired")
    ap.add_argument("--manifest", type=Path, default=ROOT / "skills-manifest.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    for c in ("promote", "retire", "record"):
        sub.add_parser(c).add_argument("name")
    sub.choices["promote"].add_argument("--expect-runtime-sha", dest="expect",
                                        help="digest of the reviewed runtime SKILL.md (first adoption only)")
    a = ap.parse_args(argv)
    ctx = Ctx(a.skills_dir, a.runtime_dir, a.retired_dir, a.manifest)
    if a.cmd == "check":
        return cmd_check(ctx)
    if a.cmd == "promote":
        return cmd_promote(ctx, a.name, a.expect)
    return {"retire": cmd_retire, "record": cmd_record}[a.cmd](ctx, a.name)


if __name__ == "__main__":
    sys.exit(main())
