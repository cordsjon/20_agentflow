# Shepherd v2 — Audit and Doctrine Collapse Implementation Plan

> **For agentic workers:** REQUIRED: Use `/sh:execute` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collapse agentflow's four frozen doctrine files into one `DOCTRINE.md`, make DOR and DOD executable with positive controls, ship the skill pack with a promotion manifest, retire the `agentflow:` command namespace, and clean the repo — per spec `docs/specs/2026-09-26-shepherd-v2-audit-design.md` (rev 2, panel 7.75, body digest `5176cdbc81e4`) and the operator decisions Q5/Q7/Q8.

**Architecture:** Rules live in Governance; agentflow keeps only what it executes. Every gate is a stdlib Python script with a test that feeds it a known-bad input. Two new scripts: `scripts/dor_gate.py` (checks a BACKLOG entry, exit 0/1/2) and `scripts/skills_manifest.py` (`check | promote | retire | record`, digest-guarded). The DOD is the existing Governance hook chain installed into this repo plus one repo-local gate. The Governance DOR pipeline switches from an LLM checklist prompt to the script.

**Tech Stack:** Python 3.11 stdlib only, pytest via the Governance venv, git hooks from `00_Governance/scripts/install_repo_hooks.py` (v6), markdown.

---

## Read this before Task 1 — facts the spec got wrong or did not measure

Measured 2026-09-26 while writing this plan. Each changes a step below; each is written into the spec as an appended section in Task 1.0 (appended below the review rounds so the body digest and the 7.75 score stay valid).

| # | Spec / handover claim | Measured | Consequence |
|---|---|---|---|
| C1 | 65 bundled `sh-*` skills; 6 are "bundle-newer" (`sh-4-reviewer-panel`, `sh-content-panel`, `sh-devops-panel`, `sh-legal-panel`, `sh-marketing-panel`, `sh-visualization-panel`); 2 panels are "bundle only" (`case1`, `design`) | **20 of the 77 dirs under `.claude/skills/` are empty husks** (no `SKILL.md`, dated 2026-04-07, never git-tracked, `git ls-files` shows 56 SKILL.md files). Five of the six "bundle-newer" panels are husks: the runtime holds the only copy (75 lines each). Only `sh-4-reviewer-panel` is really bundle-newer (bundle 9789 B, 2026-06-26 vs runtime 6640 B, 2026-06-20; 155 diff lines). `sh-case1-panel` and `sh-design-panel` exist nowhere. Real bundled: 45 `sh-*`, 11 `agentflow-*`, 1 third-party (`remotion-best-practices`). | Chunk 4: delete the 20 husks first; adopt the 5 runtime-only panels into the bundle; exactly one per-skill decision (`sh-4-reviewer-panel`), not six; the US-SH2-05 table loses two phantom rows. The `-nt` comparison the handover used reports a missing file as "bundle-newer". |
| C2 | AC-1 of US-SH2-01: 8 `sc:` hits, all in `DOD.md`/`DOR.md` | `grep -rn "sc:" *.md .claude/skills` → **81 hits in 11 files**: `GOVERNANCE-GUIDE.md` 23, `SKILLS.md` 24, `CLAUDE-LOOP.md` 13, `DOD.md` 5, `ORCHESTRATOR.md` 4, `DOR.md` 3, `BACKLOG.md` 3, `agentflow-workflow` 4, `agentflow-triage` 1, `DECISIONS.md` 1 | Chunk 1 rewrites `SKILLS.md`, `ORCHESTRATOR.md`, the two skill files and two BACKLOG lines with the mapping in Task 1.4; the AC-1 test excludes `DECISIONS.md` only (append-only journal). |
| C3 | Governance `backlog_dor_pipeline.py:494` "must call the script after this story" | Governance `BACKLOG.md` has **39 Ready stories and 0 score lines** in the `spec-panel: <score> (<date>, body:<hex>)` form. The pipeline's own panel stage (E) runs *after* its DOR stage (C) and does not write a score line. | Chunk 3 gives `dor_gate.py` a `--skip-score` flag used only by the pipeline's stage C; the pipeline keeps producing the score at stage E. Without the flag every Governance story would fail C on `no-score`. |
| C4 | pytest runs with `python3` | Default `python3` (pyenv 3.11.15) has no pytest. The repo's tests run under the Governance venv: `~/projects/00_Governance/.venv/bin/python -m pytest tests -q` → `64 passed, 6 xfailed` at `98075d6`. | Every test step below uses that interpreter. |
| C5 | 20_agentflow's BACKLOG entry has a story id in its title | The Shepherd entry's title line carries **no `US-` id**; its seven stories live in the linked spec. Governance entries use `### US-ID: title` headings. | `dor_gate.py` accepts a title substring as the selector when the argument is not an id, and reads US/AC from the linked spec when the entry body has none (Task 3.1). |
| C6 | "`install_repo_hooks.py` v4 gates" | The installer is **v6**; `--list` on 2026-09-26: spec-hierarchy, verified-tag, reflex (warn), decisions-staleness (warn), repo-local `tools/precommit.d/*` — all pre-commit; commit-trailer (blocking) on commit-msg. The global `~/.config/git/hooks/` now chains **both** pre-commit and commit-msg (chainer added 2026-09-18). | `DOCTRINE.md` names the gates by the `--list` output, not a version. |
| C7 | `sync-global-skills.sh` in Governance is the only sync tool | This repo's `scripts/sync-skills-global.sh` is a **retired stub** (2026-06-26, exits 0 with a message). `~/.claude/commands/sh` is a symlink into this repo. | Chunk 4 deletes the stub (repo hygiene) and documents the symlink as the command-side "promotion". |

**Not measured, still open:** whether Skill calls inside a subagent fire the parent's PostToolUse hook (US-SH2-05 Plan tail, Task 5.4); the DeepSeek 503 cause.

## Conventions for every task

- **Repo:** `cd ~/projects/20_agentflow` (symlink to `~/projects-local/20_agentflow`; paths below are repo-relative unless absolute).
- **Tests:** `~/projects/00_Governance/.venv/bin/python -m pytest tests -q`. Governance tests: `cd ~/projects/00_Governance && .venv/bin/python -m pytest <file> -q` (its `pytest.ini` sets `pythonpath = scripts`).
- **Commits:** the global cc-guard blocks a bare `git commit`; always `git commit -F <msgfile> -- <paths>`. Every message ends with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the commit-msg gate installed in Chunk 2 enforces the `Claude <Family> <ver>` form). Write message files into the session scratchpad, not the repo.
- **Decisions:** every "log decision" step is one `~/projects/00_Governance/bin/decisions add 20_agentflow ... --apply` call (dry-run without `--apply`). Never edit an existing Q entry.
- **Spec body is frozen.** Anything added to `docs/specs/2026-09-26-shepherd-v2-audit-design.md` goes **after** the last line; re-run the digest command from the spec's Premises and confirm `5176cdbc81e4` after every spec edit.
- **Do not touch:** `experts/`, `dags/`, `skills-lock.json`, `~/.claude/skills/*` dirs not named in the manifest (`_panel-shared`, `_eval-runner`, `prompt-master`, `synced`, `sh-claude-code-panel`, `sh-osm-panel`, everything non-`sh-*`), the direction of `sync-global-skills.sh` or the skill-sync DAG, `20_agentflow/HANDOVER.md` (stale; leave).

---

## Chunk 1: US-SH2-01 — Doctrine collapse

### Task 1.0: Record the plan-time corrections in the spec (digest-preserving)

**Files:**
- Modify: `docs/specs/2026-09-26-shepherd-v2-audit-design.md` (append only)

- [ ] **Step 1: Append the corrections section**

Append to the end of the spec (after the "Operator decisions — 2026-09-26" section):

