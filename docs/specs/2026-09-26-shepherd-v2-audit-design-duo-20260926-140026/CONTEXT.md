# CONTEXT — 2026-09-26-shepherd-v2-audit-design

_Generated procedurally by phase0-procedural.sh at 2026-09-26T12:00:26Z.
No LLM call — pure grep + stat. Reviewers can request deeper context on demand._

## 1. Spec under review

- **Path:** `/Users/jcords-macmini/projects/20_agentflow/docs/specs/2026-09-26-shepherd-v2-audit-design.md`
- **Last modified:** 2026-09-26 14:00:14
- **Lines:** 284
- **Bytes:** 39354
- **Project root:** `/Users/jcords-macmini/projects/20_agentflow`

### Section index

- Why
- Audit findings
- Design principles for v2
- Scope — user stories
- Decisions for the operator (Decide)
- Order and size
- Not in scope
- Duo review — pre-panel round 1
- Findings — DEEPSEEK  
- Self‑flagged uncertainty  
- Findings — CODEX
- Self-flagged uncertainty

## 2. Cited artifacts — grounded existence checks

This is the **grounding layer**. Every citation extracted from the spec was checked
against the filesystem. `OK` = path exists, `MISSING` = does not exist, `GLOB` =
matches via shell glob (count > 0).

### 2.1 Tilde paths

| Path | Status | Size / kind |
|---|---|---|
| `~/.claude/` | OK | directory, 57 entries |
| `~/.claude/CLAUDE.md` | OK | file, 17706B |
| `~/.claude/TENETS.md` | OK | file, 6174B |
| `~/.claude/commands` | OK | directory, 26 entries |
| `~/.claude/commands/` | OK | directory, 26 entries |
| `~/.claude/commands/agentflow` | OK | directory, 11 entries |
| `~/.claude/commands/agentflow/` | OK | directory, 11 entries |
| `~/.claude/commands/sh` | OK | directory, 47 entries |
| `~/.claude/commands/sh/` | OK | directory, 47 entries |
| `~/.claude/commands/sh/finish.md` | OK | file, 3767B |
| `~/.claude/commands/sh/verify.md` | OK | file, 3732B |
| `~/.claude/hooks/observation-logger.sh` | OK | file, 4436B |
| `~/.claude/logs/skill-invocations.jsonl` | MISSING | — |
| `~/.claude/skills` | OK | directory, 98 entries |
| `~/.claude/skills/` | OK | directory, 98 entries |
| `~/.config/dagu/dags` | OK | directory, 157 entries |
| `~/.config/dagu/dags/skill-sync.yaml` | OK | file, 7107B |
| `~/.hermes/hermes-adapter/dags` | OK | directory, 2 entries |
| `~/.local/state/claude-observations/` | OK | directory, 86 entries |
| `~/projects/00_Governance/scripts/install_repo_hooks.py` | OK | file, 20452B |
| `~/projects/20_agentflow` | OK | directory, 26 entries |
| `~/projects/20_agentflow/*.md` | GLOB | 15 matches |

### 2.2 Backticked filenames

