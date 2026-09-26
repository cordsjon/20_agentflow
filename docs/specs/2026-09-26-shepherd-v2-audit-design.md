# Shepherd v2 — Audit and Design

**Date:** 2026-09-26 · **Status:** Refining → awaiting Decide-1 (duo pre-panel round 1, spec-panel 7.75, Codex post-panel round 2 all applied) · **Author:** session audit, one read-only research agent + parent verification · **Rev 2** (2026-09-26 14:xx, after duo review round 1)

## Why

Agentflow ("Shepherd") was built in March 2026 as the operating system for agent-driven work. Since then the actual operating rules moved into `~/.claude/CLAUDE.md`, `~/.claude/TENETS.md`, the governance CLIs and the memory corpus. The repo kept accumulating tooling while its doctrine froze. This document records what the audit found and proposes the smallest v2 that closes the gap.

**Terms.** *Gate* = a check that can refuse (exit ≠ 0, hook block). *Command* = a `~/.claude/commands/<ns>/<name>.md` file, invoked as `/<ns>:<name>`. *Skill* = a `.claude/skills/<name>/SKILL.md` directory. A gate is implemented by a script or hook; a command or skill may call one, but is not one.

## Audit findings

Evidence is from `git log`, `ls` and `grep` on 2026-09-26 unless marked. Cross-repo paths are absolute.

1. **Doctrine dormant, tooling alive.** `README.md`, `DOR.md`, `DOD.md`, `ORCHESTRATOR.md`, `GOVERNANCE-GUIDE.md`, `CLAUDE-LOOP.md`, `KNOWN_PATTERNS.md`, `SKILLS.md`: no commits since March–April 2026. Last 60 days: 49 commits, all in `.claude/` (14), `experts/` (7), `data/`, `BACKLOG.md`, `tests/`, `scripts/`, `dags/`. [verified]
2. **Gates are prose.** No script, hook or test in `scripts/` or `tests/` parses `BACKLOG.md`, checks a spec-panel score, or enforces the DOD queue tail. `tests/` covers `nosignups_catalog` and `panel_propagation` only. [verified by agent, spot-checked]
3. **The DOD queue tail is dead.** `DOD.md:43-49` chains `/sc:analyze → /production-code-audit → /sc:cleanup → /sc:test → /commit-smart`. None of these resolve in `~/.claude/commands` or `~/.claude/skills`; the repo's own namespace is `/sh:`. `DOD.md` has 5 `sc:` references, `DOR.md` has 3. The replacements do resolve: `~/.claude/commands/sh/verify.md` and `~/.claude/commands/sh/finish.md` exist. [verified]
4. **Skill catalogue: 76 bundled, 18 are panels; 31 already promoted.** `.claude/skills/` holds 11 `agentflow-*` and 65 `sh-*` dirs (`ls .claude/skills | grep -cE '^(sh|agentflow)-'` → 76). The runtime `~/.claude/skills/` holds **31** `sh-*` dirs, not 2 as rev 1 claimed: 29 are also bundled (SKILL.md byte-identical 10, runtime newer 13, bundle newer 6: `sh-4-reviewer-panel`, `sh-content-panel`, `sh-devops-panel`, `sh-legal-panel`, `sh-marketing-panel`, `sh-visualization-panel`), 2 exist only in the runtime (`sh-claude-code-panel`, `sh-osm-panel`); 36 bundled `sh-*` and all 11 `agentflow-*` are not promoted. **There is no promotion tool.** `00_Governance/scripts/sync-global-skills.sh` copies RUNTIME → ARCHIVE (`~/.claude/skills` → `00_Governance/.claude/skills-global`, 31 `sh-*` archived) and its header forbids the reverse; rev 1 had the direction backwards. [verified: `comm`, `cmp`, `-nt`, script header lines 3–7]
5. **Two namespaces for the same gate, and they are command dirs, not skills.** `~/.claude/commands/sh` is a symlink to `20_agentflow/.claude/commands/global/sh` (47 commands). `~/.claude/commands/agentflow` is a real directory (11 commands: autopilot, code-review-gate, dod, dor, fipd, kickoff, loop, orchestrator, retro, triage, workflow), byte-identical to `global/agentflow`. The dagu DAG `~/.config/dagu/dags/skill-sync.yaml` rsyncs `~/.claude/commands` into 13 projects' `.claude/commands/global/` daily at 06:00 with `--delete`, so both namespaces exist as copies in `00_Governance`, `50_Excelbridge`, `75_Coaching`, `50_KETO`, `20_CONSIGLIERE` and eight more. **Consumers of `agentflow:*` by name:** 0 of 157 DAGs in `~/.config/dagu/dags`, 0 in `~/.hermes/hermes-adapter/dags` (positive control: `skill-sync.yaml` matches `sh:`); 3 files: `00_Governance/scripts/backlog_dor_pipeline.py:494` (`/agentflow:dor`), `20_agentflow/.claude/commands/global/goal.md:68,79` (`agentflow:dor`), `global/mission.md:145` (`agentflow:dod`). Observation log, 90 days: `agentflow:dor` invoked **105 times** (7th most-used skill overall); no other `agentflow:*` name appears. [verified]
6. **Doctrine duplicated in Governance, which won.** Agentflow `KNOWN_PATTERNS.md` is 114 lines, frozen April; Governance's is the maintained one (32k lines). Tenets (`~/.claude/TENETS.md`), NOT DONE line, `/mop`, `/lightsout`, evidence rule, log-decisions, session budget gate, handover stamp gate, deps registry: all live outside agentflow and postdate it. Exception: the **FIPD table** (Fix / Investigate / Plan / Decide, with the mandatory `Unknown:` clause) is defined only in agentflow `KNOWN_PATTERNS.md:9-17`; Governance's `KNOWN_PATTERNS.md` uses the term 10 times (e.g. KP-806) but never defines it. [verified]
7. **Stale clones everywhere — report done, nothing unique.** `40_convergence/agentflow`, `50_KETO/agentflow`, `MAC/agentflow`, `PY-Gen/agentflow` are checkouts of this repo frozen at the March "governance: sync" commits (`cordsjon/agentflow.git` = `cordsjon/20_agentflow.git`). The `40_convergence` clone's four items, checked 2026-09-26 against the live repo:

   | Item in clone | Disposition | Evidence |
   |---|---|---|
   | `601de58` "add Codex PR review workflow" (unpushed) | merged equivalent on `origin/master` | `.github/workflows/codex-review.yml` byte-identical to commit `c6a9d65` in 20_agentflow |
   | `33547b5` "sync public-readiness scoring dimension" (unpushed) | superseded | live `sh-spec-panel/SKILL.md` already has public-readiness; the 13 lines only in the clone version are the pre-rewrite skeleton |
   | uncommitted `KNOWN_PATTERNS.md` (+81/−27) | superseded | working tree byte-identical to live `KNOWN_PATTERNS.md` (commit `c90950c`) |
   | 3 untracked `docs/*-playground.html` | superseded | clone copies dated 2026-04-07, 62–65 KB; live copies 2026-04-30, 99–101 KB (commit `44f2b3c`) |

   | local refs beyond `master` | two tags | `v1.1.0` → d7e0a03 (same tag upstream); `v2.0.0` → 084ebb9 (same tag upstream) |
   | stashes / ignored files | none | `git stash list` → 0; `git status --ignored --porcelain` → 0 |

   Clone `origin/master` (`6c2b163`) is an ancestor of live `master`; `git log --branches --tags --not --remotes` lists exactly the two commits above. Deleting the clone still needs the operator (still-ask list). [verified]
