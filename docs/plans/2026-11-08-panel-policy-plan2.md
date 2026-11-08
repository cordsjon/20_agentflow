# Panel Policy — Plan 2: Lens Packs, Roster Shrink, Multi-Panel Stage E Implementation Plan

> **For agentic workers:** REQUIRED: Use `/sh:execute` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every automated gate consumes the Plan 1 resolver end to end: dormant panels become lens packs attached to one spec-panel run, the roster shrinks to what the resolver can dispatch, stage E runs one panel per `Policy.panels` and writes one score line per panel, the DOR gate is re-run after scoring, `HEAVY_RE` stops classifying 29 of 52 Governance stories as heavy, and the workflow quality tail names the resolved panels instead of "all applicable".

**Architecture:** Three repos, no cross-repo import. 20_agentflow owns the roster (`experts/lenses/*.yaml`, `experts/panels/`, `.claude/commands/global/sh/*-panel.md`, `experts/PANEL_PROTOCOL.md`) and the vendored resolver; 00_Governance owns the pipeline (`backlog_dor_pipeline.py`, `dor_score_write.py`) and carries byte-identical copies of `panel_policy.py` + its test; `~/.claude/skills` (git repo `cordsjon/claude-skills`, not managed) owns `workflow/SKILL.md` and the runtime copies of the five role-only panel skills. The "lens-pack loader" is prose: the panel is an LLM reading YAML, so loading = an instruction in `spec-panel.md` + a shared `## Invocation` section in `PANEL_PROTOCOL.md`, pinned by a Python test over the YAML files.

**Tech Stack:** Python 3.11 stdlib (`re`, `json`, `dataclasses`, `subprocess`), PyYAML 6.0.3 (present in the 00_Governance venv — tests only; the vendored resolver stays stdlib), pytest, bash. Design: `docs/superpowers/specs/2026-11-08-panel-policy-design.md` (read §Roster, §Customers 2–4, §Layer 3). Plan 1 and its handover: `docs/plans/2026-11-08-panel-policy-resolver.md`, `HANDOVER-20_agentflow-2026-11-08-1454.md` (gotchas 1–3 are load-bearing here).

---

## Working rules for this plan

- **Managed repos:** `AF` = `~/projects-local/.worktrees/20_agentflow/<sid>`, `GOV` = `~/projects-local/.worktrees/00_Governance/<sid>` (`~/projects/00_Governance/bin/session-worktree ensure ~/projects/<repo>`). Claim files with concord `start_work` (absolute paths) before the first edit. Commit by explicit pathspec (`git add -A -- <paths> && git commit -- <paths>`); never bare `git commit`. Land with `~/projects/00_Governance/bin/git-land ~/projects/<repo>` in the background, **GOV first, then AF, in one sitting** — both repos' identity tests compare the sibling worktree first and fail a half-landed pair (handover gotcha 1).
- **Skills repo:** `~/.claude/skills` is its own git repo (origin `cordsjon/claude-skills`, hooks via global `core.hooksPath=~/.config/git/hooks`). Commit by pathspec and push; it is not managed, no worktree. Deleting a skill dir without committing there means the next sync restores it.
- **Interpreter:** `PY=~/projects/00_Governance/.venv/bin/python` for every pytest run (bare `python3` has no pytest). Scripts under test are stdlib-only; PyYAML is used only by the new lens test.
- **Canonical test commands:** AF `cd AF && $PY -m pytest tests/test_lens_packs.py tests/test_panel_propagation.py tests/test_panel_policy.py tests/test_dor_gate.py -q`; GOV `cd GOV && $PY -m pytest tests/test_panel_policy.py tests/test_dor_score_write.py tests/test_backlog_dor_pipeline_stage_c_script.py tests/test_backlog_dor_pipeline_stage_e_policy.py tests/test_backlog_dor_pipeline_assume_stage.py tests/test_backlog_dor_pipeline_lock.py tests/test_backlog_dor_pipeline_panel_critique.py -q`; full suites (`$PY -m pytest -q` in each) before landing.
- **Stamp gate:** a stamped session cannot Write cross-project — re-stamp per repo (`echo <proj> > $STAMP_FILE`, see `~/.claude/scripts/stamp-context.sh`). Never put bypass markers in vendored files (breaks byte identity).
- **Do not** hand-edit `scripts/panel_policy_data/projects.json` (hash-checked), re-run the census, or re-derive Plan 1's measurements.
- **Foundations:** `bin/foundations open ~/projects/20_agentflow` reports `undeclared` (no `FOUNDATIONS.md`). This plan is the second half of an operator-ruled design (2026-11-08 rulings 1–5), not optimization work; proceed and log the call in Task 10.

## File structure

| Path | Responsibility |
|---|---|
| `AF/experts/lenses/{security,mobile,osm,business}.yaml` | **New.** Lens packs: `name, description, applies_when, experts[2–3], checklist[≥3]`. Replace the four deleted panel YAMLs. |
| `AF/experts/panels/{security,mobile,osm,business,ai}-panel.yaml` | **Deleted.** |
| `AF/.claude/commands/global/sh/{security,mobile,osm,business}-panel.md` | Rewritten as thin aliases: run `/sh:spec-panel … --lenses <name>`; keep the `PANEL_PROTOCOL` reference. |
| `AF/.claude/commands/global/sh/ai-panel.md` | **Deleted** (skill copy already in `.claude/skills-retired/sh-ai-panel`). |
| `AF/.claude/commands/global/sh/spec-panel.md` | Gains step 0.5 (policy header) and step 2.5 (lens-pack loading); cap text 7 → "7, or 9 with ≥2 lenses". |
| `AF/experts/PANEL_PROTOCOL.md` | Gains `## Invocation` (`--ticket`, `--threshold`, `--lenses` semantics) — once, not per command. |
| `AF/experts/registry.yaml`, `AF/experts/README.md` | Regenerated / tree updated after the deletions. |
| `AF/.claude/skills/sh-{legal,devops,content,marketing,visualization}-panel/` → `AF/.claude/skills-retired/`, `AF/skills-manifest.json` | Retired via `scripts/skills_manifest.py retire`, which also removes `~/.claude/skills/<name>`. |
| `~/.claude/skills/sh-*-panel` (five) | Removed by the retire verb; committed + pushed in the skills repo. |
| `AF/tests/test_lens_packs.py` | **New.** Lens YAML shape, expert ids exist, lens set == `panel_policy.LENS_ORDER`, deleted panels absent, aliases carry `--lenses <name>`. |
| `AF/tests/test_panel_propagation.py` | Floor `>= 15` → measured post-shrink count. |
| `GOV/scripts/panel_policy.py` + `AF/scripts/panel_policy.py` | `HEAVY_RE` tuned (vendored; edit GOV, copy to AF). |
| `GOV/tests/test_panel_policy.py` + `AF/tests/test_panel_policy.py` | Three new `HEAVY_RE` tests (vendored test file). |
| `GOV/scripts/backlog_dor_pipeline.py` | `StageResult.panel`; `write_score_line(..., panel=)`; `resolve_policy()`; `run_stage_e_panel(panel=, lenses=)`; `run_stage_e_panels()`; `aggregate_panels()`; `run_story` writes per panel and re-runs C. |
| `GOV/scripts/dor_score_write.py` | `--panel <id>` (default `spec-panel`). |
| `GOV/tests/test_dor_score_write.py` | Two per-panel tests. |
| `GOV/tests/test_backlog_dor_pipeline_stage_e_policy.py` | **New.** argv with `--lenses`; one run per policy panel; track-none skip; lenses reach spec-panel only; C re-run catches a missing panel. |
| `~/.claude/skills/workflow/SKILL.md:57-75` | Quality tail names the resolved panels. |
| `AF/DECISIONS.md` | Q46+ via `bin/decisions add` (Task 10). |

---

## Chunk 1: Roster — lens packs, aliases, deletions (AF + skills repo)

