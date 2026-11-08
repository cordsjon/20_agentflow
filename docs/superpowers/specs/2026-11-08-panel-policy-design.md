# Panel policy — design
<!-- spec-hierarchy: exempt -->

Date: 2026-11-08 · Repo: 20_agentflow (resolver, roster) · Customers in 00_Governance (`dor_gate.py`, `backlog_dor_pipeline.py`) and `~/.claude/skills/workflow`.
Source material: `HANDOVER-20_agentflow-2026-11-08-0949.md` (audit, usage count, census). Do not re-derive those numbers.

## Intent

Decide, deterministically and without asking, which expert panels a story must pass before it is Ready. Today the only automated panel is spec-panel; eleven other panel definitions exist, one of which (architecture) ran five times in 88 days and the rest zero or never. "All applicable panels ≥ 7.0" in the workflow quality tail has no definition of *applicable*. Unattended runs (`/assumed`, `/youdrive`, the DOR pipeline) therefore either run spec-panel alone or stall on a human choice.

Operator rulings that shape this (2026-11-08):

1. Panel choice is a complexity decision, not a domain decision.
2. The rule decides; it never presents a recommended set for confirmation.
3. A trivial change (one CLI flag, a tweak to an existing feature) may skip spec-panel entirely.
4. A project's default panel set is derived from measurement (the census), not from a human label. 00_Governance gets architecture by default because its numbers say so.
5. When a census refresh adds a panel to a project's defaults, Ready stories scored under the old policy re-run the new panel (churn accepted) — for the transition period. No grandfathering, no stored policy basis per story. Revisit once the roster and thresholds have settled.

## Goals

- One resolver, `panel policy`, callable from Python and from the shell, returning the panel list (possibly empty) for a story.
- Every automated gate that mentions panels consumes the resolver instead of hard-coding `spec-panel`.
- The roster shrinks to what the resolver can actually dispatch; dormant panels become lens packs attached to one spec-panel run.
- One source of truth per panel (the YAML).

## Non-goals

- Changing how a panel deliberates or scores (`PANEL_PROTOCOL.md` untouched).
- Persona grounding (gotcha 6 in the handover: no measured failure traces to it).
- Rebuilding `experts/registry.yaml` beyond what the new roster forces.
- The usage dashboard (US-CUS-TENETS-01 is separate).

## Anti-goals

- A resolver that asks. Any "confirm this set?" path is a failure of ruling 2.
- A hand-maintained per-project table. If someone must edit a project row by hand, the measured basis is gone (ruling 4). Overrides exist but are explicit and audited (below).
- Growing the roster before it shrinks.

## The resolver

Module: `scripts/panel_policy.py`, shipped the same way `dor_gate.py` is today: identical copies in `20_agentflow/scripts/` and `00_Governance/scripts/`, with a test in each repo asserting the two are byte-identical. `projects.json` travels with it (`scripts/panel_policy/projects.json` in both repos, same identity test). No cross-repo import; the gate stays self-contained. Shell entry point `panel-policy resolve <backlog> <story-ref>`; Python entry point `resolve(story_text: str, project: str) -> Policy`.

`project` is the BACKLOG's repo path relative to `~/projects` (the census's `project` column: `00_Governance`, `15_SAAS/25_Toolhub`), computed by the caller from `git rev-parse --show-toplevel`. A BACKLOG outside `~/projects` resolves as uncensused.

`Policy` carries: `track` (`none | normal | heavy`), `panels` (ordered list of panel ids, `spec-panel` first when present), `lenses` (lens-pack ids attached to spec-panel), `reasons` (one line per rule that fired, for the audit trail), and `basis` (`census:<date>`, `uncensused`, or `tag`).

The story text the resolver reads is the BACKLOG entry body plus the linked spec file when one exists — the same text `dor_gate.py` already digests for the score line, so the policy and the score cover identical input. If the resolver module or `projects.json` cannot be loaded, the gate fails closed with reason `policy-unavailable`; a broken landing is meant to be loud.

Three layers, applied in this order. Later layers add, never remove, except that `track = none` short-circuits everything.

### Layer 1 — change type (from the story text)

| Track | Rule | Result |
|---|---|---|
| `none` | Story tagged `` `[trivial]` ``, OR matches the trivial table and has no heavy marker | no panels; `dor_gate.py` track `none` |
| `heavy` | Any heavy marker | spec-panel + architecture-panel, plus layers 2–3 |
| `normal` | otherwise | spec-panel, plus layers 2–3 |

Trivial table (builder may extend, each entry must be a literal phrase or a tight regex, no LLM): "add(s) a flag", "add(s) an option", "rename", "default value", "help text", "typo", "log line", "wording"; AND the story's AC count ≤ 2; AND no heavy marker.