8. **Stale content.** `AGENT_CAPABILITIES.md:113` "GPT-4 tier"; `ORIGIN.md` frames Superpowers/SuperClaude as merged-in when they are separate live skill trees; a 17 MB `.pptx` and a `.numbers` file in the repo root; `docs/*-playground.html` (April) unreferenced by anything. `skills-lock.json` is the `npx skills` lock for one third-party skill (`remotion-best-practices`), not an inventory of ours. [verified by agent, spot-checked]
9. **Still unique, worth keeping.** FIPD (finding 6); the two-speed DOR (Bug DOR-lite: root cause, 1–3-step fix plan, named regression test, no constraint violation, XS/S estimate, no US template and no panel score; Hotfix fast track: INBOX → `/triage` `[hotfix]` → TODO-Today, DOR-lite at triage time; `DOR.md:18-35`); `CLAUDE-LOOP.md`'s worked autopilot design (never implemented; dagu nightshift and `/loop` now cover the runtime). [inference on "unique": agent scanned Governance headers, not bodies]

## Design principles for v2

- **One source per rule.** [TENET: do-no-harm, repurpose-before-build] Rules live in Governance (`~/.claude/TENETS.md`, `00_Governance/KNOWN_PATTERNS.md`, `~/.claude/CLAUDE.md`). Agentflow keeps only what it executes. Where agentflow is today the only source (FIPD), the definition moves to Governance and agentflow links to it; nothing is kept in two hand-maintained copies.
- **A gate that nobody runs is documentation.** Every gate in v2 is either a script/hook with a positive control (a known-bad input it must refuse, exercised by a test), or it is deleted.
- **Skills are the product.** Agentflow becomes the skill pack ("Shepherd"), versioned, with an explicit promotion manifest. [TENET: mva]
- **Measure before consolidating.** 18 panels is past abstract-on-third; usage was measured (US-SH2-05, below) before any merge or retirement is proposed. [TENET: abstract-on-third]
- **Runtime is the direction of truth for already-promoted skills.** `sync-global-skills.sh` archives runtime → Governance; the skill-sync DAG copies runtime commands → projects. v2 must not introduce a bundle → runtime copy that overwrites the 13 runtime-newer skills.

## Scope — user stories

**US-SH2-01 — Doctrine collapse.** As the operator, I want `DOR.md`, `DOD.md`, `KNOWN_PATTERNS.md`, `GOVERNANCE-GUIDE.md` in agentflow replaced by one `DOCTRINE.md`, so that no rule exists twice.
- Final layout: `DOCTRINE.md` with four sections — *Sources* (links to the three Governance files), *DOR* (normal track: US + AC + spec-panel ≥ 7.0; Bug DOR-lite and Hotfix fast track verbatim from `DOR.md:18-35`), *DOD* (the new queue tail: `install_repo_hooks.py` v4 gates → `/sh:verify` → `/sh:finish` → deploy), *FIPD* (one line linking the Governance entry). The four old files are deleted, not kept as pointers.
- AC-1: after this story, `grep -rn "sc:" *.md .claude/skills` returns 0 hits (the 8 in `DOD.md`/`DOR.md` disappear with the files; the queue-tail rewrite is part of this story, not US-SH2-03).
- AC-2: the FIPD table and the `Unknown:` rule exist exactly once, as a new entry in `00_Governance/KNOWN_PATTERNS.md` (append via `kp_integrity.py` discipline); agentflow's `DOCTRINE.md` links to it; `grep -c '| \*\*Fix\*\* |' ~/projects/20_agentflow/*.md` returns 0.
- AC-3: `DOCTRINE.md` names no command that fails `ls ~/.claude/commands/sh/<name>.md`.

**US-SH2-02 — Executable DOR.** As an agent, I want `sh:dor` to run a script, so that "Ready" is checked, not asserted.
- Input contract: `scripts/dor_gate.py <BACKLOG.md> <story-id> [--track normal|bug-lite|hotfix] [--json]`. A story-id is `US-[A-Z0-9]+-[0-9]+`. Two title forms are recognised: a heading (`^#{2,4} ` containing the id) and a top-level list item (`^- \*\*…\*\*` containing the id). A heading entry ends at the next heading of equal or higher level; a list entry ends at the next top-level list item or any heading. The id counts as a match only in a title line, never in body text or cross-references. Two title matches → exit 2 (ambiguous), zero → exit 2 (not found).
- Evidence contract: the panel score is a line inside the entry of the form `spec-panel: <score> (<YYYY-MM-DD>, body:<12-hex>)` where `body:<12-hex>` is the first 12 hex digits of the SHA-256 of the spec file's text **above its first `## Duo review` or `## Codex review` heading** — the reviewed body. Appended review rounds and triage do not invalidate a score; any edit to the body does, committed or not. The gate recomputes the digest from the working tree and rejects a mismatch (exit 1, reason `stale-score`).
- Track policy: `normal` requires ≥1 US, ≥1 AC per US, and a valid score ≥ 7.0. `bug-lite` requires the five DOR-lite lines (root cause, fix plan ≤3 steps, regression test named, no constraint violation, estimate XS/S) and no score. `hotfix` requires the `[hotfix]` tag and the DOR-lite lines. Default track is read from the entry's tag (`[bug]` → bug-lite, `[hotfix]` → hotfix, else normal); `--track` overrides.
- AC-1: exit 0 on pass, 1 on fail with a one-line reason per failed requirement, 2 on ambiguous/not-found; `--json` emits `{story, track, pass, reasons[]}`.
- AC-2: `tests/test_dor_gate.py` with fixtures under `tests/fixtures/backlog_*.md`: one passing and one failing entry **per track** (six fixtures), plus one stale-score case (body edited after scoring, uncommitted), one ambiguous-id case, one section transition (a `###` story followed by a `##` section that must not be absorbed), one mixed-title-form file, and one body-text cross-reference to another story id that must not count. Red first, per `feedback_redgreen_verify_new_tests`.
- AC-3: `.claude/skills/sh-dor/SKILL.md` and `commands/global/sh/dor.md` invoke the script and quote its output; they no longer restate the checklist.
- Grep before define: check `00_Governance/scripts/` for an existing backlog parser first (`backlog_dor_pipeline.py`, `decisions_probe_queue`, `handover_stamp_gate` are the closest known). `backlog_dor_pipeline.py:494` currently calls `/agentflow:dor` as a prompt string; it must call the script after this story.