### Task 1: Lens packs + their test (red first)

**Files:**
- Create: `AF/tests/test_lens_packs.py`
- Create: `AF/experts/lenses/security.yaml`, `mobile.yaml`, `osm.yaml`, `business.yaml`

- [ ] **Step 1: Write the test**

```python
"""Lens packs — experts/lenses/<name>.yaml — are what panel_policy.Policy.lenses names and
what /sh:spec-panel loads on `--lenses`. Design: docs/superpowers/specs/2026-11-08-panel-policy-design.md
§Roster. Shape + wiring only; whether the model then applies a checklist is not claimed here."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
LENSES = ROOT / "experts" / "lenses"
PANELS = ROOT / "experts" / "panels"
INDIVIDUALS = ROOT / "experts" / "individuals"
COMMANDS = ROOT / ".claude" / "commands" / "global" / "sh"
sys.path.insert(0, str(ROOT / "scripts"))
import panel_policy as pp  # noqa: E402

LENS_NAMES = ["security", "mobile", "osm", "business"]


def _lens_files() -> list[Path]:
    return sorted(LENSES.glob("*.yaml"))


def test_lens_set_matches_resolver_order():
    """A lens the resolver can name must exist as a file, and vice versa."""
    assert {f.stem for f in _lens_files()} == set(pp.LENS_ORDER) == set(LENS_NAMES)


@pytest.mark.parametrize("f", _lens_files(), ids=lambda f: f.stem)
def test_lens_pack_shape(f: Path):
    d = yaml.safe_load(f.read_text(encoding="utf-8"))
    assert set(d) >= {"name", "description", "applies_when", "experts", "checklist"}, set(d)
    assert d["name"] == f.stem
    assert 2 <= len(d["experts"]) <= 3, "a lens is 2-3 experts appended to spec-panel"
    for e in d["experts"]:
        assert (INDIVIDUALS / f"{e}.md").is_file(), f"unknown expert id {e}"
    assert len(d["checklist"]) >= 3 and all(isinstance(c, str) and c.strip() for c in d["checklist"])


@pytest.mark.parametrize("name", LENS_NAMES)
def test_lens_panel_yaml_is_gone_and_command_is_an_alias(name: str):
    assert not (PANELS / f"{name}-panel.yaml").exists(), "one source of truth: the lens YAML"
    alias = (COMMANDS / f"{name}-panel.md").read_text(encoding="utf-8")
    assert f"--lenses {name}" in alias, "alias must force its own lens"
    assert "PANEL_PROTOCOL" in alias, "wiring check (test_panel_propagation) must still see it"
    assert f"panels/{name}-panel.yaml" not in alias, "alias must not point at the deleted YAML"


def test_ai_panel_is_retired():
    assert not (PANELS / "ai-panel.yaml").exists()
    assert not (COMMANDS / "ai-panel.md").exists()
    assert (ROOT / ".claude" / "skills-retired" / "sh-ai-panel").is_dir()
```

- [ ] **Step 2: Run, expect failures**

Run: `cd AF && $PY -m pytest tests/test_lens_packs.py -q`
Expected: `test_lens_set_matches_resolver_order` FAIL (empty set vs 4), the four alias tests FAIL (`security-panel.yaml` exists), `test_ai_panel_is_retired` FAIL. The parametrized shape tests are skipped/absent (no files yet) — that is why the set test exists.

- [ ] **Step 3: Write the four lens packs**

`AF/experts/lenses/security.yaml`:
```yaml
# Lens pack — attaches to one /sh:spec-panel run on `--lenses security`. Replaces the
# standalone security-panel (deleted 2026-11-08, panel policy Plan 2). The resolver
# (scripts/panel_policy.py, layer 2) adds it from the census; `applies_when` is
# documentation only.
name: security
description: "Security lens — threat model, secrets discipline, trust boundaries, detection"
applies_when: "census (svc>=2 and cred>=5) or hosts>=10 or cred>=15; or `.panel-policy.toml` [policy] security = true"
experts: [filippo-valsorda, simon-willison, kelsey-hightower]
checklist:
  - "secret-leak scan: shape-detect literal secrets in the artifact (`key=`, `token=`, `password=`, `Authorization:`, `AKIA*`, `ghp_*`, `sk-*`, inlined .env). Any hit is CRITICAL before deliberation."
  - "trust-boundary inventory: every external ingress (HTTP body, upload, scraped page, LLM output, plugin input) names its validation step before business logic; a missing step is MAJOR."
  - "secrets discipline: storage, transport, rotation and scope are stated; the blast radius of one leaked credential is bounded."
  - "failure and detection: a compromise can be observed and contained — detection path and response named, not postulated."
```

`AF/experts/lenses/mobile.yaml`:
```yaml
name: mobile
description: "Mobile lens — platform fitness, lifecycle/permissions, device testability, store readiness"
applies_when: "census mobile=true (Flutter/Swift/Kotlin manifest present)"
experts: [jake-wharton, john-sundell, chris-lattner]
checklist:
  - "platform concerns named per target OS: permissions, lifecycle, storage, background limits."
  - "feasibility: every capability is buildable with the stated SDK/API on the stated minimum OS versions."
  - "testability: each component verifiable on device, emulator/simulator, or CI — the spec says which."
  - "distribution: signing, store guidelines and review readiness addressed when the story ships a build."
```

`AF/experts/lenses/osm.yaml`:
```yaml
name: osm
description: "OSM/geodata lens — tag evidence, CRS and admin_level anchoring, harvest pipeline ordering, ODbL"
applies_when: "census osm=true (geo dependency present, not shapely-only)"
experts: [jochen-topf, frederik-ramm, sarah-hoffmann]
checklist:
  - "tag-evidence: every OSM key=value named carries wiki status (documented/undocumented/deprecated) AND a measured corpus or taginfo count; either leg missing is MAJOR."
  - "boundary-crs: every distance, buffer, area or polygon names its CRS/unit (degrees are not meters); admin-area claims name the country-specific admin_level."
  - "pipeline-integrity: harvest -> derive -> classify -> join -> bundle order respected; a derived column names its backfill run; extract provenance (.pbf, date) recorded."
  - "ODbL attribution addressed for every shipped artifact."
```

`AF/experts/lenses/business.yaml`:
```yaml
name: business
description: "Business lens — positioning, pricing/launch assumptions, tail risk, stakeholder message"
applies_when: "story text matches pricing|launch|market|customer (panel_policy KEYWORD_LENSES)"
experts: [michael-porter, clayton-christensen, nassim-taleb]
checklist:
  - "positioning: the story names the alternative a customer would otherwise use and why this wins."
  - "pricing and launch assumptions are stated as testable claims with the measurement that would falsify them."
  - "tail risk: what breaks this (volatility, dependency, regulation) and the bounded downside."
  - "stakeholder message: the value is one sentence a customer understands without the codebase."
```

- [ ] **Step 4: Run, expect the shape tests green, the rest still red**

Run: `cd AF && $PY -m pytest tests/test_lens_packs.py -q`
Expected: `test_lens_set_matches_resolver_order` PASS, 4 × `test_lens_pack_shape` PASS, 4 alias tests + ai test FAIL (fixed in Task 3).

- [ ] **Step 5: Commit**

```bash
cd AF && git add -A -- experts/lenses tests/test_lens_packs.py && git commit -m "feat(panel-policy): lens packs security/mobile/osm/business + lens test

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- experts/lenses tests/test_lens_packs.py
```

### Task 2: Protocol `## Invocation` + spec-panel lens loading and policy header

**Files:**
- Modify: `AF/experts/PANEL_PROTOCOL.md` (append a section)
- Modify: `AF/.claude/commands/global/sh/spec-panel.md:11,22-33`

- [ ] **Step 1: Append to `PANEL_PROTOCOL.md`**