Heavy markers: new persistence (table, schema, migration), new service or daemon, new external integration, auth or credentials, queue or scheduled job, "combines" / "across" two existing capabilities, mobile target, data deletion.

No diff-size input. Every caller (Refining→Ready gate, stage E, workflow tail) runs before a branch exists, and a hint only some callers could supply would make the same story resolve differently depending on who asked. Text and tags only.

Tags use the existing title-line convention that `dor_gate.py`'s `TAG_RE` already matches (`` `[hotfix]` `` style): `` `[trivial]` `` forces track `none` for stories the regexes miss, `` `[heavy]` `` forces the heavy track. Both are visible in the BACKLOG line and therefore auditable. Precedence in `_track()`: `hotfix` > `bug` > `heavy` > `trivial` > resolver.

### Layer 2 — project default (from the census)

Input file: `scripts/panel_policy/projects.json`, generated by `scripts/panel_census.py` (moved from `~/.local/state/panel-census/2026-11-08/` into 00_Governance, committed; 20_agentflow carries the identical copy). One row per project with the **raw inputs** the rules below need: `loc, test_ratio, src_dirs, compose, db, svc, queue, llm, cred, hosts, mobile, osm`. The resolver recomputes the rules from those fields; the census's own `suggest[]` is not shipped, so there is one place the thresholds live. The file carries `generated: <date>`, the thresholds used, and `rows_sha256` — a hash the generator computes over the canonicalised rows. A hermetic test recomputes the hash from the rows and compares; a hand edit without re-running the generator fails it. The census itself needs the 41 repos on this machine and is not run in tests.

Rules (the thresholds from the handover, now the rule and not a suggestion):

- architecture: (≥ 3 source dirs or compose) and (db ≥ 3 or svc ≥ 2), or loc ≥ 15 000, or queue ≥ 5.
- security: (svc ≥ 2 and cred ≥ 5) or hosts ≥ 10 or cred ≥ 15. Projects may declare `security: true` in a `.panel-policy.toml` at the repo root for data-sensitivity reasons the census cannot see (15_belegfluss: tax data). Declaration can only add.
- test: the test lens is always inside spec-panel; the full test-panel runs when the project's test ratio < 20 %.
- mobile: Flutter/Swift/Kotlin manifest present.
- osm: geo dependency present and not `shapely`-only.

A project absent from `projects.json` (new repo, or fewer than 17 commits in 90 days at census time) gets `normal` defaults only: spec-panel with test lens. The resolver prints `basis: uncensused` so the gap is visible.

Refresh: the census is re-run by a scheduled job (dagu, monthly; the builder picks the DAG) that regenerates `projects.json` and opens a PR when rows change. The PR body lists the Ready stories whose required panel set grew (ruling 5: they re-run the added panel; the gate reports `missing-panel:<id>` until they do).

### Layer 3 — story keywords (last, add-only)

Keyword → lens or panel, read from `experts/panels/policy-keywords.yaml`. Initial table: pricing / launch / market / customer → business lens; the six auto-select rows already in `spec-panel.yaml:35-48` stay where they are (expert-level selection inside spec-panel) and are not duplicated here.

## The roster after this change

| Today | After |
|---|---|
| spec-panel | stays; gains lens-pack loading |
| architecture-panel | stays as a standalone panel (heavy track, census default) |
| test-panel | stays as standalone (test ratio < 20 %); its test lens also always-on inside spec-panel |
| security-panel, mobile-panel, osm-panel, business-panel | become lens packs (`experts/lenses/<name>.yaml`): 2–3 experts and a findings checklist appended to a spec-panel run. The YAML panels are deleted; their `commands/sh/<x>-panel.md` entries become thin aliases that run spec-panel with that lens forced, so manual invocation still works. |
| ai-panel | retired; spec-panel's LLM overlay (`spec-panel.yaml:130-137`) already covers LLM apps; roster targets ML model work none of the 41 repos does |
| consigliere-panel, personal-development-panel, claude-code-panel, research-panel, 4-reviewer-panel | untouched (project-specific or non-gate); not reachable from the resolver |
| sh-{legal,devops,content,marketing,visualization}-panel skills | deleted (never ran; YAML never existed) |

Lens pack format: `name`, `experts[]` (ids from `experts/individuals/`), `checklist[]` (findings the pack must address), `applies_when` (free text, documentation only; the resolver decides). The panel executor loads the lens packs named in `Policy.lenses` and appends their experts up to `max-experts`, raising the cap to 9 when two or more lenses attach.