```markdown

## Plan-time corrections — 2026-09-26

Measured while writing `docs/plans/2026-09-26-shepherd-v2-audit.md`; the body above is left as reviewed. Where they disagree, this section wins.

1. **Finding 4 / handover measurement:** 20 of 77 `.claude/skills/*` dirs are empty husks (no `SKILL.md`, dated 2026-04-07, never tracked). Real bundle: 45 `sh-*`, 11 `agentflow-*`, 1 third-party. Of the six "bundle-newer" skills only `sh-4-reviewer-panel` is; `sh-content-panel`, `sh-devops-panel`, `sh-legal-panel`, `sh-marketing-panel`, `sh-visualization-panel` are runtime-only (bundle dir empty). `sh-case1-panel` and `sh-design-panel` exist in neither place — the two "bundle only" rows in the US-SH2-05 table are phantoms; 11 bundled panels are at 0, not 13.
2. **US-SH2-01 AC-1:** baseline is 81 `sc:` hits in 11 files, not 8 in 2. `DECISIONS.md` (append-only) is excluded from the check; every other file is fixed.
3. **US-SH2-02:** Governance `BACKLOG.md` has 39 Ready stories and 0 conforming score lines; the pipeline scores at stage E after its DOR stage C. `dor_gate.py` gets `--skip-score`, used only by the pipeline's stage C. The selector also accepts a title substring (20_agentflow's own entry title has no story id), and US/AC are read from the linked spec when the entry body has none.
4. **US-SH2-03 AC-1:** installer is v6 (not v4); the global hooks dir chains both pre-commit and commit-msg.
5. **Finding 4:** `scripts/sync-skills-global.sh` in this repo is a retired stub (2026-06-26); deleted under US-SH2-07.
```

- [ ] **Step 2: Verify the digest is unchanged**

Run: `python3 -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('docs/specs/2026-09-26-shepherd-v2-audit-design.md').read_text().split('\n## Duo review')[0].encode()).hexdigest()[:12])"`
Expected: `5176cdbc81e4`

- [ ] **Step 3: Commit**

```bash
git commit -F "$MSG" -- docs/specs/2026-09-26-shepherd-v2-audit-design.md
# msg: docs(specs): Shepherd v2 plan-time corrections (husks, sc: baseline, pipeline score stage)
```

### Task 1.1: Failing tests for the doctrine invariants

**Files:**
- Create: `tests/test_doctrine.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Doctrine invariants for Shepherd v2 (US-SH2-01).

AC-1: no `sc:` namespace reference survives outside the append-only journal.
AC-2: the FIPD table lives in Governance, not here.
AC-3: every /sh:<name> DOCTRINE.md names resolves to a command file.
The four old doctrine files are gone; DOCTRINE.md has the four sections.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SH_COMMANDS = Path.home() / ".claude" / "commands" / "sh"
JOURNALS = {"DECISIONS.md"}  # append-only; historical text is allowed to quote dead names


def _md_files():
    yield from (p for p in ROOT.glob("*.md") if p.name not in JOURNALS)
    yield from (ROOT / ".claude" / "skills").rglob("*.md")


def test_no_sc_namespace_references():
    hits = [f"{p.relative_to(ROOT)}:{i}" for p in _md_files()
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if "sc:" in line]
    assert hits == [], f"sc: references remain: {hits}"


def test_fipd_table_not_defined_here():
    hits = [p.name for p in ROOT.glob("*.md") if "| **Fix** |" in p.read_text(encoding="utf-8")]
    assert hits == [], f"FIPD table still defined in {hits}; it belongs in 00_Governance/KNOWN_PATTERNS.md"


def test_old_doctrine_files_deleted():
    present = [n for n in ("DOR.md", "DOD.md", "KNOWN_PATTERNS.md", "GOVERNANCE-GUIDE.md", "CLAUDE-LOOP.md")
               if (ROOT / n).exists()]
    assert present == [], f"still present: {present}"


def test_doctrine_has_four_sections():
    text = (ROOT / "DOCTRINE.md").read_text(encoding="utf-8")
    for heading in ("## Sources", "## DOR", "## DOD", "## FIPD"):
        assert heading in text, f"missing {heading}"


def test_every_sh_command_in_doctrine_resolves():
    text = (ROOT / "DOCTRINE.md").read_text(encoding="utf-8")
    names = sorted(set(re.findall(r"/sh:([a-z0-9-]+)", text)))
    assert names, "DOCTRINE.md names no /sh: command at all"
    missing = [n for n in names if not (SH_COMMANDS / f"{n}.md").exists()]
    assert missing == [], f"DOCTRINE.md names commands that do not exist: {missing}"
```

- [ ] **Step 2: Run to verify they fail**

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_doctrine.py -q`
Expected: 5 failed (`sc:` hits listed; `DOCTRINE.md` not found; old files present; KNOWN_PATTERNS.md has the table).

### Task 1.2: Move the FIPD table into Governance KNOWN_PATTERNS.md

**Files:**
- Modify: `~/projects/00_Governance/KNOWN_PATTERNS.md` (append via `kp_promote.py`, never by hand)

- [ ] **Step 1: Write the KP block to the scratchpad**

File `$SCRATCH/fipd-kp.md`:

```markdown
### KP-TBD: FIPD finding taxonomy — every finding is classified Fix / Investigate / Plan / Decide, and Investigate/Decide carry an `Unknown:` clause

**Action:** Fix | **Origin:** moved verbatim from 20_agentflow KNOWN_PATTERNS.md:9-17 + DOD.md:12 under US-SH2-01 (2026-09-26); Governance used the term 10× (e.g. KP-806) without defining it | **Rung:** training | **Lens:** fixed-value

Every pattern and finding is classified by **action type** — what the reader should do next:

| Action | Definition |
|--------|-----------|
| **Fix** | Root cause known, solution clear — implement immediately |
| **Investigate** | Symptom observed, root cause unknown — gather data before acting |
| **Plan** | Issue understood, solution direction known but requires design work — add to backlog |
| **Decide** | Trade-off identified, multiple valid directions exist — escalate to human decision-maker |

**Uncertainty rule:** an *Investigate* or *Decide* finding MUST include an `Unknown:` clause naming what is not known and how it would be measured. A finding without one is a *Fix* or a *Plan*, or it is not finished. Severity-only ratings (Low/Medium/High) never replace the action type; they may accompany it.
```

- [ ] **Step 2: Dry-run, then promote**

Run: `cd ~/projects/00_Governance && .venv/bin/python scripts/kp_promote.py --in "$SCRATCH/fipd-kp.md" --dry-run`
Expected: one block printed with the next free number (KP-4974 or higher).

Run: `cd ~/projects/00_Governance && .venv/bin/python scripts/kp_promote.py --in "$SCRATCH/fipd-kp.md" && python3 scripts/kp_integrity.py`
Expected: appended; integrity reports 0 collisions. Note the assigned number as `KP_FIPD` — it goes into `DOCTRINE.md`.

- [ ] **Step 3: Commit in Governance**

```bash
cd ~/projects/00_Governance && git commit -F "$MSG" -- KNOWN_PATTERNS.md
# msg: docs(kp): KP-<n> FIPD finding taxonomy, moved from 20_agentflow (US-SH2-01 AC-2)
```
(The Governance kp-rung-lens gate requires the `**Rung:** | **Lens:**` fields — they are in the block.)

### Task 1.3: Write DOCTRINE.md and delete the four files

**Files:**
- Create: `DOCTRINE.md`
- Delete: `DOR.md`, `DOD.md`, `KNOWN_PATTERNS.md`, `GOVERNANCE-GUIDE.md`, `CLAUDE-LOOP.md` (Q7: delete, not archive)

- [ ] **Step 1: Write `DOCTRINE.md`** (replace `KP_FIPD` with the number from Task 1.2)

```markdown
# Shepherd Doctrine

One file. Rules live in Governance; this repo keeps only what it executes. Replaced `DOR.md`, `DOD.md`, `KNOWN_PATTERNS.md`, `GOVERNANCE-GUIDE.md` and `CLAUDE-LOOP.md` on 2026-09-26 (spec `docs/specs/2026-09-26-shepherd-v2-audit-design.md`, US-SH2-01; DECISIONS.md Q5–Q9). Their history is in git; none is kept as a pointer.

## Sources

The operating rules for every governed project are, in precedence order:

1. `~/.claude/CLAUDE.md` — system-wide rules, workstyle, git operations.
2. `~/.claude/TENETS.md` — the ten tenets (`[TENET: …]` tags).
3. `~/projects/00_Governance/KNOWN_PATTERNS.md` — cross-project anti-patterns (KP-NNNN), including the FIPD taxonomy (KP-KP_FIPD).

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

**Queue tail** (replaces the dead `/sc:*` chain):

```
1. commit        — the hooks above run; a refusal is the DOD failing
2. /sh:verify    — evidence pass: tests green, claims backed by output (after the commit passes the hooks, before merge)
3. /sh:finish    — merge / PR / branch cleanup
4. deploy        — project-specific; smoke per the project's own rule
```

`/sh:dod` prints the machine-readable `DOD-VERDICT:` line that `quality_gate.run_stage1_dod` consumes; its contract lives in `~/.claude/commands/sh/dod.md`.

## FIPD

Every finding is classified Fix / Investigate / Plan / Decide; Investigate and Decide carry an `Unknown:` clause. Defined once, in Governance: `~/projects/00_Governance/KNOWN_PATTERNS.md` KP-KP_FIPD.
```

- [ ] **Step 2: Delete the five files**

Run: `git rm -q DOR.md DOD.md KNOWN_PATTERNS.md GOVERNANCE-GUIDE.md CLAUDE-LOOP.md`

- [ ] **Step 3: Run the doctrine tests**

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_doctrine.py -q`
Expected: `test_fipd_table_not_defined_here`, `test_old_doctrine_files_deleted`, `test_doctrine_has_four_sections`, `test_every_sh_command_in_doctrine_resolves` PASS; `test_no_sc_namespace_references` still FAILS (SKILLS.md, ORCHESTRATOR.md, skills, BACKLOG).

### Task 1.4: Retarget every surviving `sc:` reference and the dangling doctrine links

**Files:**
- Modify: `SKILLS.md` (24 lines), `ORCHESTRATOR.md` (lines 55, 78, 143, 150, 159, 166), `.claude/skills/agentflow-workflow/SKILL.md:46,48`, `.claude/skills/agentflow-workflow/queue-format.md:64,66`, `.claude/skills/agentflow-triage/SKILL.md:50`, `BACKLOG.md:286,291,345`, `README.md:63-72,139`, `docs/README.md:27`, `.claude/skills/agentflow-loop/claude-loop.md:3`

- [ ] **Step 1: Apply the namespace mapping** — a fixed table, then a check that each target exists:

| old | new | why |
|---|---|---|
| `/sc:brainstorm` | `/sh:brainstorm` | same skill |
| `/sc:spec-panel` | `/sh:spec-panel` | same skill |
| `/sc:workflow` | `/sh:workflow` | same skill |
| `/sc:analyze` | `/sh:analyze` | same skill |
| `/sc:test` | `/sh:test` | same skill |
| `/sc:design` | `/sh:plan` | the architecture step is the plan skill |
| `/sc:implement` | `/sh:execute` | execution skill |
| `/sc:cleanup` | `/sh:verify` | v2 DOD tail has no cleanup step; findings are checked at verify |
| `/sc:command "args"` (ORCHESTRATOR placeholder) | `/sh:<command> "args"` | placeholder |
| `/sc:` (bare, ORCHESTRATOR:55) | `/sh:` | prefix |

Run: `grep -rl 'sc:' SKILLS.md ORCHESTRATOR.md .claude/skills/agentflow-workflow .claude/skills/agentflow-triage BACKLOG.md | xargs sed -i '' -e 's#/sc:brainstorm#/sh:brainstorm#g; s#/sc:spec-panel#/sh:spec-panel#g; s#/sc:workflow#/sh:workflow#g; s#/sc:analyze#/sh:analyze#g; s#/sc:test#/sh:test#g; s#/sc:design#/sh:plan#g; s#/sc:implement#/sh:execute#g; s#/sc:cleanup#/sh:verify#g; s#/sc:command#/sh:<command>#g; s#`/sc:` command hint#`/sh:` command hint#g'`

Then reword `BACKLOG.md:291` by hand: `(`/sc:*`, `/commit-smart`)` → `(the retired \`sc\` namespace, \`/commit-smart\`)`.

Run: `grep -rn 'sc:' *.md .claude/skills | grep -v '^DECISIONS.md'`
Expected: no output.

Run: `for n in $(grep -rohE '/sh:[a-z0-9-]+' SKILLS.md ORCHESTRATOR.md .claude/skills/agentflow-workflow .claude/skills/agentflow-triage | sort -u | cut -d: -f2); do [ -f ~/.claude/commands/sh/$n.md ] || echo "MISSING $n"; done`
Expected: no output (all mapped targets exist among the 47 commands).

- [ ] **Step 2: Fix the links to deleted files**

- `README.md` Core Components table (lines 63–72): delete the `CLAUDE-LOOP.md`, `GOVERNANCE-GUIDE.md`, `DOD.md`, `DOR.md`, `KNOWN_PATTERNS.md` rows; insert as first row: `| [DOCTRINE.md](DOCTRINE.md) | Sources, DOR (executable), DOD (hook chain), FIPD pointer — the only doctrine file |`.
- `README.md:139`: `See governance/CLAUDE-LOOP.md for execution model.` → `See DOCTRINE.md (DOR/DOD) and ~/.config/dagu for the nightly loop.`
- `ORCHESTRATOR.md:143`: `` `KNOWN_PATTERNS.md` `` → `` `~/projects/00_Governance/KNOWN_PATTERNS.md` ``; `ORCHESTRATOR.md:150`: `CLAUDE-LOOP.md's Cleanup Sub-Loop` → `the former CLAUDE-LOOP.md's Cleanup Sub-Loop (deleted 2026-09-26, git history)`.
- `docs/README.md:27`: `(defined in \`CLAUDE-LOOP.md\`)` → `(historical; CLAUDE-LOOP.md was deleted 2026-09-26, see DOCTRINE.md)`.
- `.claude/skills/agentflow-loop/claude-loop.md:3`: `extracted from CLAUDE-LOOP.md.` → `extracted from CLAUDE-LOOP.md (deleted 2026-09-26; this file is the surviving copy).`

- [ ] **Step 3: Full suite**

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests -q`
Expected: `69 passed, 6 xfailed` (64 + 5 new).

- [ ] **Step 4: Log the decisions the spec did not settle**

```bash
D=~/projects/00_Governance/bin/decisions
$D add 20_agentflow --context shepherd-v2/US-SH2-01 --category deviation --decided-by agent --outcome assumed --apply \
  --question "AC-1 (0 sc: hits) is unsatisfiable literally: DECISIONS.md is append-only and quotes the dead names as history. Scope?" \
  --chosen "The AC-1 test excludes DECISIONS.md only; every other file (81 hits/11 files measured) is fixed. BACKLOG.md:291 reworded." \
  --justification "An append-only journal cannot be edited without breaking the schema gate; every living document is fixed." 
$D add 20_agentflow --context shepherd-v2/US-SH2-01 --category tradeoff --decided-by agent --outcome assumed --apply \
  --question "Which /sh: command replaces /sc:cleanup, /sc:design and /sc:implement, none of which has a same-named successor?" \
  --chosen "/sc:cleanup -> /sh:verify, /sc:design -> /sh:plan, /sc:implement -> /sh:execute (mapping table in the plan Task 1.4)." \
  --justification "The v2 DOD tail drops the cleanup step; verify is where findings are checked. Each target exists in ~/.claude/commands/sh (checked by loop)."
```

- [ ] **Step 5: Commit**

```bash
git commit -F "$MSG" -- DOCTRINE.md DOR.md DOD.md KNOWN_PATTERNS.md GOVERNANCE-GUIDE.md CLAUDE-LOOP.md SKILLS.md ORCHESTRATOR.md README.md docs/README.md .claude/skills/agentflow-workflow .claude/skills/agentflow-triage .claude/skills/agentflow-loop/claude-loop.md BACKLOG.md DECISIONS.md tests/test_doctrine.py
# msg: feat(doctrine): collapse DOR/DOD/KP/GOVERNANCE-GUIDE/CLAUDE-LOOP into DOCTRINE.md (US-SH2-01)
```

**Chunk 1 review:** AC-1, AC-2, AC-3 each have a test. The FIPD KP number is the one thing that crosses repos — it is in `DOCTRINE.md` twice; grep for `KP_FIPD` placeholder before committing. `[verified]` tags: after Chunk 2 installs the hooks, any later commit touching `*.md` with a bare `[verified]` is blocked; the spec is already committed, so only new edits are affected.

---

## Chunk 2: US-SH2-03 — Executable DOD

### Task 2.1: Install the hooks and prove `--doctor`

- [ ] **Step 1: Install**

Run: `python3 ~/projects/00_Governance/scripts/install_repo_hooks.py ~/projects/20_agentflow`
Expected: both hooks written to `.git/hooks/`.

- [ ] **Step 2: Doctor**

Run: `python3 ~/projects/00_Governance/scripts/install_repo_hooks.py --doctor ~/projects/20_agentflow; echo exit=$?`
Expected: `commit-msg: installed`/reachable and `pre-commit: installed`/reachable, `exit=0`. (Nothing to commit: `.git/hooks` is not tracked.)

### Task 2.2: Governance gets the one missing per-gate control (decisions-staleness)

`00_Governance/tests/` already covers verified-tag (`test_install_repo_hooks_verified_tag.py`, `test_verified_tag_gate.py`), reflex (`test_install_repo_hooks_reflex.py`, `test_reflex_gate.py`), commit-trailer (`test_install_repo_hooks_commit_msg.py`, `test_commit_trailer_gate.py`), spec-hierarchy (`test_spec_hierarchy_gate.py`). **None covers `decisions_staleness_precommit_gate.py`.**

**Files:**
- Create: `~/projects/00_Governance/tests/test_decisions_staleness_gate.py`

- [ ] **Step 1: Write the failing test** (clone of `test_spec_hierarchy_gate.py`'s fixture)

```python
"""Positive controls for decisions_staleness_precommit_gate.py (US-SH2-03 AC-2).

The gate is WARN-only: code is always 0. The control is the message — a
12-entry open queue must produce the queue-size warning, a 3-entry one must
produce only the count line. Without this test a gate that silently stopped
printing would look identical to a clean one.
"""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import decisions_staleness_precommit_gate as gate  # noqa: E402
from _git_helpers import harden_repo  # noqa: E402


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)


def _ledger(n: int) -> str:
    return "<!-- AI-maintained, append-only -->\n\n" + "".join(
        f"## Q{i} — t — tradeoff\n\n**Question:** q{i}\n**Chosen:** c\n**Decided-by:** agent\n"
        f"**Justification:** j\n**Outcome:** assumed\n\n" for i in range(1, n + 1))


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    harden_repo(tmp_path)
    return tmp_path


def _stage(repo, text):
    (repo / "DECISIONS.md").write_text(text)
    _git(repo, "add", "DECISIONS.md")


def test_long_open_queue_warns(repo):
    _stage(repo, _ledger(gate.OPEN_WARN))
    code, msgs = gate.check(repo)
    joined = "\n".join(msgs)
    assert code == 0, "gate must never block"
    assert f"{gate.OPEN_WARN} open of {gate.OPEN_WARN} logged" in joined
    assert "stops being read" in joined


def test_short_queue_prints_count_only(repo):
    _stage(repo, _ledger(3))
    code, msgs = gate.check(repo)
    joined = "\n".join(msgs)
    assert code == 0
    assert "3 open of 3 logged" in joined
    assert "stops being read" not in joined


def test_no_staged_ledger_says_so(repo):
    code, msgs = gate.check(repo)
    assert code == 0
    assert any("nothing to judge" in m for m in msgs)
```

- [ ] **Step 2: Run** — `cd ~/projects/00_Governance && .venv/bin/python -m pytest tests/test_decisions_staleness_gate.py -q`
Expected: 3 passed (the gate exists; this is a regression pin — if `test_long_open_queue_warns` fails, read `decisions_staleness_precommit_gate.py:120-145` for the exact warning text and adjust the substring, never the threshold).

- [ ] **Step 3: Prove it can fail** — temporarily change `OPEN_WARN` assertion to `gate.OPEN_WARN + 1` in the substring, run, see FAIL, revert. (`feedback_prove_the_test_can_fail`.)

- [ ] **Step 4: Commit in Governance**

```bash
cd ~/projects/00_Governance && git commit -F "$MSG" -- tests/test_decisions_staleness_gate.py
# msg: test(gates): positive controls for decisions-staleness gate (20_agentflow US-SH2-03 AC-2)
```

### Task 2.3: `tests/test_dod_chain.py` — the chain as installed here

**Files:**
- Create: `tests/test_dod_chain.py`

- [ ] **Step 1: Write the tests**

```python
"""The DOD is the installed hook chain. This proves each gate refuses its known-bad
input IN A SCRATCH CLONE with the same installer this repo uses (US-SH2-03 AC-2).

Per-gate unit controls live in 00_Governance/tests (verified-tag, reflex,
commit-trailer, spec-hierarchy, decisions-staleness). This file tests the CHAIN:
installer -> hook file -> gate script -> git refuses/warns.

Fixture neutralises the machine's global core.hooksPath (`-c core.hooksPath=.git/hooks`)
so the scratch repo's own hooks fire — feedback_scratch_git_repo_inherits_global_hookspath.
Requires: 00_Governance checked out at ~/projects/00_Governance, python3 on PATH.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

GOV = Path.home() / "projects" / "00_Governance"
INSTALLER = GOV / "scripts" / "install_repo_hooks.py"
TRAILER = "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
FOUR_EPICS = "# Capability: C\n## Solution: S\n" + "".join(
    f"### Epic: E{i}\n#### US-A-0{i}: u\n" for i in range(1, 5))

pytestmark = pytest.mark.skipif(not INSTALLER.exists(), reason="00_Governance not present")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=.git/hooks", *args],
                          capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def _commit(repo: Path, subject: str, *, trailer: bool = True) -> subprocess.CompletedProcess:
    msg = repo.parent / "msg.txt"
    msg.write_text(subject + ("\n\n" + TRAILER + "\n" if trailer else "\n"))
    return _git(repo, "commit", "-q", "-F", str(msg))


def _out(r: subprocess.CompletedProcess) -> str:
    return r.stdout + r.stderr


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "proj"
    r.mkdir()
    for a in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        assert _git(r, *a).returncode == 0
    inst = subprocess.run([sys.executable, str(INSTALLER), str(r)], capture_output=True, text=True)
    assert inst.returncode == 0, _out(inst)
    (r / "README.md").write_text("seed\n")
    _git(r, "add", "README.md")
    seed = _commit(r, "chore: seed")
    assert seed.returncode == 0, _out(seed)
    return r


def test_clean_commit_passes(repo):
    (repo / "ok.py").write_text("def f():\n    return 1\n")
    _git(repo, "add", "ok.py")
    r = _commit(repo, "feat: ok")
    assert r.returncode == 0, _out(r)


def test_verified_tag_gate_blocks(repo):
    (repo / "AUDIT.md").write_text("| W-9 | Investigate | x | no caller | `x.html` | [verified] |\n")
    _git(repo, "add", "AUDIT.md")
    r = _commit(repo, "docs: audit")
    assert r.returncode != 0, "bare [verified] tag was not blocked"
    assert "verified" in _out(r).lower()


def test_spec_hierarchy_gate_blocks(repo):
    p = repo / "docs" / "superpowers" / "specs" / "2026-01-01-bad-design.md"
    p.parent.mkdir(parents=True)
    p.write_text(FOUR_EPICS)
    _git(repo, "add", str(p.relative_to(repo)))
    r = _commit(repo, "docs: spec")
    assert r.returncode != 0, "four-epic spec was not blocked"
    assert "spec-hierarchy" in _out(r)


def test_commit_trailer_gate_blocks(repo):
    (repo / "b.py").write_text("x = 1\n")
    _git(repo, "add", "b.py")
    r = _commit(repo, "feat: no trailer", trailer=False)
    assert r.returncode != 0, "commit without the Co-Authored-By trailer was not blocked"
    assert "commit-trailer" in _out(r)


def test_reflex_gate_warns_but_passes(repo):
    (repo / "app.py").write_text("def f():\n    try:\n        pass\n    except Exception:\n        pass\n")
    _git(repo, "add", "app.py")
    r = _commit(repo, "feat: reflex")
    assert r.returncode == 0, _out(r)
    assert "[reflex]" in _out(r)


def test_decisions_staleness_gate_warns_but_passes(repo):
    ledger = "<!-- AI-maintained, append-only -->\n\n" + "".join(
        f"## Q{i} — t — tradeoff\n\n**Question:** q\n**Chosen:** c\n**Decided-by:** agent\n"
        f"**Justification:** j\n**Outcome:** assumed\n\n" for i in range(1, 13))
    (repo / "DECISIONS.md").write_text(ledger)
    _git(repo, "add", "DECISIONS.md")
    r = _commit(repo, "docs: decisions")
    assert r.returncode == 0, _out(r)
    assert "[decisions-staleness]" in _out(r)
    assert "12 open" in _out(r)


def test_repo_local_gate_runs(repo):
    d = repo / "tools" / "precommit.d"
    d.mkdir(parents=True)
    gate = d / "10-fail"
    gate.write_text("#!/usr/bin/env bash\necho local-gate-ran; exit 1\n")
    gate.chmod(0o755)
    (repo / "c.py").write_text("y = 2\n")
    _git(repo, "add", "c.py", "tools/precommit.d/10-fail")
    r = _commit(repo, "feat: local gate")
    assert r.returncode != 0
    assert "local-gate-ran" in _out(r)
```

- [ ] **Step 2: Run** — `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_dod_chain.py -q -x`
Expected: 7 passed. If `test_verified_tag_gate_blocks` passes the commit, the `verified_tag_precommit_gate.py` scope changed — read its header, do not weaken the assertion. If the seed commit fails on the decisions-schema gate: it is not in the v6 list, ignore; if it fails on `commit-trailer`, the TRAILER literal drifted from `commit_trailer_gate.py:70-73` — fix the literal.

- [ ] **Step 3: Full suite** — `~/projects/00_Governance/.venv/bin/python -m pytest tests -q` → `76 passed, 6 xfailed`.

- [ ] **Step 4: Commit** (the hooks now run on this commit — that is the point)

```bash
git commit -F "$MSG" -- tests/test_dod_chain.py
# msg: test(dod): hook chain refuses each known-bad input in a scratch clone (US-SH2-03)
```
Expected in output: `[pre-commit] reflex`, `[pre-commit] decisions-staleness`, `[commit-msg] commit-trailer`.

**Chunk 2 review:** AC-1 (install + doctor) is a manual step with quoted output, AC-2 is `test_dod_chain.py` + the cited Governance tests + the new staleness test, AC-3 is the DOD table already written in Task 1.3. The repo-local gate test uses a throwaway gate; the real `10-skills-manifest` gate arrives in Chunk 4.

---

## Chunk 3: US-SH2-02 — Executable DOR

### Task 3.1: `scripts/dor_gate.py`

**Files:**
- Create: `scripts/dor_gate.py`
- Create: `tests/test_dor_gate.py`, `tests/fixtures/backlog_*.md`, `tests/fixtures/spec_ok.md`

- [ ] **Step 1: Fixtures** — write these files under `tests/fixtures/`:

`spec_ok.md` (the linked spec; its body digest is computed in the test, so the content is free-form but must have a review heading):
```markdown
# Widget spec

## Scope
**US-W-01 — Widget.** As a user, I want a widget, so that things happen.
- AC-1: the widget renders.
- AC-2: the widget persists.

## Duo review — round 1
Reviewer notes appended after scoring.
```

`backlog_normal_pass.md` (`DIGEST` is replaced at test time with the real 12-hex of `spec_ok.md`'s body):
```markdown
# BACKLOG

## Ready

- **Widget — the epic** (ready 2026-09-26) `[feature]` · **M** — build the widget.
  - Spec: [spec](spec_ok.md)
  - spec-panel: 7.5 (2026-09-26, body:DIGEST)
```

`backlog_normal_fail.md` — same entry with the score `6.4` and no `Spec:` link line.

`backlog_buglite_pass.md`:
```markdown
## Refining

- **Crash on save** `[bug]` · **S**
  - Root cause: `app/save.py:41` writes before the lock is held.
  - Fix plan: (1) take the lock first, (2) add the assert.
  - Regression test: `tests/test_save.py::test_lock_before_write`.
  - No constraint violations.
  - Estimate: XS
```

`backlog_buglite_fail.md` — the same without the `Regression test` and `Estimate` lines.

`backlog_hotfix_pass.md` — the buglite-pass entry with tag `` `[hotfix]` `` instead of `` `[bug]` ``.
`backlog_hotfix_fail.md` — the hotfix entry missing the `Root cause` line.

`backlog_ambiguous.md` — two headings `### US-A-01: first` and `### US-A-01: second`.

`backlog_section_transition.md`:
```markdown
## Ready

### US-T-01: Titled story `[feature]`
**As a** user, **I want** x, **so that** y.
- AC-01: something checkable

## Critical Path
- AC-99: this line belongs to the section, not the story
```
(the story must end before `## Critical Path`; the gate must count 1 AC, not 2 — asserted via `--json`.)

`backlog_mixed.md` — one heading-form story `### US-M-01: heading form` with US/AC lines, and one list-form entry `- **List form** ... ` with `- Spec: [spec](spec_ok.md)` and a score line.

`backlog_crossref.md`:
```markdown
## Ready

### US-X-01: Real story
**As a** user, **I want** x, **so that** y.
- AC-01: fine

### US-X-02: Other story
**As a** user, **I want** z, **so that** w. Depends on US-X-01 landing first.
- AC-01: fine
```
(selecting `US-X-01` must match exactly one title; the body mention in US-X-02 must not count.)

- [ ] **Step 2: Failing tests**

```python
"""dor_gate.py — executable Definition of Ready (US-SH2-02 AC-1/AC-2).
One pass + one fail per track, stale score, ambiguous id, section transition,
mixed title forms, body cross-reference. Fixtures under tests/fixtures/backlog_*.md.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "dor_gate.py"
FIX = ROOT / "tests" / "fixtures"


def body_digest(spec: Path) -> str:
    text = spec.read_text(encoding="utf-8")
    for marker in ("\n## Duo review", "\n## Codex review"):
        if marker in text:
            text = text.split(marker)[0]
            break
    return hashlib.sha256(text.encode()).hexdigest()[:12]


@pytest.fixture
def work(tmp_path):
    """Copy fixtures into tmp_path and fill DIGEST so the score matches spec_ok.md."""
    for p in FIX.glob("*.md"):
        shutil.copy(p, tmp_path / p.name)
    d = body_digest(tmp_path / "spec_ok.md")
    for p in tmp_path.glob("backlog_*.md"):
        p.write_text(p.read_text().replace("DIGEST", d))
    return tmp_path


def run(backlog: Path, selector: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GATE), str(backlog), selector, "--json", *extra],
                          capture_output=True, text=True)


def verdict(r):
    return json.loads(r.stdout.splitlines()[0])


def test_normal_pass(work):
    r = run(work / "backlog_normal_pass.md", "Widget — the epic")
    assert r.returncode == 0, r.stdout + r.stderr
    v = verdict(r)
    assert v["pass"] is True and v["track"] == "normal" and v["reasons"] == []


def test_normal_fail_low_score_and_no_link(work):
    r = run(work / "backlog_normal_fail.md", "Widget — the epic")
    assert r.returncode == 1
    reasons = verdict(r)["reasons"]
    assert any(x.startswith("score-below-7.0") for x in reasons)
    assert "no-spec-link" in reasons


def test_stale_score_after_uncommitted_body_edit(work):
    spec = work / "spec_ok.md"
    spec.write_text(spec.read_text().replace("- AC-2: the widget persists.", "- AC-2: the widget persists forever."))
    r = run(work / "backlog_normal_pass.md", "Widget — the epic")
    assert r.returncode == 1
    assert "stale-score" in verdict(r)["reasons"]


def test_appending_a_review_round_keeps_score_valid(work):
    spec = work / "spec_ok.md"
    spec.write_text(spec.read_text() + "\n## Codex review — round 2\nmore notes\n")
    assert run(work / "backlog_normal_pass.md", "Widget — the epic").returncode == 0


def test_buglite_pass(work):
    r = run(work / "backlog_buglite_pass.md", "Crash on save")
    assert r.returncode == 0, r.stdout
    assert verdict(r)["track"] == "bug-lite"


def test_buglite_fail_names_each_missing_line(work):
    r = run(work / "backlog_buglite_fail.md", "Crash on save")
    assert r.returncode == 1
    reasons = verdict(r)["reasons"]
    assert "dor-lite-missing:regression-test" in reasons
    assert "dor-lite-missing:estimate" in reasons


def test_hotfix_pass(work):
    r = run(work / "backlog_hotfix_pass.md", "Crash on save")
    assert r.returncode == 0, r.stdout
    assert verdict(r)["track"] == "hotfix"


def test_hotfix_fail(work):
    r = run(work / "backlog_hotfix_fail.md", "Crash on save")
    assert r.returncode == 1
    assert "dor-lite-missing:root-cause" in verdict(r)["reasons"]


def test_track_override(work):
    r = run(work / "backlog_buglite_pass.md", "Crash on save", "--track", "normal")
    assert r.returncode == 1  # a bug entry judged as a feature has no US/score
    assert verdict(r)["track"] == "normal"


def test_ambiguous_id_exit_2(work):
    r = run(work / "backlog_ambiguous.md", "US-A-01")
    assert r.returncode == 2
    assert verdict(r)["reasons"] == ["ambiguous-id"]


def test_not_found_exit_2(work):
    r = run(work / "backlog_normal_pass.md", "US-NOPE-99")
    assert r.returncode == 2
    assert verdict(r)["reasons"] == ["not-found"]


def test_section_transition_not_absorbed(work):
    r = run(work / "backlog_section_transition.md", "US-T-01", "--skip-score")
    v = verdict(r)
    assert r.returncode == 0, r.stdout
    assert v["counts"]["ac"] == 1, "AC-99 under ## Critical Path was absorbed into the story"


def test_mixed_title_forms(work):
    assert run(work / "backlog_mixed.md", "US-M-01", "--skip-score").returncode == 0
    assert run(work / "backlog_mixed.md", "List form").returncode == 0


def test_body_crossref_does_not_count_as_title(work):
    r = run(work / "backlog_crossref.md", "US-X-01", "--skip-score")
    assert r.returncode == 0, r.stdout
    assert verdict(r)["story"] == "US-X-01"


def test_skip_score_only_skips_score(work):
    r = run(work / "backlog_normal_fail.md", "Widget — the epic", "--skip-score")
    assert r.returncode == 0, r.stdout  # low score ignored; US+AC come from... nothing → see below


def test_human_output_ends_with_verdict_line(work):
    r = subprocess.run([sys.executable, str(GATE), str(work / "backlog_buglite_fail.md"), "Crash on save"],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.rstrip().splitlines()[-1].startswith("DOR-VERDICT: FAIL: dor-lite-missing:")
```

Fix `test_skip_score_only_skips_score` before running: `backlog_normal_fail.md` has no spec link, so with the score skipped the entry still has no US/AC → expect `returncode == 1` and reasons `["no-user-story"]`. Write it that way.

- [ ] **Step 3: Run** — `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_dor_gate.py -q`
Expected: all FAIL (`scripts/dor_gate.py` missing).

- [ ] **Step 4: Implement `scripts/dor_gate.py`**

```python
#!/usr/bin/env python3
"""dor_gate.py — executable Definition of Ready (20_agentflow US-SH2-02).

    python3 scripts/dor_gate.py <BACKLOG.md> <story-id | title-substring>
                                [--track normal|bug-lite|hotfix] [--json] [--skip-score]

Exit 0 pass · 1 fail (one reason per line) · 2 not-found / ambiguous.
Human mode ends with `DOR-VERDICT: PASS` or `DOR-VERDICT: FAIL: <first reason>`.
`--json` prints {story, track, pass, reasons[], counts{us,ac}} as the first line.

Entry = a title line plus its body. Title forms: a heading `^#{2,4} ` or a
top-level list item `^- **…**`. A heading entry ends at the next heading of equal
or higher level; a list entry ends at the next top-level list item or any heading.
The selector matches TITLE LINES ONLY: an id (US-XXX-NN) as a whole word, or —
when the argument is not an id — a case-sensitive substring of the title text.

Score line (normal track): `spec-panel: <score> (<YYYY-MM-DD>, body:<12-hex>)`.
The digest is SHA-256 of the linked spec's text above its first `## Duo review`
or `## Codex review` heading, recomputed from the working tree; mismatch = stale-score.
The spec is the first `](…​.md)` link inside the entry, resolved from the BACKLOG's dir.
When the entry body has no user story but links a spec, US/AC are counted in the spec
(a multi-story spec's per-story coverage is what the panel score attests).

`--skip-score` exists for 00_Governance/scripts/backlog_dor_pipeline.py, whose panel
stage runs AFTER its DOR stage: structural checks only, the score is produced later.
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

ID_RE = re.compile(r"\bUS-[A-Z0-9]+-[0-9]+\b")
FULL_ID_RE = re.compile(r"^US-[A-Z0-9]+-[0-9]+$")
HEADING_RE = re.compile(r"^(#{2,4}) (.*)$")
LIST_TITLE_RE = re.compile(r"^- (?:~~)?\*\*(.+?)\*\*")
TOP_ITEM_RE = re.compile(r"^(?:- |\d+\. )")
TAG_RE = re.compile(r"`\[([^\]]+)\]`")
SCORE_RE = re.compile(r"spec-panel: (\d+(?:\.\d+)?) \((\d{4}-\d{2}-\d{2}), body:([0-9a-f]{12})\)")
LINK_RE = re.compile(r"\]\(([^)\s]+\.md)\)")
US_RE = re.compile(r"(^\s*(?:#{2,4} |\*\*|- \*\*)?US-[A-Z0-9]+-[0-9]+\b)|(\bAs an? \b.*\bI want\b)", re.IGNORECASE)
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
    """Split the file into entries by the two title forms."""
    out: list[Entry] = []
    i, n = 0, len(lines)
    while i < n:
        h = HEADING_RE.match(lines[i])
        l = LIST_TITLE_RE.match(lines[i])
        if not (h or l):
            i += 1
            continue
        start = i
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
            title = lines[i]
        out.append(Entry(title=title, lines=lines[start:j], start=start + 1))
        i = j if j > i else i + 1
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


def _count_us_ac(text: str) -> dict:
    lines = text.splitlines()
    us_idx = [i for i, ln in enumerate(lines) if US_RE.search(ln)]
    ac_idx = [i for i, ln in enumerate(lines) if AC_RE.match(ln)]
    return {"us": len(us_idx), "ac": len(ac_idx), "_us_idx": us_idx, "_ac_idx": ac_idx}


def _check_normal(entry: Entry, backlog: Path, res: Result, skip_score: bool) -> None:
    link = LINK_RE.search(entry.body)
    spec = (backlog.parent / link.group(1)).resolve() if link else None
    if spec is not None and not spec.exists():
        res.reasons.append(f"spec-missing:{link.group(1)}")
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
    if spec is None:
        res.reasons.append("no-spec-link")
        return
    if body_digest(spec.read_text(encoding="utf-8")) != m.group(3):
        res.reasons.append("stale-score")


def _check_lite(entry: Entry, res: Result, hotfix: bool) -> None:
    low = entry.body.lower()
    if hotfix and "`[hotfix]`" not in entry.lines[0]:
        res.reasons.append("missing-hotfix-tag")
    for suffix, phrase in LITE_LINES.items():
        if phrase not in low:
            res.reasons.append(f"dor-lite-missing:{suffix}")


def check(backlog: Path, selector: str, *, track: str | None, skip_score: bool) -> tuple[int, Result]:
    lines = backlog.read_text(encoding="utf-8").splitlines()
    entry, err = _select(_entries(lines), selector)
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
```

- [ ] **Step 5: Run** — `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_dor_gate.py -q`
Expected: 16 passed. Likely first-run failures and their fix: the `LIST_TITLE_RE` requires the title on the same line as `- **`; `US_RE` "As a … I want" must be on one line in fixtures (it is); `test_section_transition_not_absorbed` needs `--json` `counts.ac == 1` — the `###` entry ends at `## Critical Path` because level 2 ≤ 3.

- [ ] **Step 6: Run the gate on the live entry** (the first real use)

Run: `python3 scripts/dor_gate.py BACKLOG.md "Shepherd v2 — audit and doctrine collapse"`
Expected: `DOR-VERDICT: PASS` (US/AC read from the linked spec; digest `5176cdbc81e4` matches; score 7.75). If it prints `stale-score`, someone edited the spec body — stop and report, do not touch the score line.

- [ ] **Step 7: Commit**

```bash
git commit -F "$MSG" -- scripts/dor_gate.py tests/test_dor_gate.py tests/fixtures/backlog_*.md tests/fixtures/spec_ok.md
# msg: feat(dor): executable DOR gate with per-track fixtures and body-digest score check (US-SH2-02)
```

### Task 3.2: `/sh:dor` invokes the script

**Files:**
- Modify: `.claude/skills/sh-dor/SKILL.md`, `.claude/commands/global/sh/dor.md` (identical content; the command is what `/sh:dor` resolves to via the `~/.claude/commands/sh` symlink)

- [ ] **Step 1: Replace both files' body** (keep the frontmatter, update the description):

```markdown
---
name: sh-dor
description: Run the executable Definition of Ready gate (scripts/dor_gate.py in 20_agentflow) against one BACKLOG entry and quote its verdict. Use before an item moves from Refining to Ready or into a queue.
---

# /sh:dor — Definition of Ready (executable)

The checklist is not restated here; the script is the rule (`~/projects/20_agentflow/DOCTRINE.md` § DOR).

1. Resolve the BACKLOG file (`$ARGUMENTS` may name it; default `./BACKLOG.md`) and the entry: a story id `US-XXX-NN` or a title substring.
2. Run, verbatim, and paste the whole output:
   ```bash
   python3 ~/projects/20_agentflow/scripts/dor_gate.py <BACKLOG.md> "<id-or-title>"
   ```
3. Exit 0 → the entry may move to Ready / a queue. Exit 1 → quote each `FAIL <reason>` line and stop; fix the entry (or run `/sh:spec-panel` if the reason is `no-score`/`score-below-7.0`/`stale-score`), never edit the score line by hand. Exit 2 → `not-found` or `ambiguous-id`: name the entry more precisely.
4. The FINAL line of your reply is the script's own `DOR-VERDICT:` line, unchanged. Consumers (`/goal`, `backlog_dor_pipeline.py`) parse it.

Tracks are read from the entry's tag (`[bug]` → bug-lite, `[hotfix]` → hotfix); `--track` overrides; `--json` for machines.
```

- [ ] **Step 2: Verify** — `diff .claude/skills/sh-dor/SKILL.md .claude/commands/global/sh/dor.md && grep -c 'dor_gate.py' ~/.claude/commands/sh/dor.md`
Expected: no diff, `1` (the symlink serves the new file live).

- [ ] **Step 3: Commit**

```bash
git commit -F "$MSG" -- .claude/skills/sh-dor/SKILL.md .claude/commands/global/sh/dor.md
# msg: feat(sh-dor): invoke scripts/dor_gate.py instead of restating the checklist (US-SH2-02 AC-3)
```

### Task 3.3: Governance pipeline stage C calls the script

**Files:**
- Modify: `~/projects/00_Governance/scripts/backlog_dor_pipeline.py:487-527` (`_DOR_PROMPT`, `run_stage_c_dor`) and the call at `:1019`
- Modify: `~/projects/00_Governance/tests/test_backlog_dor_pipeline_tooling.py` (stage-C cases)
- Create: `~/projects/00_Governance/tests/test_backlog_dor_pipeline_stage_c_script.py`

- [ ] **Step 1: Failing test** (real seam: a real script path, a real BACKLOG file, a child process)

```python
"""Stage C of the DOR pipeline runs 20_agentflow/scripts/dor_gate.py, not an LLM
checklist prompt (20_agentflow US-SH2-02). Real child process, real file."""
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import backlog_dor_pipeline as bdp  # noqa: E402

GATE = Path.home() / "projects" / "20_agentflow" / "scripts" / "dor_gate.py"

STORY_OK = ("## Ready\n\n### US-P-01: Story\n**As a** u, **I want** x, **so that** y.\n"
            "- [ ] AC-01: checkable\n\n**Priority:** P2 · **State:** Refining\n")
STORY_NO_AC = ("## Ready\n\n### US-P-02: Story\n**As a** u, **I want** x, **so that** y.\n\n"
               "**Priority:** P2 · **State:** Refining\n")


def _story(text, sid):
    blocks = bdp.parse_ready_blocks(text)
    return next(b for b in blocks if b.id == sid)


def test_stage_c_passes_structurally_sound_story(tmp_path, monkeypatch):
    monkeypatch.setenv("DOR_GATE_SCRIPT", str(GATE))
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_OK)
    r = bdp.run_stage_c_dor(backlog, _story(STORY_OK, "US-P-01"), dry_run=False)
    assert r.passed, r.__dict__


def test_stage_c_fails_story_without_ac_with_script_reason(tmp_path, monkeypatch):
    monkeypatch.setenv("DOR_GATE_SCRIPT", str(GATE))
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_NO_AC)
    r = bdp.run_stage_c_dor(backlog, _story(STORY_NO_AC, "US-P-02"), dry_run=False)
    assert not r.passed
    assert r.veto_reason == "no-acceptance-criteria"


def test_stage_c_missing_script_is_tooling_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("DOR_GATE_SCRIPT", str(tmp_path / "nope.py"))
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_OK)
    r = bdp.run_stage_c_dor(backlog, _story(STORY_OK, "US-P-01"), dry_run=False)
    assert not r.passed
    assert r.veto_reason == "tooling_unavailable"


def test_stage_c_does_not_require_a_score(tmp_path, monkeypatch):
    """The pipeline scores at stage E; stage C must not fail 39 Governance stories on no-score."""
    monkeypatch.setenv("DOR_GATE_SCRIPT", str(GATE))
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_OK)
    r = bdp.run_stage_c_dor(backlog, _story(STORY_OK, "US-P-01"), dry_run=False)
    assert r.passed
```

Run: `cd ~/projects/00_Governance && .venv/bin/python -m pytest tests/test_backlog_dor_pipeline_stage_c_script.py -q` → FAIL (`run_stage_c_dor` has the old signature).

- [ ] **Step 2: Implement** — replace lines 487–527 of `backlog_dor_pipeline.py`:

```python
# --- Stage C: DOR check --------------------------------------------------------
# AC-03 (rewritten 2026-09-26, 20_agentflow US-SH2-02): the DOR is a SCRIPT, not a
# checklist prompt. 20_agentflow/scripts/dor_gate.py judges the story block in the
# real BACKLOG file: US present, >=1 AC per US, track from tags. --skip-score because
# THIS pipeline produces the panel score at stage E, after C; without it every
# Governance Ready story (39 on 2026-09-26, 0 score lines) would fail here on no-score.
# The verdict is the exit code + JSON, so there is no dor_no_verdict path any more;
# a missing script is tooling_unavailable (fail-closed, never a judgement).

DOR_GATE_SCRIPT_DEFAULT = Path.home() / "projects" / "20_agentflow" / "scripts" / "dor_gate.py"


def _dor_gate_script() -> Path:
    return Path(os.environ.get("DOR_GATE_SCRIPT", str(DOR_GATE_SCRIPT_DEFAULT))).expanduser()


def run_stage_c_dor(backlog: Path, story: StoryBlock, *, dry_run: bool) -> StageResult:
    if dry_run:
        return StageResult("dor", True, detail="dry-run: would run dor_gate.py --skip-score")
    script = _dor_gate_script()
    if not script.exists():
        return StageResult("dor", False, "tooling_unavailable", f"missing {script}")
    cmd = [sys.executable, str(script), str(backlog), story.id, "--json", "--skip-score"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=STAGE_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        return StageResult("dor", False, "gate_timeout")
    if proc.returncode == 2:
        return StageResult("dor", False, "dor_tooling_failed", f"exit 2: {proc.stdout.strip()[-300:]}")
    try:
        verdict = json.loads(proc.stdout.splitlines()[0])
    except (IndexError, json.JSONDecodeError):
        return StageResult("dor", False, "dor_tooling_failed", f"unparseable: {proc.stdout[-300:]!r}")
    if verdict.get("pass"):
        return StageResult("dor", True, detail=f"track={verdict.get('track')}")
    reasons = verdict.get("reasons") or ["dor_veto"]
    return StageResult("dor", False, reasons[0], "; ".join(reasons))
```

Delete `_DOR_VERDICT_RE`, `_DOR_PROMPT` and `parse_dor_verdict` **only after** grepping: `grep -rn 'parse_dor_verdict\|_DOR_PROMPT\|_DOR_VERDICT_RE' scripts tests` — every hit outside this block is a test that must be rewritten to the new seam (Step 3). Change the call at `:1019` to `c = run_stage_c_dor(backlog, story, dry_run=dry_run)`. Ensure `import os` and `import sys` exist at the top (they do — `select_backend` uses `os.environ`).

- [ ] **Step 3: Adapt the old stage-C tests** — in `tests/test_backlog_dor_pipeline_tooling.py`, any test that removes `claude` from PATH and asserts `tooling_unavailable` from stage C now sets `DOR_GATE_SCRIPT` to a nonexistent path instead (the PATH seam still applies to stages E/F/H — leave those). Any test importing `parse_dor_verdict` is deleted with a one-line comment naming this plan.

- [ ] **Step 4: Run the pipeline suite** — `cd ~/projects/00_Governance && .venv/bin/python -m pytest tests/test_backlog_dor_pipeline_*.py -q`
Expected: all green; the 4 new tests included.

- [ ] **Step 5: Dry-run the real pipeline** — `cd ~/projects/00_Governance && .venv/bin/python scripts/backlog_dor_pipeline.py --dry-run --max-stories 1 2>&1 | tail -5` (check `--help` for the exact flags first). Expected: stage C detail `dry-run: would run dor_gate.py --skip-score`.

- [ ] **Step 6: Log + commit in Governance**

```bash
~/projects/00_Governance/bin/decisions add 00_Governance --context backlog-dor-pipeline/stage-c --category deviation --decided-by agent --outcome assumed --apply \
  --question "Stage C now calls 20_agentflow/scripts/dor_gate.py; how does it locate a script in another repo, and what about the score the script requires?" \
  --chosen "Path from env DOR_GATE_SCRIPT, default ~/projects/20_agentflow/scripts/dor_gate.py; missing -> tooling_unavailable. Called with --skip-score because stage E produces the score afterwards." \
  --justification "Governance BACKLOG had 39 Ready stories and 0 conforming score lines on 2026-09-26; without --skip-score stage C would fail all of them. Reversible: drop the flag once stage E writes score lines."
cd ~/projects/00_Governance && git commit -F "$MSG" -- scripts/backlog_dor_pipeline.py tests/test_backlog_dor_pipeline_tooling.py tests/test_backlog_dor_pipeline_stage_c_script.py DECISIONS.md
# msg: feat(dor-pipeline): stage C runs 20_agentflow dor_gate.py instead of a checklist prompt
```

**Chunk 3 review:** the score-at-stage-C tension (C3) is resolved by a flag and logged, not hidden. `test_stage_c_*` hits the real script across repos — if 20_agentflow is not checked out the tests fail loudly, which is the honest state for a cross-repo dependency. The `us-without-ac` per-US rule applies only when the entry body itself holds the stories.

---

## Chunk 4: US-SH2-04 — Skill pack with a promotion manifest, `agentflow:` retired

### Task 4.1: Remove the 20 husks, adopt the runtime truth into the bundle

**Files:**
- Delete (untracked dirs): the 20 empty `.claude/skills/*` dirs
- Modify (copy runtime → bundle): 13 runtime-newer + 5 runtime-only panels

- [ ] **Step 1: Delete husks** (untracked, so no git change):

```bash
for d in .claude/skills/*/; do [ -f "$d/SKILL.md" ] || rmdir "$d"; done; ls .claude/skills | wc -l
```
Expected: `57`.

- [ ] **Step 2: Copy runtime → bundle for the 18 where runtime is the truth**

```bash
for n in sh-ai-panel sh-architecture-panel sh-business-analysis sh-business-panel sh-consigliere-panel sh-estimate sh-mobile-panel sh-personal-development-panel sh-research-panel sh-security-panel sh-spec-panel sh-test-panel sh-ux-design \
         sh-content-panel sh-devops-panel sh-legal-panel sh-marketing-panel sh-visualization-panel; do
  rm -rf ".claude/skills/$n" && cp -R "$HOME/.claude/skills/$n" ".claude/skills/$n"; done