```markdown
## Invocation

Gate callers run a panel as `claude -p "/sh:<panel> --ticket <US-ID> [--threshold 7.0] [--lenses a,b]"`
(00_Governance `scripts/skill_runner.sh`; `backlog_dor_pipeline.run_stage_e_panel`). The flags arrive
as prompt text, not parsed options; every `sh:*-panel` honours them the same way:

- `--ticket <US-ID>`: the artifact is that story in the current repo's `BACKLOG.md` — the entry body
  plus its linked spec file when one exists. Locate it; do not ask for a paste.
- `--threshold <n>`: report the raw score in `PANEL-VERDICT`; the caller applies the threshold.
- `--lenses <csv>`: spec-panel only; other panels ignore it. For each name read
  `/Users/jcords-macmini/projects/20_agentflow/experts/lenses/<name>.yaml`: append its `experts` to the
  roster (cap `max-experts` 7; 9 when two or more lenses attach) and run each `checklist` item as a
  mandatory pre-scoring check — a miss is a MAJOR finding before deliberation, the same way
  `pre-scoring-checks` in the panel YAML work. Lens packs have no score line of their own; they are
  part of the spec-panel score.
- Which panels and lenses a story needs is decided by `python3 ~/projects/00_Governance/scripts/panel_policy.py
  resolve <BACKLOG.md> <US-ID> --json` (`panels`, `lenses`, `track`). The panel never chooses for itself.
```

- [ ] **Step 2: Edit `spec-panel.md`**

Line 11 (Usage) — append `[--ticket US-ID] [--lenses name,name]` after `[--verbose]`.

Insert after step 0 (line 22):
```markdown
0.5. **Policy header (BACKLOG stories)**: when the artifact is a BACKLOG story (`--ticket`, or an `@…/BACKLOG.md` reference with a story id), run `python3 ~/projects/00_Governance/scripts/panel_policy.py resolve <BACKLOG.md> <US-ID> --json` and print, as the first line of output, `policy: <track>; lenses: <lenses or none>; also required: <panels other than spec-panel, or none>` — the human sees what else the DOR gate will demand. `--lenses` on the command line overrides the resolver's `lenses`; without it, the resolver's list is used in step 2.5. Resolver unavailable → print `policy: unavailable` and continue without lenses (the gate itself fails closed; the review is still useful).
```

Insert after step 2 (line 24):
```markdown
2.5. **Load lens packs**: per `PANEL_PROTOCOL.md` §Invocation — one `/Users/jcords-macmini/projects/20_agentflow/experts/lenses/<name>.yaml` per lens from step 0.5 / `--lenses`; append its experts (cap below) and add its `checklist` to step 4's pre-scoring checks.
```

Step 3 (line 25): replace `up to \`max-experts: 7\` cap` with `up to the \`max-experts\` cap — 7, or 9 when two or more lens packs attach`.

- [ ] **Step 3: Propagation tests still green**

Run: `cd AF && $PY -m pytest tests/test_panel_propagation.py -q`
Expected: all pass (no allowlist phrase introduced; protocol reference intact).

- [ ] **Step 4: Commit**

```bash
cd AF && git commit -m "feat(panel-policy): PANEL_PROTOCOL invocation contract (--ticket/--threshold/--lenses); spec-panel loads lens packs and prints the policy header

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- experts/PANEL_PROTOCOL.md .claude/commands/global/sh/spec-panel.md
```

### Task 3: Thin aliases, panel deletions, ai-panel retirement, registry rebuild

**Files:**
- Rewrite: `AF/.claude/commands/global/sh/{security,mobile,osm,business}-panel.md`
- Delete: `AF/experts/panels/{security,mobile,osm,business,ai}-panel.yaml`, `AF/.claude/commands/global/sh/ai-panel.md`
- Regenerate: `AF/experts/registry.yaml`; edit `AF/experts/README.md:3,10-14`

- [ ] **Step 1: Write the four aliases** — same template, four names. `security-panel.md`:

```markdown
---
name: sh-security-panel
description: "Security lens on the spec panel — runs /sh:spec-panel with --lenses security (threat model, secrets, trust boundaries, detection)"
---

# /sh:security-panel — alias for `/sh:spec-panel --lenses security`

Since 2026-11-08 (panel policy, `docs/superpowers/specs/2026-11-08-panel-policy-design.md` §Roster) security is a
lens pack, not a standalone panel: `/Users/jcords-macmini/projects/20_agentflow/experts/lenses/security.yaml`
(experts + checklist) attaches to one spec-panel run. `scripts/panel_policy.py` adds it automatically for
projects the census marks; this command is the manual path.

## Behavior

Run `/sh:spec-panel <every argument given here> --lenses security`. Everything else is spec-panel's:
`/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` applied in full, scoring, the
`PANEL-VERDICT` line, score recording. There is no `experts/panels/security-panel.yaml` any more — do not look for one.
```

Descriptions for the other three: mobile — "Mobile lens on the spec panel — … (platform fitness, lifecycle, device testability, store readiness)"; osm — "OSM lens on the spec panel — … (tag evidence, CRS/admin_level, harvest pipeline, ODbL)"; business — "Business lens on the spec panel — … (positioning, pricing/launch assumptions, tail risk)". Keep the `name:` frontmatter as today (`sh-<x>-panel`).

- [ ] **Step 2: Delete**

```bash
cd AF && git rm -q experts/panels/security-panel.yaml experts/panels/mobile-panel.yaml experts/panels/osm-panel.yaml experts/panels/business-panel.yaml experts/panels/ai-panel.yaml .claude/commands/global/sh/ai-panel.md
```
`ai-panel` gets no retired copy of the command: `.claude/skills-retired/sh-ai-panel/SKILL.md` already preserves the roster, and git history keeps the file. (Logged in Task 10.)

- [ ] **Step 3: Rebuild the registry and fix the README**

```bash
cd AF && ./scripts/rebuild-registry.sh && git diff --stat -- experts/registry.yaml
```
Expected: the five `panels:` blocks gone, `Last rebuilt` date updated. The script regenerates the whole file from `individuals/` and `packs/`; if the experts section also churns (it was last rebuilt 2026-06-03), that churn is forced by the roster change and is accepted — say so in the commit body. The individuals' `panels: [business|mobile|osm|ai]` tags stay as they are (they now read as lens membership; design non-goal: no registry rebuild beyond what the roster forces).

`experts/README.md`: line 3 → `(spec-panel, architecture-panel, test-panel, plus lens packs in lenses/)`; in the tree replace the `panels/` children with `spec-panel.yaml`, `architecture-panel.yaml`, `test-panel.yaml` and add a `lenses/` node (`security.yaml … # 2-3 experts + checklist appended to a spec-panel run`).

- [ ] **Step 4: Run the lens test + propagation, expect lens test fully green**

Run: `cd AF && $PY -m pytest tests/test_lens_packs.py tests/test_panel_propagation.py -q`
Expected: `test_lens_packs.py` all pass. `test_panel_propagation.py::test_panel_population_is_discovered` **FAILS** (`found 17 … expected >=15` still passes here — 6 skills + 11 commands = 17 ≥ 15; it fails only after Task 4). All other propagation tests pass (aliases carry `PANEL_PROTOCOL`, no allowlist phrase).

- [ ] **Step 5: Commit**

```bash
cd AF && git add -A -- .claude/commands/global/sh experts/panels experts/registry.yaml experts/README.md && git commit -m "refactor(panel-policy): security/mobile/osm/business panels -> thin aliases over spec-panel lenses; retire ai-panel; rebuild registry

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- .claude/commands/global/sh experts/panels experts/registry.yaml experts/README.md
```

### Task 4: Retire the five role-only skills; lower the propagation floor to the measured count

**Files:**
- Move (via tool): `AF/.claude/skills/sh-{legal,devops,content,marketing,visualization}-panel/` → `AF/.claude/skills-retired/`; `AF/skills-manifest.json`
- Delete (via tool): `~/.claude/skills/sh-{legal,devops,content,marketing,visualization}-panel/`
- Modify: `AF/tests/test_panel_propagation.py:91`