`tests/test_panel_propagation.py:91` asserts ≥ 15 panel skills and that each references `PANEL_PROTOCOL` or `PANEL_CORE`. After the shrink the floor is lowered to the counted post-shrink number (measured, not guessed) and the thin alias `.md` files keep the protocol reference so the wiring check still bites.

One source of truth: `commands/sh/*-panel.md` rosters are generated from the YAML by `scripts/rebuild-registry.sh` (extended), with a test asserting they match. The builder may instead make the `.md` files roster-free and read the YAML at run time; either way the duplicated list goes.

## Customers

1. **`dor_gate.py`** (identical copies in 20_agentflow/scripts and 00_Governance/scripts; the 00_Governance copy is the one the pipeline imports — keep them identical or make one import the other). Changes: `--track` gains `none`, which keeps the structural checks (`no-user-story`, `no-acceptance-criteria`, `us-without-ac`) and skips only the score — a trivial story can still be malformed, and the trivial rule itself reads the AC count; `_track()` consults the resolver when no override is passed (tags `hotfix`/`bug` keep precedence); `SCORE_RE` generalises to `(?P<panel>[a-z-]+-panel): <score> (<date>, body:<hex>)`; `_check_normal` requires one current score line per panel in `Policy.panels`; lens packs do not get their own score line, they are part of the spec-panel score. `reasons[]` gains `missing-panel:<id>` and `track-none` entries.
2. **`backlog_dor_pipeline.py` stage E** (`run_stage_e_panel`, line 1000). Resolves policy once per story, runs each panel in `Policy.panels` through `claude -p sh:<panel> --ticket <id> --lenses <csv>`, parses one `PANEL-VERDICT` per run, writes one score line per panel. `track = none` records `panel: skipped (policy none)` and passes. `--assume` unchanged. Contract check (2026-11-08): `spec-panel.md`, `architecture-panel.md`, `test-panel.md` and `security-panel.md` all emit `PANEL-VERDICT`; none of them, spec-panel included, declares `--ticket` or `--threshold` — stage E passes those through `claude -p` as prompt text today. The other panels therefore start at parity with spec-panel; `--lenses` is new and is added to the shared `PANEL_PROTOCOL.md` invocation section, not to each command file.
3. **Workflow quality tail** (`~/.claude/skills/workflow/SKILL.md:61`): "all applicable panels" becomes "all panels named by `panel-policy resolve <US>` score ≥ 7.0". Generated TODO lines carry the resolved list.
4. **`/sh:spec-panel`** prints a header `policy: <track>; lenses: <list>; also required: <panels>` so a human running it by hand sees what else the gate will demand.

`/assumed` and `/youdrive` need no change: they already defer to the gate.

## Constraints

- No LLM call anywhere in the resolver. Regex, tags, JSON lookup.
- Resolver must run in under one second with no network.
- Managed repos: 20_agentflow and 00_Governance are edited only in session worktrees; the `dor_gate.py` copies ship in one landing or the pipeline breaks between them.
- Tests sized like `tests/test_dor_gate.py` and `tests/test_panel_propagation.py`: one focused test per stated behaviour. Red-green on the new `none` track and the generalised `SCORE_RE` before the pipeline change.

## Left to the builder

- Package shape of `panel_policy.py` and whether `DiffStat` is computed inside or passed in.
- Exact regex set for the trivial table and heavy markers (the lists above are the seed; the builder should check them against the last 30 stories in `00_Governance/BACKLOG.md` and report the hit rate before freezing).
- Which dagu DAG hosts the monthly census refresh.
- Whether `commands/sh/*-panel.md` are generated or roster-free.
- Order of landing: resolver + tests → roster shrink → `dor_gate.py` → pipeline → workflow skill text.

## Decisions taken in this document (mine, not the operator's)

- `` `[trivial]` `` / `` `[heavy]` `` title-line tags as the override mechanism (existing `TAG_RE` convention), rather than a sidecar file.
- Lens packs raise `max-experts` from 7 to 9 when two or more attach.
- `.panel-policy.toml` as the per-repo add-only declaration file.
- Uncensused projects default to spec-panel + test lens, not to the heavy track.
- Monthly census refresh via PR rather than silent regeneration.
- Resolver and `projects.json` vendored as identical copies in both repos (the `dor_gate.py` pattern), no cross-repo import; missing resolver fails the gate closed.
- No diff-size input to the resolver (callers run before a branch exists).
- Track `none` keeps structural checks, skips only the score.
- `projects.json` ships raw inputs plus a rows hash; the resolver recomputes the rules; hand edits fail the hash test.
- Resolver text = entry body + linked spec, the same input the score digest covers.