git status --porcelain .claude/skills | wc -l
```
Expected: 18 dirs now byte-identical to runtime (`for n in …; do cmp -s .claude/skills/$n/SKILL.md ~/.claude/skills/$n/SKILL.md || echo DIFF $n; done` → no output). Note: `cp -R` copies any sibling files the runtime dir holds (references, scripts) — that is intended; the pack is the whole dir.

- [ ] **Step 3: The one real bundle-newer skill: `sh-4-reviewer-panel`**

Run: `diff ~/.claude/skills/sh-4-reviewer-panel/SKILL.md .claude/skills/sh-4-reviewer-panel/SKILL.md | head -80` and read it. Decide: if the bundle's extra 3 KB is authored content the runtime lacks (not a stale skeleton), promote bundle → runtime **in Task 4.3 via `promote`**; else copy runtime → bundle like the others. Log either way:

```bash
~/projects/00_Governance/bin/decisions add 20_agentflow --context shepherd-v2/US-SH2-04 --category tradeoff --decided-by agent --outcome assumed --apply \
  --question "sh-4-reviewer-panel: bundle (2026-06-26, 9789 B) is newer than runtime (2026-06-20, 6640 B) — which copy is truth?" \
  --chosen "<bundle wins: promote after the manifest exists | runtime wins: copied runtime -> bundle>" \
  --justification "<what the 155-line diff contains>"