- [ ] **Step 1: Retire with the manifest tool (never `rm -rf` by hand)**

```bash
cd AF && for s in sh-legal-panel sh-devops-panel sh-content-panel sh-marketing-panel sh-visualization-panel; do python3 scripts/skills_manifest.py retire "$s"; done
```
Expected: five `retired <name>` lines. The verb moves the bundle to `.claude/skills-retired/<name>`, removes `~/.claude/skills/<name>`, and sets `status: retired` in `skills-manifest.json`. **If one prints `REFUSED runtime-diverged:<name>`** (the runtime copy was edited 2026-11-04 after its 2026-09-26 sha was recorded): sync the bundle to the runtime first and re-record, then retire — `cp -R ~/.claude/skills/<name>/. .claude/skills/<name>/ && python3 scripts/skills_manifest.py record <name> && python3 scripts/skills_manifest.py retire <name>` (`record` requires bundle == runtime; that is its guard). No `--force` exists; do not edit the manifest by hand.

- [ ] **Step 2: Verify the runtime tree and the skills repo state**

```bash
ls -d ~/.claude/skills/sh-*panel*            # expect only sh-claude-code-panel
cd ~/.claude/skills && git status --porcelain | head   # expect ' D sh-legal-panel/SKILL.md' etc.
```

- [ ] **Step 3: Commit + push the skills repo**

```bash
cd ~/.claude/skills && git add -A -- sh-legal-panel sh-devops-panel sh-content-panel sh-marketing-panel sh-visualization-panel && git commit -m "retire five role-only panel skills (legal/devops/content/marketing/visualization) — panel policy Plan 2; YAML never existed, never ran

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- sh-legal-panel sh-devops-panel sh-content-panel sh-marketing-panel sh-visualization-panel && git push origin main
```
Their `evals/` go with them; `_eval-runner/results-*.jsonl` are historical records and stay.

- [ ] **Step 4: Measure the new population, then set the floor**

```bash
cd AF && $PY -c "import sys; sys.path.insert(0,'tests'); import test_panel_propagation as t; print(len(t.panel_skills()), sorted(t.panel_name(f) for f in t.panel_skills()))"
```
Expected: `12` — 1 skill (`sh-claude-code-panel`) + 11 commands (12 minus `ai-panel`). Use the printed number, not this expectation. Then edit line 91: `assert len(skills) >= 12, f"expected >=12 panel skills (post-shrink roster, 2026-11-08), found {len(skills)}"`, and add above it: `# 18 before the panel-policy roster shrink; 12 after (5 role skills retired, ai-panel retired). Measured 2026-11-08.` `test_agentflow_fork_is_not_silently_live` now `skip`s (no `sh-*panel*` left in the AF fork) — expected.

- [ ] **Step 5: Run, expect green**

Run: `cd AF && $PY -m pytest tests/test_panel_propagation.py tests/test_lens_packs.py -q`
Expected: all pass, one skip.

- [ ] **Step 6: Commit (AF)**

```bash
cd AF && git add -A -- .claude/skills .claude/skills-retired skills-manifest.json tests/test_panel_propagation.py && git commit -m "chore(panel-policy): retire sh-{legal,devops,content,marketing,visualization}-panel; propagation floor 15 -> 12 (measured)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- .claude/skills .claude/skills-retired skills-manifest.json tests/test_panel_propagation.py
```

**Chunk 1 review:** every deletion goes through a tool that records it (git rm, `skills_manifest.py retire`, skills-repo commit); nothing is removed only from disk. The alias files must keep the literal `PANEL_PROTOCOL` or the propagation denominator silently drops by four and the floor hides it — that is why `test_lens_panel_yaml_is_gone_and_command_is_an_alias` asserts the string.

---

## Chunk 2: `HEAVY_RE` tuning (GOV worktree, vendored)

### Task 5: Tighten the heavy markers; measure before/after on 00_Governance Ready

**Files:**
- Modify: `GOV/scripts/panel_policy.py:35-41`
- Modify: `GOV/tests/test_panel_policy.py` (+3 tests); copied to AF in Task 9

- [ ] **Step 1: Failing tests (append)**

```python
def test_auth_words_need_a_creating_verb():
    """'token budget' and 'auth header logged' are not new auth; 'add an OAuth login' is."""
    assert pp.resolve(story(want="to cut the token budget of the planner"), None, projects=PROJECTS).track == "normal"
    assert pp.resolve(story(want="the auth header to be logged"), None, projects=PROJECTS).track == "normal"
    assert pp.resolve(story(want="to add an OAuth login for the dashboard"), None, projects=PROJECTS).track == "heavy"


def test_across_is_not_a_heavy_marker_but_combine_is():
    assert pp.resolve(story(want="the sweep to run across feature branches"), None, projects=PROJECTS).track == "normal"
    assert pp.resolve(story(want="to combine the export and import commands"), None, projects=PROJECTS).track == "heavy"


def test_mobile_marker_is_a_platform_not_a_word():
    assert pp.resolve(story(want="a swift fix to the ios/ docs path"), None, projects=PROJECTS).track == "normal"
    assert pp.resolve(story(want="an iPhone build of the app"), None, projects=PROJECTS).track == "heavy"
```

- [ ] **Step 2: Run, expect 3 failures**