| Filename | Status | Locations (up to 3) |
|---|---|---|
| `.claude/skills/sh-dor/SKILL.md` | OK | ~/projects/20_agentflow/.claude/skills/sh-dor/SKILL.md |
| `.github/workflows/codex-review.yml` | OK | ~/projects/20_agentflow/.github/workflows/codex-review.yml |
| `00_Governance/KNOWN_PATTERNS.md` | MISSING | — |
| `00_Governance/TENETS.md` | MISSING | — |
| `00_Governance/scripts/install_repo_hooks.py` | MISSING | — |
| `00_Governance/scripts/sync-global-skills.sh` | MISSING | — |
| `BACKLOG.md` | OK | ~/projects/20_agentflow/BACKLOG.md |
| `CLAUDE-LOOP.md` | OK | ~/projects/20_agentflow/CLAUDE-LOOP.md |
| `CLAUDE.md` | MISSING | — |
| `DECISIONS.md` | OK | ~/projects/20_agentflow/DECISIONS.md;~/.claude/skills/DECISIONS.md |
| `DOCTRINE.md` | MISSING | — |
| `DOD.md` | OK | ~/projects/20_agentflow/DOD.md |
| `DOR.md` | OK | ~/projects/20_agentflow/DOR.md |
| `GOVERNANCE-GUIDE.md` | OK | ~/projects/20_agentflow/GOVERNANCE-GUIDE.md |
| `KNOWN_PATTERNS.md` | OK | ~/projects/20_agentflow/KNOWN_PATTERNS.md |
| `ORCHESTRATOR.md` | OK | ~/projects/20_agentflow/ORCHESTRATOR.md |
| `ORIGIN.md` | OK | ~/projects/20_agentflow/ORIGIN.md |
| `README.md` | OK | ~/projects/20_agentflow/tools/poster-generator/README.md;~/projects/20_agentflow/.pytest_cache/README.md;~/projects/20_agentflow/docs/README.md |
| `SKILLS.md` | OK | ~/projects/20_agentflow/SKILLS.md |
| `TENETS.md` | MISSING | — |
| `backlog_dor_pipeline.py` | MISSING | — |
| `commands/global/sh/dor.md` | OK | ~/projects/20_agentflow/.claude/commands/global/sh/dor.md |
| `dod.md` | OK | ~/projects/20_agentflow/.claude/commands/global/agentflow/dod.md;~/projects/20_agentflow/.claude/commands/global/sh/dod.md;~/.claude/commands/agentflow/dod.md |
| `dor.md` | OK | ~/projects/20_agentflow/.claude/commands/global/agentflow/dor.md;~/projects/20_agentflow/.claude/commands/global/sh/dor.md;~/.claude/commands/agentflow/dor.md |
| `goal.md` | OK | ~/projects/20_agentflow/.claude/commands/global/goal.md;~/.claude/commands/goal.md |
| `install_repo_hooks.py` | MISSING | — |
| `kp_integrity.py` | MISSING | — |
| `mission.md` | OK | ~/projects/20_agentflow/.claude/commands/global/mission.md;~/.claude/commands/mission.md |
| `scratchpad/panel_usage.py` | MISSING | — |
| `scripts/skills_manifest_check.py` | MISSING | — |
| `sh-spec-panel/SKILL.md` | OK | ~/projects/20_agentflow/.claude/skills/sh-spec-panel/SKILL.md;~/.claude/skills/sh-spec-panel/SKILL.md |
| `skill-sync.yaml` | MISSING | — |
| `skills-lock.json` | OK | ~/projects/20_agentflow/skills-lock.json |
| `skills-manifest.json` | MISSING | — |
| `sync-global-skills.sh` | MISSING | — |
| `tests/fixtures/backlog_*.md` | MISSING | — |
| `tests/test_dod_chain.py` | MISSING | — |
| `tests/test_dor_gate.py` | MISSING | — |

### 2.3 Slash-commands (skills)

| Command | Status | Path |
|---|---|---|
| `/lightsout` | OK | ~/.claude/commands/lightsout.md |
| `/loop` | OK | ~/.claude/commands/sh/loop.md |
| `/mop` | OK | ~/.claude/skills/mop/SKILL.md |
| `/triage` | OK | ~/.claude/commands/sh/triage.md |

### 2.4 sh: panel skills

| Skill | Status | Path |
|---|---|---|
| `sh:dor` | OK | ~/.claude/commands/sh/dor.md |
| `sh:parallel` | OK | ~/.claude/commands/sh/parallel.md |

## 3-6. Surrounding code, prior decisions, open questions, repo conventions

**Procedurally deferred.** This collector intentionally does not synthesize these
sections — they require judgment the grounding layer alone cannot provide.
Reviewers should pull what they need:

- For *surrounding code* of a flagged path: open the path directly.
- For *prior decisions*: check sibling specs in `/Users/jcords-macmini/projects/20_agentflow/docs/specs` (see section index).
- For *open questions inherited*: search the spec for "Q1", "Q2", etc.
- For *repo conventions*: read `/Users/jcords-macmini/projects/20_agentflow/CLAUDE.md` and `/Users/jcords-macmini/projects/20_agentflow/KNOWN_PATTERNS.md`.

## 7. What this collector did NOT check

- Function names, CLI sub-commands, and config keys (`escalation.to`, `schema_version` etc.) — these are spec-internal JSON schema fields, not external artifacts; no existence check applies.
- External URLs and resources.
- Path placeholders containing `<...>` or `...` — filtered out as noise.
- Whether file *contents* match the spec's claims about them. Only file existence is verified.
- Imports / call sites of cited code paths (would require an LSP or wider grep).

If a reviewer needs any of these, they should request explicitly.
