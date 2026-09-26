# CONTEXT — 2026-09-26-shepherd-v2-audit-design

_Generated procedurally by phase0-procedural.sh at 2026-09-26T11:47:50Z.
No LLM call — pure grep + stat. Reviewers can request deeper context on demand._

## 1. Spec under review

- **Path:** `/Users/jcords-macmini/projects/20_agentflow/docs/specs/2026-09-26-shepherd-v2-audit-design.md`
- **Last modified:** 2026-09-26 13:38:36
- **Lines:** 70
- **Bytes:** 8776
- **Project root:** `/Users/jcords-macmini/projects/20_agentflow`

### Section index

- Why
- Audit findings
- Design principles for v2
- Scope — user stories
- Decisions for the operator (Decide)
- Order and size
- Not in scope

## 2. Cited artifacts — grounded existence checks

This is the **grounding layer**. Every citation extracted from the spec was checked
against the filesystem. `OK` = path exists, `MISSING` = does not exist, `GLOB` =
matches via shell glob (count > 0).

### 2.1 Tilde paths

| Path | Status | Size / kind |
|---|---|---|
| `~/.claude/CLAUDE.md` | OK | file, 17706B |
| `~/.claude/commands` | OK | directory, 26 entries |
| `~/.claude/skills` | OK | directory, 98 entries |
| `~/projects/00_Governance/scripts/install_repo_hooks.py` | OK | file, 20452B |
| `~/projects/20_agentflow` | OK | directory, 26 entries |

### 2.2 Backticked filenames

| Filename | Status | Locations (up to 3) |
|---|---|---|
| `.claude/skills/sh-dor/SKILL.md` | OK | ~/projects/20_agentflow/.claude/skills/sh-dor/SKILL.md |
| `00_Governance/KNOWN_PATTERNS.md` | MISSING | — |
| `00_Governance/TENETS.md` | MISSING | — |
| `00_Governance/scripts/sync-global-skills.sh` | MISSING | — |
| `BACKLOG.md` | OK | ~/projects/20_agentflow/BACKLOG.md |
| `CLAUDE-LOOP.md` | OK | ~/projects/20_agentflow/CLAUDE-LOOP.md |
| `CLAUDE.md` | MISSING | — |
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
| `install_repo_hooks.py` | MISSING | — |
| `skills-lock.json` | OK | ~/projects/20_agentflow/skills-lock.json |
| `sync-global-skills.sh` | MISSING | — |

### 2.3 Slash-commands (skills)

| Command | Status | Path |
|---|---|---|
| `/lightsout` | OK | ~/.claude/commands/lightsout.md |
| `/loop` | OK | ~/.claude/commands/sh/loop.md |
| `/mop` | OK | ~/.claude/skills/mop/SKILL.md |

### 2.4 sh: panel skills

| Skill | Status | Path |
|---|---|---|
| `sh:dod` | OK | ~/.claude/commands/sh/dod.md |
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