Run: `cd GOV && $PY -m pytest tests/test_panel_policy.py -q -k "auth_words or across or mobile_marker"`
Expected: FAIL (today's regex: bare `token`/`auth` → heavy; `across … feature` → heavy; `swift`/`ios` → heavy).

- [ ] **Step 3: Replace `HEAVY_RE`**

```python
HEAVY_RE = re.compile(
    # new persistence / service / integration / queue / auth — needs a creating verb nearby
    r"\b(?:new|add(?:s|ed|ing)?|create(?:s|d)?|introduce(?:s|d)?|migrat(?:e|es|ing))\b[^.\n]{0,40}"
    r"\b(?:table|schema|migration|service|daemon|integration|queue|scheduled job|cron(?:job)?"
    r"|auth(?:entication|orization)?|oauth|credentials?|secrets?|api[- ]keys?|login)\b"
    # combining two existing capabilities (bare "across" dropped: "across feature branches")
    r"|\b(?:combines?|merges?|unif(?:y|ies))\b[^.\n]{0,40}\b(?:capabilit(?:y|ies)|features?|commands?|skills?|pipelines?)\b"
    # mobile target — platform names, not the words "swift"/"ios" (adverb, path segment)
    r"|\b(?:flutter|swiftui|kotlin|android|ios app|iphone|ipad)\b"
    # data deletion
    r"|\bdelet(?:e|es|ing)\b[^.\n]{0,30}\b(?:data|rows|records|files)\b", re.IGNORECASE)
```
Update the module docstring's layer-1 line only if it enumerates markers (it does not today).

- [ ] **Step 4: Run the whole file, expect green**

Run: `cd GOV && $PY -m pytest tests/test_panel_policy.py -q`
Expected: `16 passed` (13 + 3). `test_heavy_marker_beats_trivial_text` ("creates a new table") still heavy.

- [ ] **Step 5: Measure old vs new on the live Ready list (read-only, scratch script)**

Write to the scratchpad (not the repo):
```python
# heavy_delta.py  <old panel_policy.py> <new panel_policy.py> <BACKLOG.md> <project>
import importlib.util, re, sys
from pathlib import Path
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old, new = load(sys.argv[1], "pp_old"), load(sys.argv[2], "pp_new")
backlog, project = Path(sys.argv[3]), sys.argv[4]
text = backlog.read_text(encoding="utf-8"); ready = text.split("\n## Ready", 1)[1].split("\n## ", 1)[0]
ids = re.findall(r"^### (US-[A-Z0-9-]+-\d+)", ready, re.M)
projects = new.load_projects(); rows = []
for sid in ids:
    si = new.story_input(backlog, sid)
    if not si: continue
    _, body, tags = si
    o = old.resolve(body, project, title_tags=tags, projects=projects)
    n = new.resolve(body, project, title_tags=tags, projects=projects)
    rows.append((sid, o.track, n.track, next((r for r in n.reasons if r.startswith("heavy:")), "")))
print(f"{len(rows)} Ready; heavy old={sum(r[1]=='heavy' for r in rows)} new={sum(r[2]=='heavy' for r in rows)}")
for r in rows:
    if r[1] != r[2] or r[2] == "heavy": print(*r, sep="\t")
```
```bash
git -C ~/projects/00_Governance show master:scripts/panel_policy.py > "$SCRATCH/pp_old.py"
python3 "$SCRATCH/heavy_delta.py" "$SCRATCH/pp_old.py" GOV/scripts/panel_policy.py ~/projects/00_Governance/BACKLOG.md 00_Governance
```
Expected: old heavy = 29 (handover), new heavy well below. **Acceptance:** read every remaining `heavy:<match>` line — each must name a real new persistence/service/integration/auth/queue/mobile/deletion. A false positive means one more regex iteration (max one; then stop and log it as open). Put the two counts and the list of flipped story ids in the commit body. Do not edit BACKLOG.md.

- [ ] **Step 6: Commit (GOV)**

```bash
cd GOV && git commit -m "fix(panel-policy): HEAVY_RE needs a creating verb for auth words; drop bare across/token/ios/swift

00_Governance Ready: heavy <old> -> <new> of <n>. Flipped: <ids>.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- scripts/panel_policy.py tests/test_panel_policy.py
```
The identity tests now fail in both repos until Task 9 copies and lands — intended (gotcha 1).

---

## Chunk 3: Pipeline — per-panel score lines, multi-panel stage E, C re-run (GOV)

### Task 6: `write_score_line(…, panel=)` and `dor_score_write.py --panel`

**Files:**
- Modify: `GOV/scripts/backlog_dor_pipeline.py:982-1016`
- Modify: `GOV/scripts/dor_score_write.py`
- Modify: `GOV/tests/test_dor_score_write.py` (+2 tests)

- [ ] **Step 1: Failing tests (append; real child processes, same seam as the file's existing tests)**

```python
STORY_HEAVY = ("## Ready\n\n### US-P-03: Introduce a new table for runs\n**As a** u, **I want** x, **so that** y.\n"
               "- [ ] AC-01: checkable\n\n**Priority:** P2 · **State:** Refining\n")


def test_per_panel_lines_coexist_and_each_replaces_only_itself(tmp_path):
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_HEAVY)  # heavy -> the gate wants spec-panel AND architecture-panel
    assert _run(CLI, backlog, "US-P-03", "7.8", "--date", "2026-11-08").returncode == 0
    gate = _run(GATE, backlog, "US-P-03")
    assert gate.returncode == 1 and "missing-panel:architecture-panel" in gate.stdout, gate.stdout
    assert _run(CLI, backlog, "US-P-03", "7.2", "--date", "2026-11-08", "--panel", "architecture-panel").returncode == 0
    assert _run(GATE, backlog, "US-P-03").returncode == 0
    assert _run(CLI, backlog, "US-P-03", "8", "--date", "2026-11-09", "--panel", "architecture-panel").returncode == 0
    text = backlog.read_text()
    assert text.count("spec-panel: 7.8 (") == 1 and text.count("architecture-panel: 8 (") == 1
    assert text.count("-panel: ") == 2, text
    assert _run(GATE, backlog, "US-P-03").returncode == 0


def test_bad_panel_name_is_refused(tmp_path):
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY)
    assert _run(CLI, backlog, "US-P-01", "8", "--panel", "nope").returncode == 2
    assert backlog.read_text() == STORY
```

- [ ] **Step 2: Run, expect 2 failures**

Run: `cd GOV && $PY -m pytest tests/test_dor_score_write.py -q`
Expected: new tests FAIL (`--panel` unrecognised → argparse exit 2 on the first, which makes the first test fail at its third assertion; the second passes by accident — fine, it is the regression guard).

- [ ] **Step 3: Implement**

`backlog_dor_pipeline.py` — replace `write_score_line`:
```python
PANEL_ID_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*-panel")


def write_score_line(backlog: Path, story_id: str, score: float, today: str,
                     panel: str = "spec-panel") -> StageResult:
    """Record a passing panel score in the story as `<panel>: <score> (<date>, body:<digest>)`.

    One line per panel (panel policy, Plan 2): this panel's earlier line is replaced, other
    panels' lines are kept. The digest is dor_gate.score_digest over the block with EVERY
    score line removed — the text the gate re-hashes — so all panel lines read current
    together. Under the BACKLOG lock, invariant-guarded on the story-id set.
    """
    if not PANEL_ID_RE.fullmatch(panel):
        return StageResult("score-write", False, "score_bad_panel", panel)

    def _panel_of(ln: str) -> str | None:
        m = dor_gate.SCORE_RE.search(ln)
        return m.group("panel") if m else None

    with backlog_lock(backlog):
        text = backlog.read_text()
        lines = text.splitlines(keepends=True)
        entry, err = dor_gate.find_entry(backlog, story_id)
        if entry is None:
            return StageResult("score-write", False, "score_story_not_found", err or "")
        start = entry.start - 1
        end = start + len(entry.lines)
        block = [ln for ln in lines[start:end] if _panel_of(ln) != panel]
        clean = dor_gate.Entry(title=entry.title, start=entry.start,
                               lines=[ln.rstrip("\n") for ln in block if _panel_of(ln) is None])
        line = f"{panel}: {score:g} ({today}, body:{dor_gate.score_digest(clean, backlog)})\n"
        score_idx = [i for i, ln in enumerate(block) if _panel_of(ln)]
        if score_idx:
            at = score_idx[-1] + 1            # keep the panel lines together
        else:
            state_idx = [i for i, ln in enumerate(block) if dor_gate.STATE_LINE_RE.search(ln)]
            if state_idx:
                at = state_idx[-1]
                if at > 0 and not block[at - 1].strip():
                    at -= 1  # keep the blank line before the metadata line
            else:
                at = len(block)
                while at > 1 and not block[at - 1].strip():
                    at -= 1
        block.insert(at, line)
        new_text = "".join(lines[:start] + block + lines[end:])
        if sorted(_STORY_RE.findall(new_text)) != sorted(_STORY_RE.findall(text)):
            return StageResult("score-write", False, "score_invariant_story_id_set")
        fsutil.atomic_write(backlog, new_text)
    return StageResult("score-write", True, detail=line.strip())
```

`dor_score_write.py`: docstring line 2 → `Record a panel score (spec-panel by default) on a BACKLOG story…`; usage line adds `[--panel <id>-panel]`; add
```python
    ap.add_argument("--panel", default="spec-panel",
                    help="panel id as the gate names it (spec-panel, architecture-panel, test-panel)")
```
and before the score range check:
```python
    if not bdp.PANEL_ID_RE.fullmatch(a.panel):
        print(f"dor-score-write: --panel {a.panel!r} is not a <name>-panel id", file=sys.stderr)
        return 2
```
and pass `panel=a.panel` to `write_score_line`.

- [ ] **Step 4: Run the writer tests and the stage-C tests, expect green**

Run: `cd GOV && $PY -m pytest tests/test_dor_score_write.py tests/test_backlog_dor_pipeline_stage_c_script.py -q`
Expected: all pass (`test_score_line_goes_stale_on_edit_and_is_replaced_not_stacked` still `count("spec-panel: ") == 1`).

- [ ] **Step 5: Commit**

```bash
cd GOV && git commit -m "feat(dor): one score line per panel — write_score_line(panel=), dor_score_write --panel

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- scripts/backlog_dor_pipeline.py scripts/dor_score_write.py tests/test_dor_score_write.py
```

### Task 7: Stage E runs every panel the policy names; C is re-run after the writes

**Files:**
- Modify: `GOV/scripts/backlog_dor_pipeline.py` (docstring line 18; `_is_score_reason` comment 526-530; `StageResult` 178-188; import next to line 72; stage E block 942-1033; `run_story` 1408-1447)
- Create: `GOV/tests/test_backlog_dor_pipeline_stage_e_policy.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Stage E consumes the panel policy: one `claude -p sh:<panel>` run per Policy.panels, lenses
passed to spec-panel only, one score line per panel, track `none` skips the panel, and stage C
is re-run after the writes so the gate — not the pipeline — judges completeness. Panel runs are
stubbed (they are `claude -p`); the BACKLOG write and the gate read are real."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import backlog_dor_pipeline as bdp  # noqa: E402

STORY_HEAVY = ("## Ready\n\n### US-P-03: Introduce a new table for runs\n**As a** u, **I want** x, **so that** y.\n"
               "- [ ] AC-01: checkable\n\n**Priority:** P2 · **State:** Refining\n")
STORY_TRIVIAL = ("## Ready\n\n### US-P-04: Add a --quiet flag `[trivial]`\n**As a** u, **I want** less noise, **so that** y.\n"
                 "- [ ] AC-01: flag exists\n\n**Priority:** P2 · **State:** Refining\n")


def _story(text, sid):
    return next(b for b in bdp.parse_ready_blocks(text) if b.id == sid)


@pytest.fixture
def quiet_stages(monkeypatch):
    monkeypatch.delenv("DOR_GATE_SCRIPT", raising=False)
    monkeypatch.setattr(bdp, "run_stage_f_selfcontained", lambda *a, **k: bdp.StageResult("selfcontained", True, advisory=True))
    monkeypatch.setattr(bdp, "run_stage_h_plan", lambda *a, **k: bdp.StageResult("plan", True, detail="p.md"))
    monkeypatch.setattr(bdp, "run_stage_d_fix", lambda *a, **k: pytest.fail("D must not run on score-only failures"))


def test_run_stage_e_panel_argv_carries_panel_and_lenses(monkeypatch):
    seen = []
    monkeypatch.setattr(bdp.subprocess, "run", lambda argv, **kw: seen.append(argv) or
                        subprocess.CompletedProcess(argv, 0, stdout="PANEL-VERDICT: 8.0\n", stderr=""))
    r = bdp.run_stage_e_panel("US-X-1", panel="spec-panel", lenses=("security", "osm"), dry_run=False)
    assert seen[-1][1:] == ["sh:spec-panel", "--ticket", "US-X-1", "--threshold", "7.0", "--lenses", "security,osm"]
    assert r.passed and r.score == 8.0 and r.panel == "spec-panel" and r.stage == "panel"
    r2 = bdp.run_stage_e_panel("US-X-1", panel="architecture-panel", lenses=("security",), dry_run=False)
    assert seen[-1][1:] == ["sh:architecture-panel", "--ticket", "US-X-1", "--threshold", "7.0"]
    assert r2.panel == "architecture-panel"


def test_one_panel_run_per_policy_panel_then_c_rechecks(tmp_path, quiet_stages, monkeypatch):
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_HEAVY)
    calls = []

    def fake_e(sid, *, panel="spec-panel", lenses=(), **k):
        calls.append((panel, tuple(lenses)))
        return bdp.StageResult("panel", True, score=7.5, panel=panel)
    monkeypatch.setattr(bdp, "run_stage_e_panel", fake_e)
    out = bdp.run_story(tmp_path, backlog, _story(STORY_HEAVY, "US-P-03"), dry_run=False)
    assert out["outcome"] == "CLEARED", out
    assert calls == [("spec-panel", ()), ("architecture-panel", ())]
    text = backlog.read_text()
    assert "spec-panel: 7.5 (" in text and "architecture-panel: 7.5 (" in text
    assert [s.stage for s in out["stages"]].count("dor") == 2, "C runs again after the score writes"
    assert bdp.run_stage_c_dor(backlog, _story(text, "US-P-03"), dry_run=False).passed


def test_track_none_skips_the_panel_and_clears(tmp_path, quiet_stages, monkeypatch):
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_TRIVIAL)
    monkeypatch.setattr(bdp, "run_stage_e_panel", lambda *a, **k: pytest.fail("policy none: no panel run"))
    out = bdp.run_story(tmp_path, backlog, _story(STORY_TRIVIAL, "US-P-04"), dry_run=False)
    assert out["outcome"] == "CLEARED", out
    assert "-panel: " not in backlog.read_text()
    assert any(s.stage == "panel" and "policy none" in s.detail for s in out["stages"])


def test_lenses_from_repo_declaration_reach_spec_panel_only(tmp_path, quiet_stages, monkeypatch):
    (tmp_path / ".panel-policy.toml").write_text("[policy]\nsecurity = true\n")
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_HEAVY)
    calls = []
    monkeypatch.setattr(bdp, "run_stage_e_panel", lambda sid, *, panel="spec-panel", lenses=(), **k:
                        calls.append((panel, tuple(lenses))) or bdp.StageResult("panel", True, score=7.5, panel=panel))
    bdp.run_story(tmp_path, backlog, _story(STORY_HEAVY, "US-P-03"), dry_run=False)
    assert calls == [("spec-panel", ("security",)), ("architecture-panel", ())]


def test_unscored_required_panel_is_needs_rework_not_cleared(tmp_path, quiet_stages, monkeypatch):
    """A panel that never produced a verdict: G runs once, E re-runs, still no verdict -> veto."""
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(STORY_HEAVY)

    def fake_e(sid, *, panel="spec-panel", lenses=(), **k):
        if panel == "spec-panel":
            return bdp.StageResult("panel", True, score=7.5, panel=panel)
        return bdp.StageResult("panel", False, "panel_no_verdict", panel=panel)
    monkeypatch.setattr(bdp, "run_stage_e_panel", fake_e)
    monkeypatch.setattr(bdp, "run_stage_g_autofix", lambda *a, **k: (bdp.StageResult("autofix", True), None))
    out = bdp.run_story(tmp_path, backlog, _story(STORY_HEAVY, "US-P-03"), dry_run=False)
    assert out["outcome"] == "NEEDS-REWORK", out
    assert "architecture-panel: " not in backlog.read_text()
```

- [ ] **Step 2: Run, expect 5 failures**

Run: `cd GOV && $PY -m pytest tests/test_backlog_dor_pipeline_stage_e_policy.py -q`
Expected: FAIL (`TypeError: unexpected keyword 'panel'`, `StageResult` has no `panel`, single E call, no second `dor` stage).

- [ ] **Step 3: Implement**

Import (after line 72 `import dor_gate`):
```python
import panel_policy  # noqa: E402  vendored from 20_agentflow; stage E runs the panels it names
```

`StageResult` — add after `score`:
```python
    panel: str = ""  # stage E only: which panel produced this result (spec-panel, architecture-panel, ...)
```

Docstring line 18–19 →
```
  E  panels           — one claude -p sh:<panel> per panel the policy names
                         (scripts/panel_policy.py), lenses on spec-panel; one score
                         line per panel; then C is re-run so the gate judges the set
```
`_is_score_reason` comment: delete the sentence "Stage E still scores spec-panel only until Plan 2 makes it multi-panel."

Stage E block — replace the `# --- Stage E` comment header and `run_stage_e_panel`:
```python
# --- Stage E: panels ------------------------------------------------------------
# AC-05 + panel policy (20_agentflow Plan 2, 2026-11-08): the resolver names the panels;
# each runs as `claude -p sh:<panel> --ticket <id> --threshold <t> [--lenses a,b]` via
# skill_runner.sh, PANEL-VERDICT parsed per quality_gate.parse_panel_verdict semantics
# (last line wins, fail-closed, FAIL:<reason> is structural). Lenses attach to spec-panel
# only (PANEL_PROTOCOL.md §Invocation). Track `none` runs nothing and passes.


def resolve_policy(backlog: Path, story_id: str):
    """panel_policy.Policy for the story as it is on disk now (after D/assume rewrites),
    or None when the resolver cannot answer — stage E then fails closed."""
    try:
        projects = panel_policy.load_projects()
        si = panel_policy.story_input(backlog, story_id)
        if si is None:
            return None
        _, text, tags = si
        return panel_policy.resolve(text, panel_policy.project_key(backlog), title_tags=tags,
                                    projects=projects, repo_root=backlog.parent)
    except panel_policy.PolicyUnavailable:
        return None


def run_stage_e_panel(story_id: str, *, panel: str = "spec-panel", lenses: tuple[str, ...] = (),
                      threshold: float = PANEL_THRESHOLD, dry_run: bool) -> StageResult:
    if dry_run:
        return StageResult("panel", True, detail=f"dry-run: would run sh:{panel}", panel=panel)
    cmd = [SKILL_RUNNER, f"sh:{panel}", "--ticket", story_id, "--threshold", str(threshold)]
    if lenses and panel == "spec-panel":
        cmd += ["--lenses", ",".join(lenses)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=STAGE_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        return StageResult("panel", False, "gate_timeout", panel=panel)
    except FileNotFoundError:
        return StageResult("panel", False, "tooling_unavailable", panel=panel)
    if proc.returncode != 0:
        return StageResult("panel", False, "panel_tooling_failed",
                           f"exit {proc.returncode}: {proc.stderr.strip()[-500:]}", panel=panel)
    r = parse_panel_verdict(proc.stdout, threshold)
    r.panel = panel
    return r


def aggregate_panels(results: list[StageResult]) -> StageResult:
    """What G and the veto see: one failing panel fails the set; details are concatenated
    with the panel named, so the autofix prompt knows which panel said what."""
    failed = [r for r in results if not r.passed]
    if not failed:
        return StageResult("panel", True, detail="; ".join(f"{r.panel}: {r.detail}" for r in results))
    return StageResult("panel", False, failed[0].veto_reason,
                       "\n\n".join(f"[{r.panel}] {r.detail or r.veto_reason}" for r in failed))


def run_stage_e_panels(backlog: Path, story: StoryBlock, *, dry_run: bool) -> tuple[list[StageResult], StageResult]:
    """(per-panel results, aggregate). Empty results with a passing aggregate = track none."""
    pol = resolve_policy(backlog, story.id)
    if pol is None:
        agg = StageResult("panel", False, "policy_unavailable")
        return [], agg
    if pol.track == "none":
        return [], StageResult("panel", True, detail="skipped (policy none)")
    results = [run_stage_e_panel(story.id, panel=p, lenses=tuple(pol.lenses), dry_run=dry_run)
               for p in pol.panels]
    return results, aggregate_panels(results)
```

`run_story` — replace from `e = run_stage_e_panel(story.id, dry_run=dry_run)` through the score-write block:
```python
    e_results, e = run_stage_e_panels(backlog, story, dry_run=dry_run)
    stages.extend(e_results or [e])
    panel_results = e_results
    f = run_stage_f_selfcontained(story, dry_run=dry_run)
    stages.append(f)

    # Autofix still consumes an advisory finding — "does not block" is not
    # "is ignored". Only a BLOCKING failure can end the run as NEEDS-REWORK.
    if not e.passed or not f.passed:
        g, fixed_body = run_stage_g_autofix(story, e, f, dry_run=dry_run)
        stages.append(g)
        if autofix_failure_vetoes(entry_stages=[e, f], autofix=g):
            return {"story_id": story.id, "outcome": "NEEDS-REWORK", "stages": stages}
        if fixed_body and not dry_run:
            apply_r = apply_story_replacement(backlog, story, fixed_body)
            stages.append(apply_r)
            # A failed write is always fatal — the story on disk may now be
            # inconsistent, so this is never an advisory-only situation.
            if not apply_r.passed:
                return {"story_id": story.id, "outcome": "NEEDS-REWORK", "stages": stages}
            story = StoryBlock(id=story.id, title=story.title, body=fixed_body,
                               start_line=story.start_line, end_line=story.end_line,
                               state=story.state)

        e2_results, e2 = run_stage_e_panels(backlog, story, dry_run=dry_run)
        stages.extend(e2_results or [e2])
        panel_results = e2_results
        f2 = run_stage_f_selfcontained(story, dry_run=dry_run)
        stages.append(f2)
        if stages_veto([e2, f2]):
            return {"story_id": story.id, "outcome": "NEEDS-REWORK", "stages": stages}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Q335 + Plan 2: every passing panel score becomes that panel's score line, written
    # after the last body change (G). Then C runs again: the GATE decides whether the set
    # is complete and current — the pipeline never infers it (handover 2026-11-08 gotcha 2).
    if not dry_run:
        for r in panel_results:
            if r.passed and r.score is not None:
                w = write_score_line(backlog, story.id, r.score, today, panel=r.panel or "spec-panel")
                stages.append(w)
                if not w.passed:
                    return {"story_id": story.id, "outcome": "NEEDS-REWORK", "stages": stages}
    c2 = run_stage_c_dor(backlog, story, dry_run=dry_run)
    stages.append(c2)
    if not c2.passed:
        return {"story_id": story.id, "outcome": "NEEDS-REWORK", "stages": stages}
```
Keep everything after (`plan_path = None` …) unchanged.

- [ ] **Step 4: Run the new file and every pipeline test that stubs stage E, expect green**

Run: `cd GOV && $PY -m pytest tests/test_backlog_dor_pipeline_stage_e_policy.py tests/test_backlog_dor_pipeline_stage_c_script.py tests/test_backlog_dor_pipeline_assume_stage.py tests/test_backlog_dor_pipeline_lock.py tests/test_backlog_dor_pipeline_panel_critique.py tests/test_backlog_dor_pipeline_plan_stage.py tests/test_backlog_dor_pipeline_selfcontained.py -q`
Expected: all pass. The existing stubs `lambda sid, **k: StageResult("panel", True, score=7.5)` still fit (`panel=""` → written as spec-panel); the tests that stub `write_score_line` also stub `run_stage_c_dor`, so the C re-run passes there. If a test stubs the writer but not C, it now fails on the re-run — that test was asserting CLEARED without a score line and must be fixed to stub C, not the other way round.

- [ ] **Step 5: Commit**

```bash
cd GOV && git commit -m "feat(dor-pipeline): stage E runs every policy panel, lenses to spec-panel, one score line per panel, C re-run after writes

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- scripts/backlog_dor_pipeline.py tests/test_backlog_dor_pipeline_stage_e_policy.py
```

**Chunk 3 review:** the per-panel `StageResult` keeps `stage="panel"` so ledger digests that filter on the stage name see the same rows as before, now with a `panel` key; `aggregate_panels` is never appended to `stages` when per-panel rows exist (no double counting). The C re-run is the design's "gate decides", and it also closes the 18-story gap from Plan 1 once nightly E writes the architecture lines.

---

## Chunk 4: Workflow tail, sync, landing, decisions

### Task 8: Workflow quality tail names the resolved panels

**Files:**
- Modify: `~/.claude/skills/workflow/SKILL.md:57-75`

- [ ] **Step 1: Edit** — under `### Step 4 — Always add quality tail` insert before the first code block:

```markdown
Resolve the panels first — `python3 ~/projects/00_Governance/scripts/panel_policy.py resolve <BACKLOG.md> <US-ID>` — and write the result into the tail. "All applicable panels" is not a definition; the resolver's list is.
```
In both code blocks replace the AC line with:
```
  - AC: every panel named by `panel-policy resolve` scores ≥ 7.0 (none when its track is `none`), tests pass, DOD checklist green, no Medium+ findings
  - Panels: <resolved list, e.g. spec-panel, architecture-panel [lenses: security] — or "none (track none)">
```

- [ ] **Step 2: Commit + push the skills repo**

```bash
cd ~/.claude/skills && git commit -m "workflow: quality tail names the panels panel-policy resolves, not 'all applicable'

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- workflow/SKILL.md && git push origin main
```
(`workflow/evals` does not reference the old wording — checked 2026-11-08.)

### Task 9: Sync the vendored pair, full suites, land GOV then AF, smoke

- [ ] **Step 1: Copy GOV → AF**

```bash
cp GOV/scripts/panel_policy.py AF/scripts/panel_policy.py
cp GOV/tests/test_panel_policy.py AF/tests/test_panel_policy.py
cd AF && git commit -m "chore(panel-policy): vendor HEAVY_RE tuning + tests from 00_Governance

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- scripts/panel_policy.py tests/test_panel_policy.py
```

- [ ] **Step 2: Identity tests from both worktrees** (they compare the sibling worktree of the same session first)

Run: `cd AF && $PY -m pytest tests/test_dor_gate_vendor_identity.py -q; cd GOV && $PY -m pytest tests/test_dor_gate_vendor_identity.py tests/test_backlog_dor_pipeline_stage_c_script.py::test_vendored_gate_matches_upstream -q`
Expected: all pass in both.

- [ ] **Step 3: Full suites**

Run: `cd AF && $PY -m pytest -q` then `cd GOV && $PY -m pytest -q`
Expected: green (Plan 1 baseline: AF 137 + new; GOV 3979 + new). Quote the summary lines in the handover; no "known failure" is acceptable this time.

- [ ] **Step 4: Land, GOV first, then AF — both in the background, the second after the first reports landed**

```bash
~/projects/00_Governance/bin/git-land ~/projects/00_Governance
~/projects/00_Governance/bin/git-land ~/projects/20_agentflow
```
A refusal on GOV's `land.check` that names `test_dor_gate_vendor_identity` means AF is not yet in the sibling worktree state — do not retry blindly; read `~/projects-local/.concord/land-logs/00_Governance/<ts>-<sid>.log`.

- [ ] **Step 5: Smoke from the main checkouts**

```bash
cd ~/projects/00_Governance
python3 scripts/panel_policy.py resolve BACKLOG.md US-GOV-GOAL-LOOP-01 --json     # panels [spec-panel, architecture-panel], basis census:2026-11-08, track normal
$PY scripts/dor_score_write.py --help | grep -c -- --panel                       # 1
ls ~/.claude/skills | grep -c 'panel'                                             # 2 (_panel-shared, sh-claude-code-panel)
ls ~/.claude/commands/sh/*-panel.md | wc -l                                       # 11
python3 - <<'EOF'
import sys; sys.path.insert(0, "scripts"); import panel_policy as pp, re
from pathlib import Path
b = Path("BACKLOG.md"); ready = b.read_text().split("\n## Ready",1)[1].split("\n## ",1)[0]
ids = re.findall(r"^### (US-[A-Z0-9-]+-\d+)", ready, re.M); pj = pp.load_projects()
h = sum(pp.resolve(pp.story_input(b, i)[1], "00_Governance", title_tags=pp.story_input(b, i)[2], projects=pj).track == "heavy" for i in ids)
print(f"heavy {h}/{len(ids)}")                                                    # the Task 5 'new' number
EOF
```

### Task 10: Decisions, debt, handover

- [ ] **Step 1: Log the calls this plan made that the design did not settle** (each in the AF worktree, then land; `--decided-by` defaults to agent — these are agent calls)

```bash
D=~/projects/00_Governance/bin/decisions
$D add 20_agentflow --context 'panel-policy/plan2' --category deviation --question 'Where does the lens-pack "loader" live?' --chosen 'Prose: PANEL_PROTOCOL.md §Invocation + spec-panel.md steps 0.5/2.5, pinned by tests/test_lens_packs.py over the YAML' --justification 'The panel executor is an LLM reading YAML; there is no Python executor to extend. The test pins shape, expert ids, lens set == LENS_ORDER and alias wiring.' --outcome applied --apply
$D add 20_agentflow --context 'panel-policy/plan2' --category tradeoff --question 'ai-panel retirement: keep a retired copy of the command file?' --chosen 'git rm only; .claude/skills-retired/sh-ai-panel already preserves the roster' --justification 'No commands-retired convention exists; inventing one for a single file is more structure than the artefact is worth.' --outcome applied --apply
$D add 20_agentflow --context 'panel-policy/plan2' --category tradeoff --question 'Per-panel stage E results: new stage names or a panel field?' --chosen 'StageResult.panel field; stage stays "panel"' --justification 'Ledger consumers filter on stage; a new name per panel would hide architecture runs from every digest written so far.' --outcome applied --apply
$D add 20_agentflow --context 'panel-policy/plan2' --category deviation --question 'HEAVY_RE: which markers were dropped?' --chosen 'bare token/auth (now need a creating verb), bare across, bare ios/swift (now platform names)' --justification 'Measured on 00_Governance Ready: heavy <old>-><new> of <n> (Task 5). token = LLM tokens, across = branches, swift = adverb in this corpus.' --outcome applied --apply
$D add 20_agentflow --context 'panel-policy/plan2' --category tradeoff --question 'Foundations for 20_agentflow are undeclared (bin/foundations open). Proceed with Plan 2?' --chosen 'Proceeded: Plan 2 completes an operator-ruled design (2026-11-08 rulings 1-5), not optimization work.' --justification 'TENET-11 undeclared branch: judged from the design doc; FOUNDATIONS.md for 20_agentflow remains to be written.' --outcome applied --apply
```
Individuals' stale `panels:` tags and the duplicate `dor_gate.py` identity test are left as they are — name both in the handover's `NOT DONE:` line, not as decisions.

- [ ] **Step 2: Debt gate** — no new CLI (only `--panel` on an existing one, and new verbs on none), so no memory pair is due. If the GOV commit is blocked by the debt gate anyway, read the message; do not defer with `ALLOW_AUTOMATION_DEBT=1` unless it names a new CLI.

- [ ] **Step 3: Handover** (`/sh:handoff`) with premises: both `master` shas, `test_lens_packs.py` count, propagation floor, GOV `heavy` count, `ls ~/.claude/skills | grep -c panel` = 2, `dor_score_write.py --help` has `--panel`, and the Ready-story block from Plan 1's handover re-measured once post-landing (how many of the 52 still fail `missing-panel:architecture-panel` — expected: all until the nightly E writes the lines; the first nightly after landing is the real test).

---

## Done when

- `experts/lenses/{security,mobile,osm,business}.yaml` exist and `tests/test_lens_packs.py` is green; the four `sh:*-panel` commands are aliases over `/sh:spec-panel --lenses <name>`; `ai-panel` and the five role skills are gone from both the runtime tree and the skills repo; `test_panel_propagation.py` floor equals the measured roster.
- `/sh:spec-panel` on a BACKLOG story prints `policy: …; lenses: …; also required: …` first and loads the lens packs; `PANEL_PROTOCOL.md` documents `--ticket/--threshold/--lenses` once.
- `backlog_dor_pipeline.run_story` runs one panel per `Policy.panels`, passes lenses to spec-panel only, writes one score line per panel, re-runs C, and skips panels on track `none`; `dor_score_write.py --panel architecture-panel` writes a line the gate accepts alongside the spec-panel line.
- `HEAVY_RE` no longer fires on bare `token`/`auth`/`across`/`ios`/`swift`; the 00_Governance Ready heavy count is recorded old→new in the commit body.
- Workflow quality tails name the resolved panels.
- Identity tests green from both main checkouts; full suites green; DECISIONS Q46–Q50 logged.