```

- [ ] **Step 4: Commit the adoption**

```bash
git add .claude/skills && git commit -F "$MSG" -- .claude/skills DECISIONS.md
# msg: chore(skills): adopt runtime copies of 18 sh-* skills into the bundle; 20 empty husk dirs removed (US-SH2-04 AC-2 precondition)
```

### Task 4.2: `scripts/skills_manifest.py` + manifest + tests

**Files:**
- Create: `scripts/skills_manifest.py`, `skills-manifest.json`, `tests/test_skills_manifest.py`, `tools/precommit.d/10-skills-manifest`

- [ ] **Step 1: Failing tests**

```python
"""skills_manifest.py — check | promote | retire | record (US-SH2-04 AC-1/2/4).
Everything runs against tmp dirs passed via --skills-dir/--runtime-dir/--manifest,
so the machine's ~/.claude/skills is never touched by the tests."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "scripts" / "skills_manifest.py"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mk_skill(root: Path, name: str, text: str = "# skill\n") -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(text)
    return d


@pytest.fixture
def env(tmp_path):
    skills, runtime, retired = tmp_path / "skills", tmp_path / "runtime", tmp_path / "retired"
    skills.mkdir(); runtime.mkdir()
    manifest = tmp_path / "skills-manifest.json"
    mk_skill(skills, "sh-a"); mk_skill(skills, "sh-b")
    mk_skill(runtime, "sh-a")  # already promoted, identical
    mk_skill(runtime, "_decoy", "# not ours\n")  # never in the manifest
    manifest.write_text(json.dumps({"version": 1, "skills": {
        "sh-a": {"status": "global", "since": "2026-09-26", "synced_sha256": sha(skills / "sh-a" / "SKILL.md")},
        "sh-b": {"status": "repo-local", "since": "2026-09-26"},
    }}, indent=2))
    return {"skills": skills, "runtime": runtime, "retired": retired, "manifest": manifest}


def run(env, *args):
    return subprocess.run([sys.executable, str(TOOL), "--skills-dir", str(env["skills"]),
                          "--runtime-dir", str(env["runtime"]), "--retired-dir", str(env["retired"]),
                          "--manifest", str(env["manifest"]), *args], capture_output=True, text=True)


def load(env):
    return json.loads(env["manifest"].read_text())["skills"]


def test_check_clean(env):
    r = run(env, "check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_check_fails_on_unlisted_dir(env):
    mk_skill(env["skills"], "sh-c")
    r = run(env, "check")
    assert r.returncode == 1 and "unlisted:sh-c" in r.stdout


def test_check_fails_on_missing_dir(env):
    m = json.loads(env["manifest"].read_text()); m["skills"]["sh-ghost"] = {"status": "repo-local", "since": "2026-09-26"}
    env["manifest"].write_text(json.dumps(m))
    r = run(env, "check")
    assert r.returncode == 1 and "missing-dir:sh-ghost" in r.stdout


def test_check_fails_on_duplicate_key(env):
    text = env["manifest"].read_text().replace('"sh-b": {', '"sh-a": {"status":"retired","since":"x"}, "sh-b": {', 1)
    env["manifest"].write_text(text)
    r = run(env, "check")
    assert r.returncode == 1 and "duplicate-key:sh-a" in r.stdout


def test_check_fails_on_empty_dir(env):
    (env["skills"] / "sh-empty").mkdir()
    r = run(env, "check")
    assert r.returncode == 1 and "empty-dir:sh-empty" in r.stdout


def test_check_reports_runtime_drift_without_failing(env):
    (env["runtime"] / "sh-a" / "SKILL.md").write_text("# edited in runtime\n")
    r = run(env, "check")
    assert r.returncode == 0 and "runtime-diverged:sh-a" in r.stdout


def test_promote_copies_and_records_digest(env):
    r = run(env, "promote", "sh-b")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (env["runtime"] / "sh-b" / "SKILL.md").read_text() == "# skill\n"
    e = load(env)["sh-b"]
    assert e["status"] == "global" and e["synced_sha256"] == sha(env["skills"] / "sh-b" / "SKILL.md")


def test_promote_refuses_after_runtime_edit(env):
    assert run(env, "promote", "sh-b").returncode == 0
    (env["runtime"] / "sh-b" / "SKILL.md").write_text("# runtime edit after promote\n")
    (env["skills"] / "sh-b" / "SKILL.md").write_text("# bundle edit\n")
    r = run(env, "promote", "sh-b")
    assert r.returncode == 1 and "runtime-diverged:sh-b" in r.stdout
    assert (env["runtime"] / "sh-b" / "SKILL.md").read_text() == "# runtime edit after promote\n"


def test_retire_moves_bundle_and_removes_runtime_under_guard(env):
    r = run(env, "retire", "sh-a")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (env["skills"] / "sh-a").exists()
    assert (env["retired"] / "sh-a" / "SKILL.md").exists()
    assert not (env["runtime"] / "sh-a").exists()
    assert load(env)["sh-a"]["status"] == "retired"


def test_retire_refuses_on_runtime_divergence(env):
    (env["runtime"] / "sh-a" / "SKILL.md").write_text("# someone edited the live copy\n")
    r = run(env, "retire", "sh-a")
    assert r.returncode == 1 and "runtime-diverged:sh-a" in r.stdout
    assert (env["skills"] / "sh-a").exists() and (env["runtime"] / "sh-a").exists()


def test_record_sets_digest_only_when_identical(env):
    mk_skill(env["skills"], "sh-r", "# same\n"); mk_skill(env["runtime"], "sh-r", "# same\n")
    m = json.loads(env["manifest"].read_text()); m["skills"]["sh-r"] = {"status": "global", "since": "2026-09-26"}
    env["manifest"].write_text(json.dumps(m))
    assert run(env, "record", "sh-r").returncode == 0
    assert load(env)["sh-r"]["synced_sha256"] == sha(env["skills"] / "sh-r" / "SKILL.md")
    (env["runtime"] / "sh-r" / "SKILL.md").write_text("# differs\n")
    r = run(env, "record", "sh-r")
    assert r.returncode == 1 and "not-identical:sh-r" in r.stdout


def test_decoy_runtime_dir_survives_every_subcommand(env):
    for args in (("check",), ("promote", "sh-b"), ("record", "sh-a"), ("retire", "sh-a")):
        run(env, *args)
    assert (env["runtime"] / "_decoy" / "SKILL.md").read_text() == "# not ours\n"
```

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_skills_manifest.py -q` → all FAIL (no script).

- [ ] **Step 2: Implement `scripts/skills_manifest.py`**

```python
#!/usr/bin/env python3
"""skills_manifest.py — the Shepherd skill pack's promotion manifest (US-SH2-04).

    python3 scripts/skills_manifest.py check
    python3 scripts/skills_manifest.py promote <name>   # bundle -> ~/.claude/skills/<name>
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
  (unrecorded-runtime) — run `record` first.
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


