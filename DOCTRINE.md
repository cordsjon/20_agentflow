# Shepherd Doctrine

One file. Rules live in Governance; this repo keeps only what it executes. Replaced `DOR.md`, `DOD.md`, `KNOWN_PATTERNS.md`, `GOVERNANCE-GUIDE.md` and `CLAUDE-LOOP.md` on 2026-09-26 (spec `docs/specs/2026-09-26-shepherd-v2-audit-design.md`, US-SH2-01; DECISIONS.md Q5–Q9). Their history is in git; none is kept as a pointer.

## Sources

The operating rules for every governed project are, in precedence order:

1. `~/.claude/CLAUDE.md` — system-wide rules, workstyle, git operations.
2. `~/.claude/TENETS.md` — the ten tenets (`[TENET: …]` tags).
3. `~/projects/00_Governance/KNOWN_PATTERNS.md` — cross-project anti-patterns (KP-NNNN), including the FIPD taxonomy (KP-4974).

Nothing in this repo restates those. If a rule here contradicts them, they win and this file is wrong.

## DOR — Definition of Ready

**Gate:** must pass before implementation begins. An item that fails DOR stays in `BACKLOG.md#Refining`.

**Executable check:** `python3 scripts/dor_gate.py <BACKLOG.md> <story-id-or-title> [--track normal|bug-lite|hotfix] [--json]` (US-SH2-02). Exit 0 pass, 1 fail with one reason per line, 2 not-found/ambiguous. `/sh:dor` runs it and quotes the output. The track is read from the entry's tag: `[bug]` → bug-lite, `[hotfix]` → hotfix, else normal.

**Normal track** — the entry (or the spec it links) has ≥ 1 User Story, ≥ 1 Acceptance Criterion per story, and a valid panel score:

```
spec-panel: <score> (<YYYY-MM-DD>, body:<12-hex>)
```

`body:<12-hex>` is the first 12 hex digits of the SHA-256 of the linked spec's text above its first `## Duo review` or `## Codex review` heading. Appending review rounds keeps the score valid; editing the body invalidates it (`stale-score`). Score < 7.0 fails. The score comes from `/sh:spec-panel`.

**Bug DOR-lite** — for `[bug]` items. No US template, no panel score. Five lines, each present:

- **Root cause identified** — specific file/line/mechanism documented
- **Fix plan** — 1-3 concrete steps; if > 3 steps it's a feature, use the normal track
- **Regression test named** — which test file + test case will catch this
- **No constraint violations** — fix doesn't conflict with project constraints
- **Estimate** — XS (1 item) or S (2 items); larger = normal track

**Hotfix fast track** — a bug that is actively blocking development (server down, build broken, data corruption):

1. Add a bullet to `INBOX.md` immediately.
2. `/sh:triage` classifies it `[hotfix]` and moves it directly to `TODO-Today.md` (skips Ideation/Refining).
3. Bug DOR-lite is satisfied at triage time.
4. Autopilot executes it as the next queue item.

`/sh:workflow` must not generate a queue for an item that has not passed DOR.

## DOD — Definition of Done

**Gate:** must pass before deployment. The gate is the hook chain, not a checklist.

**Step 0 (once per clone):** `python3 ~/projects/00_Governance/scripts/install_repo_hooks.py ~/projects/20_agentflow`, then `--doctor` must report both hooks installed and reachable. `tests/test_dod_chain.py` proves each gate refuses its known-bad input in a scratch clone (US-SH2-03).

**Gates, by hook event** (`install_repo_hooks.py --list`, v6, 2026-09-26):

| Event | Gate | Posture | Refuses |
|---|---|---|---|
| pre-commit | spec-hierarchy | blocking | a staged `docs/superpowers/specs/*.md` with unbounded fan-out (≥ 4 Epics under one Solution) |
| pre-commit | verified-tag | blocking | a `[verified]` tag with no checkable evidence |
| pre-commit | reflex | warn-only | reflex patterns in added `.py` lines (bare `except Exception`, unguarded `await client…`, `.json()` without status check, unguarded writes, `fcntl`) |
| pre-commit | decisions-staleness | warn-only | a staged `DECISIONS.md` whose open `assumed` queue is ≥ 12 or holds a stale risk entry |
| pre-commit | repo-local `tools/precommit.d/*` | blocking | `10-skills-manifest`: `scripts/skills_manifest.py check` non-zero (US-SH2-04) |
| commit-msg | commit-trailer | blocking | a message without the mandated `Co-Authored-By: Claude <Family> <ver> <noreply@anthropic.com>` trailer |

There are no pre-push gates.

**Queue tail** (replaces the dead `sc` command chain):

```
1. commit        — the hooks above run; a refusal is the DOD failing
2. /sh:verify    — evidence pass: tests green, claims backed by output (after the commit passes the hooks, before merge)
3. /sh:finish    — merge / PR / branch cleanup
4. deploy        — project-specific; smoke per the project's own rule
```

`/sh:dod` prints the machine-readable `DOD-VERDICT:` line that `quality_gate.run_stage1_dod` consumes; its contract lives in `~/.claude/commands/sh/dod.md`.

## FIPD

Every finding is classified Fix / Investigate / Plan / Decide; Investigate and Decide carry an `Unknown:` clause. Defined once, in Governance: `~/projects/00_Governance/KNOWN_PATTERNS.md` KP-4974.
