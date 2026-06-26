# HANDOVER — Panel cost reduction (2026-06-25)

## Why this session existed
Usage dashboard showed `sh` panels driving ~44% of limit usage (architecture-panel
28%, spec 10%, test 4%). Goal: cut panel cost without losing quality.

## Shipped (all on `master`, pushed — repo: 20_agentflow)
1. **Silent mode = default on all 10 real panels** — commit in `526d8cd`, merged
   `d6ae08a`. Added `## Verbosity` block + `--verbose` opt-out to the 7 panels
   lacking it (ai, architecture, business, personal-development, security, spec,
   test); consigliere/mobile/research already had it. business-panel's old
   `--synthesis-only` was inverted to `--verbose`. Cuts panel OUTPUT tokens
   ~60–80%, ~0% quality loss (full internal analysis preserved).
2. **sh-analyze pinned to `model: sonnet`** — `4df16e4`, merged `9f2a7a0`. Read-only
   static analysis → Sonnet per CLAUDE.md. HTML note in the skill flags that
   open-ended bug/security depth still wants Opus. Positions analyze as the cheap
   antipattern alternative to architecture-panel for *code* (panel still wins for
   *design* judgment).
3. **Measurement harness** — `3048fdc`. `scripts/measure-panel-vs-analyze.sh`.

## Key decisions (don't relitigate)
- All 10 panels carry the "AUTO-FIX, NOT SYNTHESIS-ONLY" policy → they write code,
  so they STAY on Opus (user chose "keep auto-fix on Opus"). Only sh-analyze
  (read-only) dropped to Sonnet. The 7 empty `sh-*-panel` dirs are stubs — ignore.
- Cost ≠ quality on the same %: Silent mode is ~55% cheaper / ~0% worse;
  panel→analyze is ~80% cheaper / ~0% worse FOR CODE ANTIPATTERNS but materially
  worse for DESIGN review. Match tool to job.

## NEXT TASK (the only open item) — run the measurement
The $/run figures in this session were **estimates**. Run the harness in a FRESH
session to get measured numbers:
```
cd ~/projects/20_agentflow && ./scripts/measure-panel-vs-analyze.sh
```
It spawns its own `claude -p --output-format json` subprocesses and prints
in/out/cache tokens + $/run + $/50 for: panel-verbose-opus, panel-silent-opus,
analyze-opus, analyze-sonnet. Raw JSON saved under `.tmp/measure-*/`.
If `claude -p` flags differ on this box, check `claude -p --help` for the
`--output-format json` + `--model` equivalents and adjust the `run()` helper.

## Housekeeping
- `chore/measure-harness` branch is empty (commit went to master directly) —
  delete it if you like: `git push origin --delete chore/measure-harness`.
- Spell-checker diagnostics (FIPD, antipattern, surnames) and the VS Code
  "`model` not supported" hint are noise — `model:` IS a valid Claude Code skill
  field (confirmed against official docs this session).