def _guard_runtime(ctx: Ctx, name: str, entry: dict) -> str | None:
    r = ctx.runtime_skill(name)
    if not r.exists():
        return None
    recorded = entry.get("synced_sha256")
    if not recorded:
        return f"unrecorded-runtime:{name}"
    if sha256(r) != recorded:
        return f"runtime-diverged:{name}"
    return None


def cmd_promote(ctx: Ctx, name: str) -> int:
    data = load(ctx.manifest)
    entry = data["skills"].get(name)
    if entry is None or not ctx.bundle_skill(name).exists():
        print(f"ERROR not-in-bundle:{name}")
        return 1
    if entry.get("status") == "retired":
        print(f"ERROR retired:{name}")
        return 1
    if (err := _guard_runtime(ctx, name, entry)):
        print(f"REFUSED {err}")
        return 1
    dst = ctx.runtime / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ctx.skills / name, dst)
    entry.update(status="global", since=date.today().isoformat(), synced_sha256=sha256(ctx.bundle_skill(name)))
    save(ctx.manifest, data)
    print(f"promoted {name} -> {dst}")
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
    a = ap.parse_args(argv)
    ctx = Ctx(a.skills_dir, a.runtime_dir, a.retired_dir, a.manifest)
    if a.cmd == "check":
        return cmd_check(ctx)
    return {"promote": cmd_promote, "retire": cmd_retire, "record": cmd_record}[a.cmd](ctx, a.name)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run** — `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_skills_manifest.py -q` → 12 passed.

