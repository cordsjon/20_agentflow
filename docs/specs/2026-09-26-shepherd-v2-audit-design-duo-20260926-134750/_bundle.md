# DUO REVIEW BUNDLE

## CONTEXT.md (procedural extraction, phase 0)

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

## SPEC.md (/Users/jcords-macmini/projects/20_agentflow/docs/specs/2026-09-26-shepherd-v2-audit-design.md)

# Shepherd v2 — Audit and Design

**Date:** 2026-09-26 · **Status:** Refining (spec-panel not yet run) · **Author:** session audit, one read-only research agent + parent verification

## Why

Agentflow ("Shepherd") was built in March 2026 as the operating system for agent-driven work. Since then the actual operating rules moved into `~/.claude/CLAUDE.md`, `00_Governance/TENETS.md`, the governance CLIs and the memory corpus. The repo kept accumulating tooling while its doctrine froze. This document records what the audit found and proposes the smallest v2 that closes the gap.

## Audit findings

Evidence is from `git log`, `ls` and `grep` on 2026-09-26 unless marked.

1. **Doctrine dormant, tooling alive.** `README.md`, `DOR.md`, `DOD.md`, `ORCHESTRATOR.md`, `GOVERNANCE-GUIDE.md`, `CLAUDE-LOOP.md`, `KNOWN_PATTERNS.md`, `SKILLS.md`: no commits since March–April 2026. Last 60 days: 49 commits, all in `.claude/` (14), `experts/` (7), `data/`, `BACKLOG.md`, `tests/`, `scripts/`, `dags/`. [verified]
2. **Gates are prose.** No script, hook or test in `scripts/` or `tests/` parses `BACKLOG.md`, checks a spec-panel score, or enforces the DOD queue tail. `tests/` covers `nosignups_catalog` and `panel_propagation` only. [verified by agent, spot-checked]
3. **The DOD queue tail is dead.** `DOD.md:43-49` chains `/sc:analyze → /production-code-audit → /sc:cleanup → /sc:test → /commit-smart`. None of these exist in `~/.claude/commands` or `~/.claude/skills` today; the repo's own namespace is `/sh:`. `DOD.md` has 5 `sc:` references, `DOR.md` has 3. [verified]
4. **Skill catalogue: 75 bundled, 18 are panels.** `.claude/skills/` holds 11 `agentflow-*` and 64 `sh-*` skills. Only `sh-4-reviewer-panel` and `sh-spec-panel` were promoted to `~/.claude/skills` (both 2026-08-25, newer than the bundled copies). The rest are reachable only when `20_agentflow/.claude/skills` is an additional working directory. A promotion tool exists: `00_Governance/scripts/sync-global-skills.sh`. [verified]
5. **Two namespaces for the same gate.** `sh:dor`/`sh:dod` and `agentflow:dor`/`agentflow:dod` both load in a session. Nothing says which is canonical. [verified from the session's skill list]
6. **Doctrine duplicated in Governance, which won.** Agentflow `KNOWN_PATTERNS.md` is 114 lines, frozen April; Governance's is the maintained one (32k lines). Tenets, NOT DONE line, `/mop`, `/lightsout`, evidence rule, log-decisions, session budget gate, handover stamp gate, deps registry: all live outside agentflow and postdate it. [verified]
7. **Stale clones everywhere.** `40_convergence/agentflow`, `50_KETO/agentflow`, `MAC/agentflow`, `PY-Gen/agentflow` are submodule/copy checkouts of this repo frozen at the March "governance: sync" commits. The `40_convergence` one carries two never-pushed commits (`33547b5`, `601de58` "add Codex PR review workflow") and an uncommitted `KNOWN_PATTERNS.md` restructure. `cordsjon/agentflow.git` and `cordsjon/20_agentflow.git` resolve to the same GitHub repo. [verified]
8. **Stale content.** `AGENT_CAPABILITIES.md:113` "GPT-4 tier"; `ORIGIN.md` frames Superpowers/SuperClaude as merged-in when they are separate live skill trees; a 17 MB `.pptx` and a `.numbers` file in the repo root; `docs/*-playground.html` (April) unreferenced by anything. [verified by agent]
9. **Still unique, worth keeping.** FIPD with the mandatory `Unknown:` clause on Investigate/Decide (`DOD.md:12`, `KNOWN_PATTERNS.md:9-17`); the two-speed DOR (Bug DOR-lite / hotfix fast track, `DOR.md:18-35`); `CLAUDE-LOOP.md`'s worked autopilot design (never implemented; dagu nightshift and `/loop` now cover the runtime). [inference on "unique": agent scanned Governance headers, not bodies]

## Design principles for v2

- **One source per rule.** [TENET: do-no-harm, repurpose-before-build] Rules live in Governance (`TENETS.md`, `KNOWN_PATTERNS.md`, `CLAUDE.md`). Agentflow keeps only what it executes.
- **A gate that nobody runs is documentation.** Every gate in v2 is either a CLI/hook with a positive control, or it is deleted.
- **Skills are the product.** Agentflow becomes the skill pack ("Shepherd"), versioned, with an explicit promotion list. [TENET: mva]
- **Measure before consolidating.** 18 panels is past abstract-on-third, but merging them without usage data is a guess. [TENET: abstract-on-third]

## Scope — user stories

**US-SH2-01 — Doctrine collapse.** As the operator, I want `DOR.md`, `DOD.md`, `KNOWN_PATTERNS.md`, `GOVERNANCE-GUIDE.md` in agentflow replaced by one `DOCTRINE.md` that points to the Governance sources, so that no rule exists twice.
- AC-1: `grep -rn "sc:" *.md .claude/skills` returns 0 hits.
- AC-2: `KNOWN_PATTERNS.md` in agentflow is a ≤20-line pointer to `00_Governance/KNOWN_PATTERNS.md` and carries the FIPD definitions and the `Unknown:` rule verbatim from there (the one thing Governance imports from agentflow, not the reverse).
- AC-3: The Bug DOR-lite / hotfix track survives, as a section of `DOCTRINE.md`.

**US-SH2-02 — Executable DOR.** As an agent, I want `sh:dor` to run a script, so that "Ready" is checked, not asserted.
- AC-1: `scripts/dor_gate.py <BACKLOG.md> <story-id>` exits 1 unless the entry has ≥1 US, ≥1 AC per US, and a recorded spec-panel score ≥ 7.0; exits 0 otherwise; `--json` output.
- AC-2: A positive control test (an entry that must fail, one that must pass) in `tests/`.
- AC-3: `.claude/skills/sh-dor/SKILL.md` invokes the script and quotes its output; it no longer restates the checklist.
- Grep before define: check `00_Governance/scripts/` for an existing backlog/DOR parser first (`decisions_probe_queue`, `handover_stamp_gate` are the closest known).

**US-SH2-03 — Executable DOD.** As an agent, I want the DOD to be the existing hook chain, so that agentflow does not carry a second one.
- AC-1: `DOD.md` queue tail replaced by: `install_repo_hooks.py` v4 gates + `/sh:verify` + `/sh:finish`. No command is named that does not resolve in `~/.claude/commands` or the loaded skill list.
- AC-2: `python3 ~/projects/00_Governance/scripts/install_repo_hooks.py --list ~/projects/20_agentflow` shows the gates installed on this repo.

**US-SH2-04 — Skill pack with a promotion list.** As the operator, I want a `SKILLS.md` that says for each bundled skill: global / repo-local / retired, so that sessions outside agentflow get the right set.
- AC-1: `skills-lock.json` regenerated; every `.claude/skills/*` dir appears in exactly one of the three lists.
- AC-2: The global list is applied with `sync-global-skills.sh` and `ls ~/.claude/skills` matches it.
- AC-3: `agentflow:*` and `sh:*` duplicates resolved to one namespace (Decide, below).

**US-SH2-05 — Panel usage measurement (Investigate).** Before merging panels, count invocations per panel over the last 90 days from the skill-invocation observations the hooks already capture. Output: a table in this spec. Panels with 0 invocations are candidates for retirement; the rest stay as-is in v2. Unknown: where the observation log is persisted and whether it covers non-`/private/tmp` sessions.

**US-SH2-06 — Clone cleanup (Plan).** Replace the four frozen `agentflow/` checkouts with a one-line pointer file. Before deleting `40_convergence/agentflow`: cherry-pick or archive `601de58` (Codex PR review workflow) and diff its `KNOWN_PATTERNS.md` restructure against the live repo. Deleting un-merged work is on the still-ask list, so this story starts with a report, not a delete.

**US-SH2-07 — Repo hygiene.** Move `Agentflow-Skills-in-Action-2.pptx` and the `.numbers` file out of git (Kingston backup per the large-file rule); delete `docs/*-playground.html`; fix `AGENT_CAPABILITIES.md:113`; rewrite `ORIGIN.md`'s framing in one paragraph.

## Decisions for the operator (Decide)

1. Namespace: keep `sh:` (64 skills, README, GOVERNANCE-GUIDE) and retire `agentflow:*`, or the reverse. Recommendation: keep `sh:`, fewer renames. Unknown: whether any dagu DAG or Hermes chain calls `agentflow:*` by name.
2. Does `CLAUDE-LOOP.md` get archived as a design record, or deleted? Recommendation: archive under `docs/archive/` with a header pointing at dagu nightshift.
3. Does Shepherd stay a separate repo, or become `00_Governance/skills-pack/`? Recommendation: separate repo, because Governance already sync-copies skills outward and a second inward path would create a loop.

## Order and size

01 → 03 → 02 → 04 (each ≤ 1 day) · 05 and 07 anytime (≤ 2 h each) · 06 last, after the operator answers Decide-1.

## Not in scope

Rewriting any panel's prose. Building a new orchestrator (`superpowers:dispatching-parallel-agents`, `sh:parallel`, the Workflow tool and dagu already cover routing). Touching the `experts/` and `dags/` directories, which are the live part.