**US-SH2-03 — Executable DOD.** As an agent, I want the DOD to be the existing hook chain with proof it refuses, so that agentflow does not carry a second one.
- AC-1: `python3 ~/projects/00_Governance/scripts/install_repo_hooks.py --list ~/projects/20_agentflow` lists the v4 gates and `--doctor` reports them installed on this repo.
- AC-2: one failing control **per gate** the installer manages. `--list` on 2026-09-26: spec-hierarchy, verified-tag, reflex (warn-only), decisions-staleness (warn-only), repo-local `tools/precommit.d/*`, all pre-commit; commit-trailer (blocking) on commit-msg. There are no pre-push gates, so no push scenario is needed. Per-gate controls that already exist in Governance are cited by path, not re-written: `00_Governance/tests/test_install_repo_hooks_verified_tag.py`, `test_install_repo_hooks_reflex.py`, `test_install_repo_hooks_commit_msg.py`, `test_commit_trailer_gate.py`; spec-hierarchy and decisions-staleness get one each if none exists (check `00_Governance/tests/` first). This repo adds `tests/test_dod_chain.py` for the chain *as installed here*: scratch clone (fixture neutralises global `core.hooksPath`, per `feedback_scratch_git_repo_inherits_global_hookspath`), one violating commit per blocking gate rejected, each warn-only gate seen to emit its warning, one clean commit passes. `--doctor` on 2026-09-26 reports both hooks NOT INSTALLED on 20_agentflow; installing them is step 1 of this story.
- AC-3: `DOCTRINE.md`'s DOD section states which hook event each gate fires on (pre-commit vs. pre-push) and where `/sh:verify` and `/sh:finish` sit relative to them.