- [ ] **Step 4: Write the real manifest** — generate, then `record` each global:

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
skills = sorted(p.name for p in Path(".claude/skills").iterdir() if (p/"SKILL.md").exists())
runtime = Path.home()/".claude/skills"
m = {"version": 1, "skills": {}}
for n in skills:
    st = "global" if (runtime/n/"SKILL.md").exists() and n.startswith("sh-") else "repo-local"
    m["skills"][n] = {"status": st, "since": "2026-09-26"}
Path("skills-manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True)+"\n")
print(sum(e["status"]=="global" for e in m["skills"].values()), "global;", len(m["skills"]), "total")
PY
for n in $(python3 -c "import json;print(' '.join(k for k,v in json.load(open('skills-manifest.json'))['skills'].items() if v['status']=='global'))"); do python3 scripts/skills_manifest.py record "$n" || echo "RECORD FAILED $n"; done
python3 scripts/skills_manifest.py check
```
Expected: `29 global; 57 total` (24 overlaps + 5 adopted panels; if `sh-4-reviewer-panel` was decided "bundle wins" in Task 4.1 its `record` fails `not-identical` — then run `promote sh-4-reviewer-panel` instead, which is the guarded bundle → runtime copy the decision authorised). `check` → `0 errors, 0 drift`. The 11 `agentflow-*` dirs and `remotion-best-practices` are `repo-local`.

- [ ] **Step 5: Register the pre-commit gate**

`tools/precommit.d/10-skills-manifest`:
```bash
#!/usr/bin/env bash
# Repo-local DOD gate (DOCTRINE.md § DOD): the skill pack manifest must match .claude/skills/.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec python3 scripts/skills_manifest.py check
```
`chmod +x tools/precommit.d/10-skills-manifest`. Positive control: `mkdir .claude/skills/sh-zz && touch .claude/skills/sh-zz/SKILL.md && git add -A .claude/skills/sh-zz && git commit -F "$MSG" -- .claude/skills/sh-zz; echo exit=$?` → non-zero exit, output contains `unlisted:sh-zz`. Then `git rm -rq --cached .claude/skills/sh-zz && rm -r .claude/skills/sh-zz`.

- [ ] **Step 6: SKILLS.md gets a manifest section** — insert after the H1 intro:

```markdown
## Promotion manifest (Shepherd v2)

`skills-manifest.json` is the source of truth for every dir under `.claude/skills/`: `global` (also installed in `~/.claude/skills/`, digest-guarded), `repo-local` (this repo only), `retired` (moved to `.claude/skills-retired/`). Lifecycle: `python3 scripts/skills_manifest.py check | promote <name> | retire <name> | record <name>` (see the script header). `check` runs in this repo's pre-commit (`tools/precommit.d/10-skills-manifest`). Commands (`/sh:<name>`) need no promotion: `~/.claude/commands/sh` is a symlink to `.claude/commands/global/sh`. `skills-lock.json` is the third-party `npx skills` lock for `remotion-best-practices`, not ours. `agentflow-*` skills are `repo-local`; retirement of the 11 zero-invocation panels is decided per panel after the subagent-coverage question (spec US-SH2-05).
```

- [ ] **Step 7: Suite + commit**

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests -q` → `104 passed, 6 xfailed` (76 + 16 + 12).

```bash
git commit -F "$MSG" -- scripts/skills_manifest.py skills-manifest.json tests/test_skills_manifest.py tools/precommit.d/10-skills-manifest SKILLS.md
# msg: feat(skills): promotion manifest with digest-guarded promote/retire and pre-commit check (US-SH2-04 AC-1/2/4)
```
Expected: output shows `[pre-commit] 10-skills-manifest` and the count line.

### Task 4.3: Retire the `agentflow:` namespace (Decide-1 / Q5)

**Files:**
- Delete: `.claude/commands/global/agentflow/{autopilot,code-review-gate,fipd,kickoff,loop,orchestrator,retro,triage,workflow}.md` and the same 9 under `~/.claude/commands/agentflow/`
- Modify then delete: `.claude/commands/global/agentflow/{dor,dod}.md` and `~/.claude/commands/agentflow/{dor,dod}.md`
- Modify: `.claude/commands/global/goal.md:68,79`, `.claude/commands/global/mission.md:145`

- [ ] **Step 1: Migrate the three callers first** (the pipeline caller was migrated in Task 3.3):

- `goal.md:68`: `` the per-goal `agentflow:dor` result `` → `` the per-goal `sh:dor` result ``; `goal.md:79`: `did agentflow:dor PASS?` → `did sh:dor PASS?`.
- `mission.md:145`: `` `agentflow:dod` `` → `` `sh:dod` ``.

Run: `grep -rn 'agentflow:' .claude/commands/global/*.md ~/projects/00_Governance/scripts/*.py | grep -v '^.*commands/global/agentflow/'`
Expected: no output.

- [ ] **Step 2: Write the two-line aliases** (both locations, both files), e.g. `dor.md`:

```markdown
---
name: agentflow-dor
description: Retired alias. Use /sh:dor.
---
This command moved to `/sh:dor`. Invoke the `sh:dor` skill with the same arguments: $ARGUMENTS
```
(`dod.md` likewise with `sh:dod`.) Commit the aliases + caller edits as one commit so a bisect never lands on "callers migrated, alias missing":

```bash
git commit -F "$MSG" -- .claude/commands/global/goal.md .claude/commands/global/mission.md .claude/commands/global/agentflow/dor.md .claude/commands/global/agentflow/dod.md
# msg: refactor(commands): migrate goal/mission to sh:dor / sh:dod; agentflow:dor/dod become aliases (US-SH2-04 AC-3)
```

- [ ] **Step 3: Delete the 9 unused commands in both places, then the aliases** (same story, per Q5):

```bash
git rm -q .claude/commands/global/agentflow/{autopilot,code-review-gate,fipd,kickoff,loop,orchestrator,retro,triage,workflow}.md
git rm -q .claude/commands/global/agentflow/{dor,dod}.md
rm -r ~/.claude/commands/agentflow
ls .claude/commands/global/agentflow ~/.claude/commands/agentflow 2>&1 | head -2
```
Expected: both "No such file or directory". `~/.claude` is not a git repo; the deleted runtime copies are byte-identical to what git history holds under `.claude/commands/global/agentflow/` (verified 2026-09-26 in spec finding 5).

- [ ] **Step 4: Commit + log the propagation follow-up**

```bash
git commit -F "$MSG" -- .claude/commands/global/agentflow
# msg: chore(commands): retire the agentflow: namespace — 9 unused commands deleted, dor/dod aliases removed after caller migration (US-SH2-04 AC-3, Q5)
```
Append to the spec's Plan-time corrections section: `6. agentflow:* retired <date> <commit>; skill-sync DAG propagates the deletion to 13 projects at the next 06:00 run — verify one project (e.g. \`ls ~/projects/50_Excelbridge/.claude/commands/global/agentflow\` → absent) the day after.` Re-check the digest (`5176cdbc81e4`).

**Chunk 4 review:** AC-1 (`check` + pre-commit) has a positive control (`sh-zz`); AC-2's ordering constraint (runtime → bundle first, then `record`, only then any `promote`) is Task 4.1 → 4.2 Step 4; AC-4's decoy test is `test_decoy_runtime_dir_survives_every_subcommand`; AC-3's deletion is irreversible for the runtime dir but recoverable from git. The 11 zero-use panels are **not** retired here (spec: per-panel decision after Task 5.4).

---

## Chunk 5: US-SH2-07 hygiene, US-SH2-05 tail, US-SH2-06 inventories, closeout

### Task 5.1: Large files out of git, playgrounds deleted (US-SH2-07)

**Files:**
- Delete from git: `Agentflow-Skills-in-Action-2.pptx` (17 MB), `agentflow(Comparison - Outlook).numbers` (176 KB), `docs/business-panel-playground.html`, `docs/pipeline-playground.html`, `docs/spec-panel-playground.html`, `scripts/sync-skills-global.sh` (retired stub, C7)
- Modify: `docs/index.html:762-798` (remove the `playgrounds` group), `docs/shepherd.html:1193-1200` (remove the two nav links), `docs/README.md:17-19`, `AGENT_CAPABILITIES.md:113`, `ORIGIN.md:69-91`

- [ ] **Step 1: Back up first** (`feedback_backup_large_files_to_kingston_first`):

```bash
DST=/Volumes/KINGSTON/mac-backups/projects_offload/2026-09-26/20_agentflow; mkdir -p "$DST"
cp -p "Agentflow-Skills-in-Action-2.pptx" "agentflow(Comparison - Outlook).numbers" "$DST/" && ls -la "$DST" && cmp "Agentflow-Skills-in-Action-2.pptx" "$DST/Agentflow-Skills-in-Action-2.pptx" && echo backup-verified
```
Expected: `backup-verified`. Stop if `/Volumes/KINGSTON` is not mounted.

- [ ] **Step 2: Remove from the tree**

```bash
git rm -q "Agentflow-Skills-in-Action-2.pptx" "agentflow(Comparison - Outlook).numbers" docs/business-panel-playground.html docs/pipeline-playground.html docs/spec-panel-playground.html scripts/sync-skills-global.sh
```
History still holds the 17 MB blob; a history rewrite is on the still-ask list — **not** done here (say so in the NOT DONE line).

- [ ] **Step 3: Remove the dangling references**

- `docs/index.html`: delete the whole object from `    {\n      key: 'playgrounds',` through its closing `    }` (lines 762–798) **and the comma on the preceding group's closing brace** so the array stays valid JS. Check: `node -e "require('fs').readFileSync('docs/index.html','utf8')" && grep -c playground docs/index.html` → `0`. (If `node` is absent, open the file in Playwright/browser and check the console has no syntax error.)
- `docs/shepherd.html`: delete the two `<a href="…-playground.html" …>…</a>` blocks (lines 1193–1200). `grep -c playground docs/shepherd.html` → `0`.
- `docs/README.md`: delete lines 17–19; change line 3's "and panel playgrounds" to "" (keep the sentence grammatical).
- `AGENT_CAPABILITIES.md:113`: `  - Rate limits on GPT-4 tier` → `  - Rate limits depend on the vendor plan in force (the 2026-03 "GPT-4 tier" note is obsolete)`.

- [ ] **Step 4: Rewrite ORIGIN.md's merge framing** — replace lines 69–91 (`### Phase 5 — The Merge` … `**Shepherd.**`) with:

```markdown
### Phase 5 — The Name

The question became obvious: why three mental models? Ralph provides persistence, Superpowers provides execution discipline, SuperClaude provides analysis depth, AgentFlow provides governance — layers, not competitors. They were **not merged into one code base**: Superpowers and SuperClaude remain separate, live skill trees installed alongside this repo, and Ralph's stop hook is a plugin. What this repo did was give the governance layer one namespace (`/sh:`, 47 commands as of 2026-09) and one doctrine (`DOCTRINE.md`), and drop its own duplicates of what the other trees already did. The result needed a name that captured guiding a flock of tasks through a pipeline, protecting them from wolves (bugs), and getting them to completion.

**Shepherd.**
```
Also change the Timeline row `| 2026 Q1 | Phase 5: The merge — Shepherd v2.0 |` → `| 2026 Q1 | Phase 5: One namespace and one doctrine — Shepherd v2.0 |`.

- [ ] **Step 5: Suite + commit**

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests -q` → `104 passed, 6 xfailed`.

```bash
git commit -F "$MSG" -- "Agentflow-Skills-in-Action-2.pptx" "agentflow(Comparison - Outlook).numbers" docs/business-panel-playground.html docs/pipeline-playground.html docs/spec-panel-playground.html scripts/sync-skills-global.sh docs/index.html docs/shepherd.html docs/README.md AGENT_CAPABILITIES.md ORIGIN.md
# msg: chore(repo): move pptx/numbers to Kingston, delete playgrounds + retired sync stub, fix stale capability line, reframe ORIGIN merge story (US-SH2-07)
```

### Task 5.2: US-SH2-06 — inventory the three remaining clones (no deletion)

- [ ] **Step 1: Run the four-command inventory per clone**

```bash
for c in ~/projects/50_KETO/agentflow ~/projects/MAC/agentflow ~/projects/PY-Gen/agentflow; do
  echo "== $c"; git -C "$c" log --oneline --branches --tags --not --remotes | wc -l
  git -C "$c" for-each-ref refs/heads refs/tags --format='%(refname:short) %(objectname:short)'
  git -C "$c" stash list | wc -l; git -C "$c" status --ignored --porcelain | wc -l; done
```

- [ ] **Step 2: Record** — append to the spec's Plan-time corrections section a table `| clone | unpushed commits | local refs | stashes | untracked+ignored | disposition |` with one row per clone and one disposition row per non-empty result (expected: all zeros → "nothing unique; deletion is an operator ask"). Re-check the digest.

- [ ] **Step 3: Commit** — `git commit -F "$MSG" -- docs/specs/2026-09-26-shepherd-v2-audit-design.md` (msg: `docs(specs): clone inventories for 50_KETO/MAC/PY-Gen (US-SH2-06)`).

**Deleting any of the four clones stays an operator decision** (still-ask list). Do not `rm -rf`.

### Task 5.3: US-SH2-05 Plan tail — does a subagent's Skill call reach the observation log?

- [ ] **Step 1:** Note the newest line count: `wc -l ~/.local/state/claude-observations/$(date +%F).jsonl`.
- [ ] **Step 2:** Spawn one read-only `Explore` subagent whose only instruction is: "Invoke the `sh:help` skill via the Skill tool, then reply DONE." Wait for it.
- [ ] **Step 3:** `grep -c 'invoked sh:help\|invoked sh-help' ~/.local/state/claude-observations/$(date +%F).jsonl` before/after, and `grep 'sh:help\|sh-help' ~/.local/state/claude-observations/$(date +%F).jsonl | tail -2` to read the `sid`/`project` fields.
- [ ] **Step 4:** Append the answer (covered / not covered, with the two grep lines) to the spec's Plan-time corrections section as item 7. Re-check the digest. Commit (`docs(specs): US-SH2-05 subagent hook coverage measured`). This unblocks the per-panel retirement decisions — those are a **separate** story, not this plan.

### Task 5.4: Closeout

- [ ] **Step 1: BACKLOG** — move the Shepherd entry from `## Ready` to `## Done` with `(done 2026-09-26)`, keep the score line, add one line: `Shipped: DOCTRINE.md, scripts/dor_gate.py (+16 tests), tests/test_dod_chain.py (+7), scripts/skills_manifest.py (+12), agentflow: namespace retired, pptx/numbers → Kingston. Not done: clone deletion (operator), panel retirements (per-panel, after US-SH2-05 tail), history rewrite for the 17 MB blob (still-ask).`
- [ ] **Step 2: DOR gate on the live entry one last time** — `python3 scripts/dor_gate.py BACKLOG.md "Shepherd v2 — audit and doctrine collapse"` → `DOR-VERDICT: PASS` (the entry is in Done now; the gate does not care which section).
- [ ] **Step 3: Doctor + suite + decisions**

```bash
python3 ~/projects/00_Governance/scripts/install_repo_hooks.py --doctor ~/projects/20_agentflow
~/projects/00_Governance/.venv/bin/python -m pytest tests -q
~/projects/00_Governance/bin/decisions open -p 20_agentflow   # expect Q2 + the assumed entries from this plan as the review queue
```
- [ ] **Step 4: Commit + push** — `git commit -F "$MSG" -- BACKLOG.md` (msg: `docs(backlog): Shepherd v2 done`); `git push`. Also `cd ~/projects/00_Governance && git push` (KP entry, staleness test, pipeline stage C — check which branch Governance is on first; the last handover said `feat/yello-judge-drafts`, so push that branch and say so).
- [ ] **Step 5: `/sh:handoff`** with the `NOT DONE:` line listing: clone deletions (operator), 11 panel retirements (per-panel decisions), 17 MB blob in history (still-ask), skill-sync propagation check (next day), DeepSeek 503 diagnosis, memory-store unify (carried 3×).

**Chunk 5 review:** every deletion is either backed up and verified (`cmp`) or recoverable from git; the three operator-gated items are named, not silently dropped. US-SH2-05's Plan tail produces a measurement, not a retirement.

---

## Order and dependencies

```
1.0 → 1.1 → 1.2 (Governance) → 1.3 → 1.4        Chunk 1  (≤ ½ day)
2.1 → 2.2 (Governance) → 2.3                    Chunk 2  (≤ ½ day; needs Chunk 1 only for the DOD table already in DOCTRINE.md)
3.1 → 3.2 → 3.3 (Governance)                    Chunk 3  (≤ 1 day)
4.1 → 4.2 → 4.3                                 Chunk 4  (≤ 1 day; 4.3 needs 3.3's pipeline caller migration)
5.1 · 5.2 · 5.3 (independent) → 5.4             Chunk 5  (≤ ½ day)
```

Chunks 2 and 3 are independent of each other and could run in parallel worktrees; Chunk 4 waits for 3.3. Everything in Chunk 5 except 5.4 can run any time after Chunk 1.

## Decisions this plan pre-logs (review queue after execution)

| Where | Decision | Outcome |
|---|---|---|
| Task 1.4 | AC-1 excludes `DECISIONS.md` (append-only) | assumed |
| Task 1.4 | `/sc:cleanup→/sh:verify`, `/sc:design→/sh:plan`, `/sc:implement→/sh:execute` | assumed |
| Task 3.3 | pipeline stage C: `DOR_GATE_SCRIPT` env + `--skip-score` | assumed (Governance ledger) |
| Task 4.1 | `sh-4-reviewer-panel` truth direction | assumed |
| Task 1.0 (implicit) | US/AC read from the linked spec when the entry body has none; title-substring selector; bug-lite does not fail on a present score | assumed — log as one entry at Task 3.1 Step 7 |
| Task 4.2 (implicit) | `check` reports drift, exits 1 only on structural errors; `record` subcommand added | assumed — log at Task 4.2 Step 7 |