**US-SH2-04 — Skill pack with a promotion manifest.** As the operator, I want `SKILLS.md` plus `skills-manifest.json` to say for each bundled skill: `global` / `repo-local` / `retired`, so that sessions outside agentflow get the right set.
- Manifest schema: `{"version": 1, "skills": {"<dir-name>": {"status": "global|repo-local|retired", "since": "<YYYY-MM-DD>", "synced_sha256": "<SHA-256 of SKILL.md at the last outward copy; global entries only>"}}}`. `skills-lock.json` is untouched (third-party lock, finding 8).
- AC-1: every `.claude/skills/*` dir appears exactly once in the manifest; `scripts/skills_manifest.py check` exits 1 on a missing or duplicate entry (test with one of each). It runs in this repo's pre-commit chain (registered as a repo-local gate through `install_repo_hooks.py`, named in `DOCTRINE.md`'s DOD section) and is runnable by hand as `python3 scripts/skills_manifest.py check`; it gets no SKILL.md or `/sh:` command — a CI-only gate per *Terms*.
- AC-2: comparison is **scoped to manifest entries**: for each `global` entry, `~/.claude/skills/<name>/SKILL.md` exists and is byte-identical to the bundle; runtime dirs not in the manifest (`_panel-shared`, `sh-claude-code-panel`, `sh-osm-panel`, everything non-`sh-*`) are never touched or reported. Before the first sync, the 13 runtime-newer skills are copied runtime → bundle and the 6 bundle-newer ones get a per-skill decision logged in `DECISIONS.md`; only then may bundle → runtime copies run. Every later outward copy is guarded by `synced_sha256`: if the runtime `SKILL.md` digest differs from the recorded one, the copy is refused (exit 1, `runtime-diverged`) until reconciled. Test: a runtime edit made after a successful promote makes the next promote refuse.
- AC-4 (lifecycle): the manifest states are established by `scripts/skills_manifest.py check | promote <name> | retire <name>`. `promote` copies bundle → `~/.claude/skills/<name>` under the AC-2 guard and records `synced_sha256`. `retire` moves the bundle dir to `.claude/skills-retired/<name>` (outside Claude Code's scan path) and removes the runtime copy only under the same digest guard, otherwise refuses and names the divergence. `check` is AC-1 plus a digest-drift report. A decoy runtime dir not in the manifest survives every subcommand (test).
- AC-3 (depends on Decide-1 and finding 5's consumer list): `agentflow:*` retired by deleting 9 of the 11 files in `commands/global/agentflow/` and `~/.claude/commands/agentflow/` (0 invocations in 90 days); `dor.md` and `dod.md` stay as two-line aliases that invoke `/sh:dor` and `/sh:dod` until the three callers (`backlog_dor_pipeline.py:494`, `goal.md:68,79`, `mission.md:145`) are migrated in the same story, then they are deleted too. The skill-sync DAG propagates the deletions to the 13 project copies at the next 06:00 run (`--delete`); verify one project the day after.

**US-SH2-05 — Panel usage measurement (Investigate) — DONE 2026-09-26.**
- Source: `~/.local/state/claude-observations/<YYYY-MM-DD>.jsonl`, written by the PostToolUse hook `~/.claude/hooks/observation-logger.sh` (no matcher; self-filters on `tool_name`). Fields: `ts, sid, project (cwd basename), tool, summary ("invoked <name>"), file`.
- Coverage: 85 daily files, 2026-06-28 → 2026-09-26; 2,311 Skill invocations; 104 distinct `project` values, of which `tmp` (sessions started in `/private/tmp`, like this one) accounts for 1,131. So the log **does** cover non-`/private/tmp` sessions, but `tmp` sessions cannot be attributed to a project. Both invocation forms are captured (`sh:` 49, `sh-` 45 on panels). **Not verified:** whether Skill calls issued inside a subagent (e.g. `panel-executor`) fire the parent's PostToolUse hook; a zero below means "zero within verified coverage", not "never used".

  | Panel | Invocations | Distinct sessions | Where it lives |
  |---|---|---|---|
  | spec-panel | 69 | 66 | bundle + runtime |
  | ai-panel | 12 | 12 | bundle + runtime |
  | architecture-panel | 9 | 9 | bundle + runtime |
  | consigliere-panel | 2 | 2 | bundle + runtime |
  | test-panel | 1 | 1 | bundle + runtime |
  | osm-panel | 1 | 1 | runtime only |
  | 4-reviewer-panel, business-panel, content-panel, devops-panel, legal-panel, marketing-panel, mobile-panel, personal-development-panel, research-panel, security-panel, visualization-panel | 0 | 0 | bundle + runtime |
  | case1-panel, design-panel | 0 | 0 | bundle only |
  | claude-code-panel | 0 | 0 | runtime only |

- Reproduce: the count script is `scratchpad/panel_usage.py` of session `cfbfa4d9`; it is 40 lines of stdlib and should be re-run, not trusted, before any retirement.
- Outcome: 13 bundled panels have zero invocations in 90 days. They are retirement **candidates** (status `retired` in the US-SH2-04 manifest), decided per panel after the subagent-coverage question above is answered (Plan: one grep of the hook input for `agent_id`/parent session, ≤ 1 h).

**US-SH2-06 — Clone cleanup (Plan) — report done, delete pending.** The four frozen `agentflow/` checkouts are replaced by a one-line pointer file. The inventory for `40_convergence/agentflow` is in finding 7: every item has a merged equivalent or a newer superset on `origin/master`, so no archive is needed beyond the remote. Remaining steps: (1) operator approves deletion of `40_convergence/agentflow` (un-merged commits exist locally even though their content is upstream; still-ask list); (2) same inventory for `50_KETO`, `MAC`, `PY-Gen` before their deletion — expected trivial, they carry no local commits, but the check per clone is the same four-command inventory as finding 7 — `git log --branches --tags --not --remotes` (any local ref, not only `master`), `git for-each-ref refs/heads refs/tags`, `git stash list`, `git status --ignored --porcelain` — with a disposition row per non-empty result recorded here before the deletion ask.

**US-SH2-07 — Repo hygiene.** Move `Agentflow-Skills-in-Action-2.pptx` and the `.numbers` file out of git (Kingston backup per the large-file rule); delete `docs/*-playground.html`; fix `AGENT_CAPABILITIES.md:113`; rewrite `ORIGIN.md`'s framing in one paragraph.

## Decisions for the operator (Decide)

1. **Namespace: keep `sh:` and retire `agentflow:*`.** Recommendation unchanged: keep `sh:` (47 commands, 65 skills, README, GOVERNANCE-GUIDE); fewer renames. The rev-1 Unknown is resolved: no DAG or Hermes chain calls `agentflow:*`; the live consumers are `agentflow:dor` (105 invocations / 90 days, via `goal.md` and `backlog_dor_pipeline.py`) and `agentflow:dod` (`mission.md`), handled by the alias-then-migrate step in US-SH2-04 AC-3. What the operator decides: the direction, and whether the 9 unused `agentflow:*` commands are deleted outright or parked under `docs/archive/`.
2. Does `CLAUDE-LOOP.md` get archived as a design record, or deleted? Recommendation: archive under `docs/archive/` with a header pointing at dagu nightshift.
3. Does Shepherd stay a separate repo, or become `00_Governance/skills-pack/`? Recommendation: separate repo, because Governance already archives skills inward (`skills-global/`) and a second inward path would create a loop.

## Order and size

01 → 03 → 02 → 04 (each ≤ 1 day; 04 AC-3 waits for Decide-1) · 05 done (its Plan tail ≤ 1 h) · 07 anytime (≤ 2 h) · 06 delete step after Decide-1 and operator approval.

## Not in scope

Rewriting any panel's prose. Building a new orchestrator (`superpowers:dispatching-parallel-agents`, `sh:parallel`, the Workflow tool and dagu already cover routing). Touching the `experts/` and `dags/` directories, which are the live part. Changing the direction of `sync-global-skills.sh` or the skill-sync DAG.

## Duo review — pre-panel round 1

_Generated by review-duo at 2026-09-26T11:49:08Z. Phase artifacts: `/Users/jcords-macmini/projects/20_agentflow/docs/specs/2026-09-26-shepherd-v2-audit-design-duo-20260926-134750`_
_Two independent reviewers, shared context. Claude triages per-comment. No LLM-driven synthesis._

### DeepSeek findings

## Findings — DEEPSEEK  

### [CRITICAL] Missing referenced governance artifacts  
- **What:** The spec repeatedly cites files that do not exist in the repository: `00_Governance/TENETS.md`, `00_Governance/scripts/sync-global-skills.sh`, `00_Governance/scripts/install_repo_hooks.py`, `CLAUDE.md`, and the target `DOCTRINE.md` that the v2 design is supposed to create.  
- **Where:** Throughout the document (e.g., “One source per rule. … Rules live in Governance (`TENETS.md`, `KNOWN_PATTERNS.md`, `CLAUDE.md`).” – first paragraph of *Design principles*; US‑SH2‑01 “replace … by one `DOCTRINE.md`”; US‑SH2‑03 AC‑1 referencing `install_repo_hooks.py`; US‑SH2‑04 AC‑2 referencing `sync-global-skills.sh`).  
- **Why it matters:** Without these files the implementation plan cannot be executed; any automation that expects them will fail, and the “single source of truth” principle cannot be satisfied.  
- **Suggested fix:** Add the missing files to the repo (or correct the spec to point at the actual existing paths). If the files are intended to live in the `00_Governance` sub‑repo, either include them as a submodule or adjust the spec to reference the correct location. Explicitly list the expected path and a brief stub for each missing artifact.  
- **Confidence:** high  

### [CRITICAL] Acceptance criteria that contradict current state  
- **What:** US‑SH2‑01 AC‑1 requires `grep -rn "sc:" *.md .claude/skills` to return zero hits, yet the audit findings (point 3) state that `DOD.md` still contains five `sc:` references and `DOR.md` contains three.  
- **Where:** US‑SH2‑01 AC‑1 (under *Scope — user stories*); Audit finding 3 ( “The DOD queue tail is dead … `DOD.md:43-49` chains `/sc:…` …”).  
- **Why it matters:** The acceptance test is impossible to satisfy unless the spec first removes those `sc:` references, which is not described elsewhere. This creates a dead‑end for the implementation team.  
- **Suggested fix:** Either (a) update the acceptance criterion to reflect the intended post‑v2 state (e.g., “no `sc:` references remain after migration”) and add a story that removes them, or (b) amend the audit findings to note that those references will be eliminated as part of the v2 work.  
- **Confidence:** high  

### [CRITICAL] Undefined commands referenced in acceptance criteria  
- **What:** US‑SH2‑03 AC‑1 mentions `/sh:verify` and `/sh:finish` as required gates, but a search of `~/.claude/commands` and `~/.claude/skills` shows no such commands.  
- **Where:** US‑SH2‑03 AC‑1 ( “`install_repo_hooks.py` v4 gates + `/sh:verify` + `/sh:finish`”).  
- **Why it matters:** The DOD replacement cannot be validated without concrete command implementations; CI tests will fail and operators will have no runnable gate.  
- **Suggested fix:** Define and implement the two missing commands (or rename the acceptance criteria to use existing commands). Include their file locations in the spec.  
- **Confidence:** high  

### [IMPORTANT] Ambiguous decision about namespace migration  
- **What:** The “Decisions for the operator” section lists a recommendation to keep the `sh:` namespace but flags “Unknown: whether any dagu DAG or Hermes chain calls `agentflow:*` by name.” No plan is provided to discover or mitigate this risk.  
- **Where:** Decision 1 under *Decisions for the operator (Decide)*.  
- **Why it matters:** If any external workflow still references `agentflow:*`, retiring that namespace will break those pipelines, causing production outages.  
- **Suggested fix:** Add a concrete investigation step (e.g., grep all DAG definitions, CI configs, and deployment scripts for `agentflow:` prefixes) before the namespace migration, and record the result as a gating condition.  
- **Confidence:** medium  

### [IMPORTANT] Incomplete specification of skill‑promotion workflow  
- **What:** US‑SH2‑04 AC‑1 and AC‑2 require `skills-lock.json` regeneration and that `sync-global-skills.sh` produce a matching list, yet the spec does not define the format of `skills-lock.json`, the exact steps for regeneration, or how to verify the list equality.  
- **Where:** US‑SH2‑04 (user story) and the earlier audit finding 4 referencing `sync-global-skills.sh`.  
- **Why it matters:** Without a precise contract, developers may produce divergent lock files, leading to inconsistent skill sets across environments.  
- **Suggested fix:** Add a brief schema for `skills-lock.json` (e.g., list of skill IDs with status enum), and a verification command such as `diff <(cat skills-lock.json) <(sync-global-skills.sh --dry-run)`. Include these in the acceptance criteria.  
- **Confidence:** medium  

### [IMPORTANT] Unclear provenance of panel‑usage observation log  
- **What:** US‑SH2‑05 asks to count invocations from “the skill‑invocation observations the hooks already capture,” but the spec does not identify where that log is stored, its format, or whether it includes non‑`/private/tmp` sessions.  
- **Where:** US‑SH2‑05 (user story) – the “Unknown” note in the story description.  
- **Why it matters:** The measurement cannot be performed reliably, making the story impossible to complete and risking inaccurate panel retirement decisions.  
- **Suggested fix:** Document the exact log location (e.g., `~/.claude/logs/skill-invocations.jsonl`), its schema, and any filtering needed. If the log does not exist, add a task to create it before the measurement story.  
- **Confidence:** medium  

### [NIT] Inconsistent terminology for “gate” vs “command”  
- **What:** The spec sometimes calls a gate a “CLI/hook” (Design principle) and elsewhere a “command” (e.g., “No command is named that does not resolve in `~/.claude/commands`”). The mixed terminology could confuse implementers.  
- **Where:** Throughout *Design principles* and US‑SH2‑03 AC‑1.  
- **Why it matters:** Ambiguity may lead to duplicated implementations (one as a CLI, another as a skill) or missed validation steps.  
- **Suggested fix:** Choose a single term (e.g., “gate”) and define it early in the spec, then use it consistently.  
- **Confidence:** low  

### [NIT] Missing link to the “FIPD” definition  
- **What:** The spec mentions “FIPD with the mandatory `Unknown:` clause” but does not provide a reference or definition for “FIPD”.  
- **Where:** Audit finding 9 and US‑SH2‑01 AC‑2.  
- **Why it matters:** Readers unfamiliar with the acronym may not understand the requirement, leading to incomplete implementation.  
- **Suggested fix:** Add a brief definition or a link to the section in `KNOWN_PATTERNS.md` where FIPD is defined.  
- **Confidence:** low  

## Self‑flagged uncertainty  

- The exact location of the “skill‑invocation observations” log (US‑SH2‑05) is unknown; I assume it exists somewhere in `~/.claude/` based on prior patterns, but the repo may not contain it.  
- Whether any external CI pipelines already reference `agentflow:*` namespaces is not searchable from the provided bundle; I flagged it as an unknown risk but cannot confirm its presence.  
- The spec’s “measure before consolidating” principle references a “third” threshold; I am not certain what numeric value “abstract‑on‑third” maps to, but it does not affect the concrete findings above.  
### Codex findings

## Findings — CODEX

### [CRITICAL] Doctrine collapse removes a file that the next story must edit
- What: US-SH2-01 replaces `DOD.md`, but US-SH2-03 subsequently requires modifying its queue tail.
- Where: US-SH2-01, “replaced by one `DOCTRINE.md`”; US-SH2-03 AC-1, “`DOD.md` queue tail replaced”; Order, “01 → 03”.
- Why it matters: Following the stated order leaves US-SH2-03 without its target; recreating it would undo the doctrine collapse.
- Suggested fix: Define the final documentation layout explicitly and make US-SH2-03 target the surviving document. State whether old filenames are removed or retained as pointers.
- Confidence: high

### [IMPORTANT] FIPD has contradictory ownership and duplication requirements
- What: The spec simultaneously assigns FIPD to Governance, describes it as imported from Agentflow, and requires a verbatim copy in Agentflow.
- Where: “One source per rule”; US-SH2-01 AC-2, “carries the FIPD definitions and the `Unknown:` rule verbatim from there” and “Governance imports from agentflow, not the reverse”.
- Why it matters: Implementers cannot identify the authoritative copy or migration direction, and maintaining two handwritten copies recreates the drift being addressed.
- Suggested fix: Choose one authoritative FIPD location, require its contents to be established before removing existing definitions, and use a reference elsewhere. If duplication is necessary, specify generated copying and an equality check.
- Confidence: high

### [IMPORTANT] The executable DOR can block the fast track it must preserve
- What: The gate unconditionally requires user stories, acceptance criteria, and a panel score, without defining how Bug DOR-lite or hotfix exceptions work.
- Where: US-SH2-01 AC-3, “Bug DOR-lite / hotfix track survives”; US-SH2-02 AC-1, “exits 1 unless … a recorded spec-panel score ≥ 7.0”.
- Why it matters: The fast track may survive only as documentation while the executable gate rejects its intended users.
- Suggested fix: Specify normal, bug-lite, and hotfix eligibility and requirements, including whether each needs a panel score. Make the gate select the appropriate policy and test each path.
- Confidence: high

### [IMPORTANT] DOR lacks an input and evidence contract
- What: The gate’s acceptance criteria do not define entry boundaries, US-to-AC association, or which panel result belongs to the current specification.
- Where: US-SH2-02 AC-1, “`<BACKLOG.md> <story-id>`”, “≥1 AC per US”, and “a recorded spec-panel score”.
- Why it matters: Implementations can disagree about readiness, accidentally count neighboring entries, or accept a score earned before material specification changes.
- Suggested fix: Supply representative backlog fixtures and define story identifiers, entry boundaries, AC ownership, and the panel-result record, including a spec revision or content hash. Require rejection of ambiguous entries and mismatched evidence.
- Confidence: high

### [IMPORTANT] Hook installation is treated as proof of DOD enforcement
- What: The DOD story checks installed gates and command resolution without requiring evidence that the resulting chain blocks an invalid completion.
- Where: Design principles, “Every gate … with a positive control”; US-SH2-03 AC-2, “`--list` … shows the gates installed”.
- Why it matters: Installed hooks can be bypassed, misconfigured, or attached to the wrong event; resolving `/sh:verify` and `/sh:finish` does not demonstrate execution.
- Suggested fix: Identify the required gates and execution events, and reference existing controls or add a failing and passing completion scenario. Specify how `/sh:verify` and `/sh:finish` participate in that path.
- Confidence: high

### [IMPORTANT] The promotion check has no ownership boundary
- What: The spec compares the entire global skills directory with Agentflow’s promotion list despite acknowledging separate live skill trees.
- Where: US-SH2-04 AC-2, “`ls ~/.claude/skills` matches it”; Audit finding 8, “separate live skill trees”; Audit finding 4, promoted panels are “newer than the bundled copies”.
- Why it matters: Literal directory equality cannot accommodate unrelated skills and may encourage their removal. Applying stale bundled copies could also overwrite newer promoted panels.
- Suggested fix: Compare only Agentflow-owned installations recorded in a manifest, preserve unrelated entries, and define version reconciliation for already-promoted skills before syncing. Test preservation of unrelated skills and newer existing copies.
- Confidence: high

### [IMPORTANT] Namespace retirement lacks a consumer migration dependency
- What: Namespace duplicates must be retired even though external callers are unknown and possible DAG consumers are outside the allowed edit scope.
- Where: US-SH2-04 AC-3; Decide-1, “Unknown: whether any dagu DAG or Hermes chain calls `agentflow:*`”; Not in scope, “Touching … `dags/`”; Order places only US-SH2-06 explicitly after Decide-1.
- Why it matters: Removing an existing name can break unattended workflows, and discovering a caller leaves no defined migration path within scope.
- Suggested fix: Make US-SH2-04 depend on Decide-1 and a consumer inventory. Preserve compatibility aliases until callers migrate, or explicitly authorize the required consumer changes and validate them before removing names.
- Confidence: high

### [IMPORTANT] Clone cleanup does not require preservation of all unique work
- What: The cleanup precondition names only one of two unpushed commits and requires only a diff of the uncommitted restructure.
- Where: Audit finding 7, “two never-pushed commits (`33547b5`, `601de58`) and an uncommitted … restructure”; US-SH2-06, “cherry-pick or archive `601de58` … and diff”.
- Why it matters: Cherry-picking one commit need not preserve the other, and inspecting a diff does not preserve uncommitted work. The later deletion could therefore discard work despite satisfying the stated checks.
- Suggested fix: Require an inventory and durable disposition for both commits and all uncommitted changes. Before requesting deletion approval, verify a recoverable archive or merged equivalent and include its location in the report.
- Confidence: high

### [IMPORTANT] Zero observed invocations is not defined against coverage
- What: Panel retirement candidacy uses zero invocations while the observation log’s location and session coverage remain unknown.
- Where: US-SH2-05, “Panels with 0 invocations are candidates for retirement”; “Unknown: where the observation log is persisted and whether it covers non-`/private/tmp` sessions”.
- Why it matters: Missing telemetry can appear as non-use and influence the promotion or retirement inventory incorrectly.
- Suggested fix: Report observation dates, retention, session coverage, and alias normalization alongside counts. Distinguish “zero within verified coverage” from “unknown,” and make usage-based retirement decisions depend on completing this investigation.
- Confidence: high

**NIT:** (none)

## Self-flagged uncertainty

- The bundle omits the current backlog format, DOR checklist, and fast-track requirements. I can identify missing contracts but cannot determine the exact parser schema or exemption rules.
- Hook implementations, invocation events, positive controls, and promotion-tool behavior were not supplied. These may already provide safeguards; the spec should reference that evidence explicitly.
- The ancestry of the two unpushed commits is unknown. A suitable archive of `601de58` might preserve both, but the permitted cherry-pick option does not establish that.
- The collector’s `MISSING` results do not establish that cross-repository Governance paths are absent. I have not treated them as confirmed broken references.

### Triage — Claude, 2026-09-26 (round 1)

Every finding gets an applied edit (✅, where in rev 2) or an explicit ignore (❌, why). Grounding claims were re-checked against the filesystem before deciding.

**DeepSeek**

| # | Finding | Verdict | Disposition |
|---|---|---|---|
| D1 | CRITICAL — referenced governance artifacts missing | ⚠️ partly valid | `00_Governance/TENETS.md` does not exist; the file is `~/.claude/TENETS.md` — fixed in *Why*, principles, finding 6. The other four exist (`sync-global-skills.sh`, `install_repo_hooks.py`, `~/.claude/CLAUDE.md`, and `DOCTRINE.md` is the story's deliverable). Paths are now absolute. Ignored as CRITICAL: the collector's `MISSING` was scoped to this repo, as Codex's self-flag noted. |
| D2 | CRITICAL — AC-1 contradicts current state | ❌ ignored | An AC states the post-story state; the 8 `sc:` hits are what the story removes. Wording tightened to "after this story" so it cannot be misread. |
| D3 | CRITICAL — `/sh:verify`, `/sh:finish` undefined | ❌ ignored | Both resolve: `~/.claude/commands/sh/verify.md`, `~/.claude/commands/sh/finish.md` (verified `ls`). Finding 3 now names the paths; US-SH2-01 AC-3 makes resolution an AC. |
| D4 | IMPORTANT — namespace Unknown has no investigation step | ✅ applied | Investigation run this session: 0 hits in 157 dagu DAGs + hermes-adapter DAGs (positive control `skill-sync.yaml`), 3 caller files, 105 `agentflow:dor` invocations. Recorded in finding 5, Decide-1, US-SH2-04 AC-3. |
| D5 | IMPORTANT — `skills-lock.json` contract undefined | ✅ applied, differently | `skills-lock.json` is the `npx skills` lock for `remotion-best-practices` (finding 8); the spec no longer repurposes it. New `skills-manifest.json` with schema and a check script (US-SH2-04). |
| D6 | IMPORTANT — observation log provenance unknown | ✅ applied | Located, schema and coverage documented, measurement done (US-SH2-05). Suggested path `~/.claude/logs/skill-invocations.jsonl` was a guess; real path is `~/.local/state/claude-observations/`. |
| D7 | NIT — gate vs command terminology | ✅ applied | *Terms* paragraph added under *Why*. |
| D8 | NIT — FIPD undefined | ✅ applied | Expanded in finding 6 with the source lines. |

**Codex**

| # | Finding | Verdict | Disposition |
|---|---|---|---|
| C1 | CRITICAL — US-01 deletes `DOD.md`, US-03 then edits it | ✅ applied | Queue-tail rewrite folded into US-SH2-01 (final layout stated; old files deleted). US-SH2-03 is now only the executable half. Order 01 → 03 kept. |
| C2 | IMPORTANT — FIPD ownership contradictory | ✅ applied | One authoritative copy: a new Governance `KNOWN_PATTERNS.md` entry; agentflow links. Verified Governance uses the term 10× without defining it, so the move is a real gap fill, not duplication. US-SH2-01 AC-2 has the equality check (`grep -c` → 0 in agentflow). |
| C3 | IMPORTANT — executable DOR blocks the fast track | ✅ applied | `--track normal|bug-lite|hotfix`, tag-derived default, per-track requirements from `DOR.md:18-35`, fixtures per track (US-SH2-02). |
| C4 | IMPORTANT — DOR lacks input/evidence contract | ✅ applied | Story-id regex, entry boundary, ambiguity exit 2, score line format with spec sha, `stale-score` rejection, fixture list (US-SH2-02). |
| C5 | IMPORTANT — hook install ≠ enforcement | ✅ applied | US-SH2-03 AC-2: scratch-clone positive control (violating commit rejected, clean commit passes), AC-3 names hook events. |
| C6 | IMPORTANT — promotion check has no ownership boundary | ✅ applied | Manifest-scoped comparison, unrelated runtime dirs named and excluded, runtime-newer reconciliation before any outward copy, new design principle on direction of truth (US-SH2-04 AC-2). Also corrected the underlying grounding error: `sync-global-skills.sh` runs runtime → archive, and 31 skills are already promoted (finding 4). |
| C7 | IMPORTANT — namespace retirement lacks consumer dependency | ✅ applied | US-SH2-04 AC-3 depends on Decide-1 + the measured consumer list; `dor`/`dod` kept as aliases until the three callers migrate; DAG propagation step named. |
| C8 | IMPORTANT — clone cleanup may lose work | ✅ applied | Full inventory with per-item disposition and upstream location (finding 7); both unpushed commits and all uncommitted changes covered; deletion still gated on the operator. |
| C9 | IMPORTANT — zero invocations undefined against coverage | ✅ applied | Coverage window, record count, project attribution limit and the unverified subagent case stated; zeros labelled "within verified coverage"; retirement gated on closing that question (US-SH2-05). |

Not changed on either reviewer's request: the "Not in scope" list, the three Decide recommendations (Decide-1 now carries the resolved Unknown), the order 01 → 03 → 02 → 04.

## Duo review — post-panel round 2

_Generated by review-duo at 2026-09-26T12:00:26Z (Codex leg) — phase artifacts: `/Users/jcords-macmini/projects/20_agentflow/docs/specs/2026-09-26-shepherd-v2-audit-design-duo-20260926-140026`_
_DeepSeek leg FAILED: HTTP 503 from the api-router on the 48 KB prompt, three attempts (14:00, 14:05, 14:07); a one-line probe returned OK in 1.2 s, so the failure is size- or load-related upstream, not a router outage. Not diagnosed further this session; this round is Codex-only, which still meets the two-Codex-pass floor of `feedback_codex_spec_review_protocol`._

### DeepSeek findings

(none — leg failed, see above)

### Codex findings

## Findings — CODEX

**CRITICAL:** (none)

### [IMPORTANT] Score freshness ignores uncommitted specification changes
- What: The proposed revision check accepts an old panel score when the specification has changed without a new commit.
- Where: US-SH2-02, “`<spec-sha>` must equal `git log -1 --format=%h -- <spec path named in the entry>`”.
- Why it matters: Editing the specification leaves that command’s result unchanged, allowing materially changed requirements to pass using earlier review evidence.
- Suggested fix: Bind the score to a digest of the reviewed specification contents and compare it with the current file. Alternatively, require the recorded commit and reject staged, unstaged, or untracked changes to the specification. Add a fixture for edits made after scoring but before committing.
- Confidence: high

### [IMPORTANT] Entry boundaries can include unrelated backlog sections
- What: The parser contract does not terminate entries at higher-level headings or define how bold titles interact with Markdown heading levels.
- Where: US-SH2-02, “An entry spans from the heading or bold-title line that contains the id to the next line of the same level”.
- Why it matters: A story under `###` followed by a new `##` section can absorb unrelated content, potentially borrowing acceptance criteria or panel evidence from another entry.
- Suggested fix: Define supported title forms, terminate heading-based entries at the next heading of equal or higher level, and specify boundaries for bold-title entries. Define AC ownership and count identifier matches only in recognized entry titles. Add fixtures covering section transitions, mixed title forms, and references to other story IDs.
- Confidence: high

### [IMPORTANT] One rejected commit does not validate every DOD gate
- What: The acceptance test proves refusal by one gate, while the design principle requires a positive control for every gate.
- Where: Design principles, “Every gate in v2 … with a positive control”; US-SH2-03 AC-2, “a commit that violates one named v4 gate is rejected”.
- Why it matters: The test can pass while other gates are ineffective, and a commit-only scenario does not exercise gates attached to pre-push.
- Suggested fix: Identify the required gates and their hook events, then require a failing control for each gate, either through referenced existing tests or new controls. Exercise pre-push gates with a push to a disposable local remote, and retain passing controls.
- Confidence: high

### [IMPORTANT] Runtime reconciliation protects only the first promotion
- What: The spec requires reconciliation before the first sync but gives no conflict policy for subsequent runtime edits.
- Where: Design principles, “Runtime is the direction of truth for already-promoted skills”; US-SH2-04 AC-2, “Before the first sync … only then may bundle → runtime copies run”.
- Why it matters: A later bundle-to-runtime copy can overwrite new runtime work even though the initial migration satisfied every acceptance criterion.
- Suggested fix: Record the last synchronized content digest for each managed skill. Before every outward copy, detect runtime changes since that baseline and require reconciliation before overwriting them. Test a runtime edit made after a successful initial sync.
- Confidence: high

### [IMPORTANT] Manifest statuses lack an executable lifecycle
- What: The manifest labels skills as global, repo-local, or retired without defining the operations that establish those states.
- Where: Audit finding 4, “There is no promotion tool”; US-SH2-04, “`global` / `repo-local` / `retired`”; US-SH2-05, retirement candidates receive “status `retired`”.
- Why it matters: A checker can report missing global installations without installing them, and marking an installed skill retired can leave it discoverable and usable indefinitely.
- Suggested fix: Specify a promotion command or a concrete manual procedure, including installation, verification, and retirement behavior. Define whether retired skills move outside discovery directories and how previously managed runtime copies are removed or archived. Require that unrelated runtime skills remain untouched.
- Confidence: high

### [IMPORTANT] Remaining clone inventories omit potentially unique Git state
- What: The deletion checks cover commits on `master` and working-tree status but omit other branches, stashes, and ignored files.
- Where: US-SH2-06, “the check is `git log origin/master..master` + `git status --porcelain` per clone”.
- Why it matters: Both commands can report nothing to preserve while another local branch, a stash, or an ignored local artifact contains unique work that deletion would destroy.
- Suggested fix: Before requesting deletion approval, inventory all local branches and relevant refs against preserved upstream history, list stashes, and inspect ignored files. Record a durable disposition for anything unique, or create and verify an archive covering Git state and required local files.
- Confidence: high

**NIT:** (none)

## Self-flagged uncertainty

- The bundle omits representative backlog entries, so compatibility with the existing format cannot be assessed; the parser finding concerns the stated contract.
- Governance hook implementations and existing tests were not supplied. They may already provide the missing per-gate controls, but the spec does not identify them.
- No promotion implementation or complete skill-directory contents were supplied. Existing external tooling might provide lifecycle behavior, although the audit explicitly says no promotion tool exists.
- The bundle does not establish that the remaining clones contain other branches, stashes, or valuable ignored files. The finding concerns the completeness of the deletion preconditions, not confirmed data loss.

### Triage — Claude, 2026-09-26 (round 2)

| # | Finding | Verdict | Disposition |
|---|---|---|---|
| P1 | IMPORTANT — score freshness ignores uncommitted edits | ✅ applied | Score now binds to `body:<12-hex>` = SHA-256 of the spec text above the first review heading, recomputed from the working tree; stale-score fixture is an uncommitted body edit (US-SH2-02). |
| P2 | IMPORTANT — entry boundaries can absorb unrelated sections | ✅ applied | Two title forms defined; heading entries end at equal-or-higher heading, list entries at next top-level item or heading; id counts only in title lines; three new fixtures (US-SH2-02). |
| P3 | IMPORTANT — one rejected commit ≠ every gate | ✅ applied, narrowed | Per-gate control required; existing Governance tests cited by path for 4 of 6 gates. Verified `install_repo_hooks.py --list`: all gates are pre-commit or commit-msg, none pre-push, so the push scenario is dropped as inapplicable. `--doctor` shows the hooks are not yet installed here — made step 1 of US-SH2-03. |
| P4 | IMPORTANT — reconciliation protects only the first promotion | ✅ applied | `synced_sha256` per global entry; every outward copy refuses on runtime divergence; test named (US-SH2-04 AC-2). |
| P5 | IMPORTANT — manifest statuses lack a lifecycle | ✅ applied | `skills_manifest.py check\|promote\|retire` with digest guard, retired dirs moved outside the scan path, decoy-dir test (US-SH2-04 AC-4). |
| P6 | IMPORTANT — clone inventory omits branches/stashes/ignored | ✅ applied | Ran it for `40_convergence/agentflow`: 2 local tags both present upstream at the same commits, 0 stashes, 0 ignored files (finding 7); the four-command inventory is now the precondition for the other three clones (US-SH2-06). |

Body digest after this round: `body:5176cdbc81e4` (what the BACKLOG score line cites).

## Operator decisions — 2026-09-26

Recorded here, below the review rounds, so the body digest `5176cdbc81e4` and the 7.75 score stay valid. The "Decisions for the operator" section above keeps its original recommendations as written; where the operator chose differently, this section wins. Journal entries: `DECISIONS.md` Q5–Q8.

| Decide | Chosen | Matches recommendation | Entry |
|---|---|---|---|
| 1 — namespace | Keep `sh:`, retire `agentflow:*`, **delete** the 9 unused commands outright. `dor.md`/`dod.md` stay as two-line aliases until `backlog_dor_pipeline.py:494`, `goal.md:68,79`, `mission.md:145` migrate in US-SH2-04, then go too. | yes (delete, not park) | Q5; Q6 closes Q3 |
| 2 — `CLAUDE-LOOP.md` | **Delete outright.** Git history is the record. | **no** — spec recommended archive under `docs/archive/` | Q7 |
| 3 — repo placement | Shepherd stays a separate repo (`20_agentflow`). | yes | Q8 |

Consequences for the plan: US-SH2-07 deletes `CLAUDE-LOOP.md` instead of moving it (no `docs/archive/` entry needed for it); US-SH2-04 AC-3 is unblocked; US-SH2-06's delete step still needs a separate operator approval per the still-ask rule. Status: Ready.
