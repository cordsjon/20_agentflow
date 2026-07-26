# BACKLOG — Cross-Project

> **Central priority authority.** Items here span projects or are project-agnostic.
> Project-scoped items stay in their own BACKLOG.md.
>
> Items flow: **Ideation -> Refining -> Ready -> project TODO-Today.md (execution)**

---

## Ideation

> **Moved to Idea Forge** — items imported into Consigliere Idea Forge (`http://localhost:9104/ideas`) on 2026-04-09.

### US-AF-01: Register measure-panel-vs-analyze.sh so it's rediscovered, not rebuilt

> Origin: Automation debt analysis (2026-07-20) — created `scripts/measure-panel-vs-analyze.sh` (2026-06-25) with no memory registration; a future session re-derives the same token-cost harness instead of finding it.

**As a** developer measuring panel vs. analyze token cost,
**I want** `scripts/measure-panel-vs-analyze.sh` registered in memory with a reference + feedback pair,
**so that** future sessions find and reuse the existing harness instead of rewriting a `claude -p --output-format json` cost-measurement script from scratch.

**Acceptance Criteria:**
- [ ] Reference memory written: `reference_measure-panel-vs-analyze_cli.md` in memory/ + MEMORY.md pointer
- [ ] Feedback memory written: `feedback_use_measure-panel-vs-analyze_cli.md` in memory/ + MEMORY.md pointer
- [ ] Project CLAUDE.md (or 20_agentflow-specific tool preferences doc) updated with the invocation rule: use `scripts/measure-panel-vs-analyze.sh [TARGET_FILE]` — never hand-roll a new token-measurement script
- [ ] Test: grep memory dir for `measure-panel-vs-analyze` returns both files; a fresh session asked "measure panel vs analyze token cost" finds the script via memory before writing new code

**Size:** S · **Tags:** `[agentflow]` `[registration]` `[cli]`

### US-AF-02: Extract nosignups fixture generator from plan-doc heredoc into a reusable script

> Origin: Automation debt analysis (2026-07-20) — `docs/plans/2026-07-20-nosignups-catalog-sync.md` Task 1 embeds a heredoc Python script (trims the 222-tool `nosignups_full.json` payload into 5-tool/4-tool fixtures) inline in a plan doc; regenerating fixtures after upstream drift means re-copying it out of prose again.

**As a** developer maintaining the nosignups catalog test fixtures,
**I want** the fixture-trimming logic extracted into a standalone script under `scripts/` or `tests/fixtures/`,
**so that** regenerating `nosignups_5tools.json`/`nosignups_4tools.json` after upstream `tools.json` drift is one command, not a re-read of the plan doc to find and re-paste the embedded heredoc.

**Acceptance Criteria:**
- [ ] Fixture-generation logic (currently embedded in `docs/plans/2026-07-20-nosignups-catalog-sync.md` Task 1 Step 1) moved to `scripts/gen_nosignups_fixtures.py` (or equivalent), taking the source `tools.json` path as an argument
- [ ] Script is idempotent: re-running against unchanged upstream data reproduces byte-identical fixtures
- [ ] Reference memory written: `reference_gen_nosignups_fixtures_cli.md` + MEMORY.md pointer
- [ ] Feedback memory written: `feedback_use_gen_nosignups_fixtures_cli.md` + MEMORY.md pointer
- [ ] Test: `python3 scripts/gen_nosignups_fixtures.py tests/fixtures/nosignups_full.json` regenerates `nosignups_5tools.json` and `nosignups_4tools.json` matching current committed fixtures byte-for-byte

**Size:** M · **Tags:** `[agentflow]` `[nosignups]` `[test-fixtures]` `[automation]`

## Refining

### US-AF-03: Panel protocol — external-contract conformance stage + auto-fix re-gate

> Origin: ARD fleet-discovery spec review (a2a-cli-registry, 2026-07-26). Two panels
> (ai-panel 8.4, spec-panel 8.6) passed a spec that codex then scored 3-4/10 with three
> CRITICALs. Post-mortem found four protocol-level root causes (all verified, not guessed):
>
> 1. **Grounding is internal-only.** `PANEL_PROTOCOL.md ## Grounding` mandates resolving
>    claims in repo source or the reviewed document — no step ever fetches the EXTERNAL
>    standard the design claims conformance to. The ARD §3.4 url-as-artifact-document
>    MUST-violation and the §4.2.1 FQDN-publisher rule were only catchable by reading
>    `ard.md` itself, which codex did and the panels structurally could not.
> 2. **Risk-note laundering.** The draft's Risk 2 already disclosed the url-vs-endpoint
>    tension ("flagged for re-check at v1.0"); both panels treated the author's hedge as
>    mitigation. Disclosure is not resolution when an external MUST is violated.
> 3. **No consumer dry-run.** Emitted artifacts (claude mcp add command, OpenWorker config)
>    were reviewed for shape, never checked against the consumer's real contract — the
>    generated command dialed a bearer-gated endpoint with no auth header → guaranteed 401.
>    (Existing memory rule feedback_verify_contract_against_consumer exists but is not
>    encoded in the panel protocol.)
> 4. **Auto-fix without re-gate.** The https→http downgrade hole did not exist in the
>    draft — it was INTRODUCED by the ai-panel's own auto-fix ("path/scheme differences on
>    the same host are accepted") and no pass ever reviewed the fixes themselves.
>    Structural note: panels are personas inside ONE model context and inherit its blind
>    spots; the remedy must be deterministic protocol steps, not "personas try harder."

**As a** panel-gate consumer relying on sh:*-panel verdicts before implementation,
**I want** the shared panel protocol to verify external-spec conformance, dry-run emitted
artifacts against their consumers, and adversarially re-gate its own auto-fixes,
**so that** a passing panel score means the design survives the checks an independent
reviewer (codex) would apply — instead of only internal-consistency checks.

**Spec:** `docs/specs/2026-07-26-panel-protocol-external-conformance-design.md`

**Acceptance Criteria:**
- [ ] AC-1: `PANEL_PROTOCOL.md` gains an **External-Contract Conformance** stage: when the
  reviewed artifact names an external spec/protocol it implements (ARD, MCP, A2A, OAuth,
  …), the panel MUST retrieve the authoritative spec text (curl/WebFetch, cached to the
  session scratchpad), enumerate the MUST/SHALL clauses the design touches, and verify
  each. A disclosed-but-unresolved MUST violation is a CRITICAL finding — an author risk
  note never downgrades it (kills root causes 1+2).
  **Constraint amendment:** the same edit supersedes `PANEL_PROTOCOL.md:10` ("No new
  indexing dependency. Serena + Read only.") with a scoped exception permitting
  curl/WebFetch for external spec documents only; the no-new-*indexing*-dependency rule
  stands. Without this the two lines conflict and the stage is unimplementable as written.
- [ ] AC-2: Protocol gains a **Consumer dry-run** rule: any artifact the design emits for a
  named consumer (CLI command, config snippet, API payload) is checked against that
  consumer's actual contract (its docs, config schema, or source when local) with the
  question "does this run/connect as generated?" — cross-linking
  feedback_verify_contract_against_consumer (kills root cause 3).
  **Two tiers, cheap first:** Tier 1 (always, zero-fetch) — an emit that contradicts the
  reviewed document's OWN claims about the endpoint it targets is CRITICAL; this alone
  catches the ARD 401 (line 134 emits unauthenticated vs lines 66/143 "bearer auth").
  Tier 2 (escalation) — fetch the consumer's real contract when Tier 1 is clean.
- [ ] AC-3: `PANEL_CORE.md` Auto-Fix Policy gains a **fix re-gate**: after applying fixes,
  one adversarial refute pass runs over the fix diff (via
  `00_Governance/scripts/codex_refute.py` where codex is available, self-refute otherwise)
  BEFORE commit; findings against the fixes are fixed and re-gated once (kills root
  cause 4). **Loop bound — stop at two:** two consecutive rounds finding author-introduced
  defects halts the loop and escalates to the operator; no third patch. (Adopts the
  existing gate in `codex_refute.py`, which exists because a self-scored 7.4 spec was
  scored 4.2→4.1→3.0 by codex as its author "fixed" it.)
- [ ] AC-4 (regression fixture, falsifiable): running the upgraded spec-panel against the
  pre-codex ARD spec revision (`a2a-cli-registry` commit `c481ddd`) catches at least 2 of
  the 3 codex CRITICALs (ARD §3.4 url-vs-endpoint, missing bearer in emits, https→http
  downgrade) WITHOUT codex assistance — verified red-first by confirming the current
  protocol misses all 3 on the same fixture.
  **Determinism rule:** panels are non-deterministic, so the assertion is a detection floor
  over N=3 `--model`-pinned runs — median signature-match ≥ 2 passes; the red-first run on
  the current protocol must produce median 0, and its output is committed to
  `tests/fixtures/` before the test is accepted. Harness `scripts/panel_regression.sh`
  clones `scripts/measure-panel-vs-analyze.sh` and reuses `parse_panel_verdict()` from
  `00_Governance/scripts/quality_gate.py` (fail-closed on a missing verdict line).
- [ ] AC-5 (propagation — the blast radius the story originally under-scoped): the new
  stages reach all **13** in-scope surfaces, not 2 (1 PANEL_PROTOCOL + 1 PANEL_CORE +
  `00_Governance/CLAUDE.md §8` + **10** `sh-*-panel/SKILL.md` that load the protocol;
  verified `grep -rl PANEL_PROTOCOL --include=SKILL.md` → 10, PANEL_CORE consumers a strict
  subset). Those 10 Load-Protocol lines each name an allowlist of sections ("apply its
  Grounding and Refute Stage sections"), so appending a stage to `PANEL_PROTOCOL.md` leaves
  it **inert**. Rewrite them to apply the protocol wholesale (preferred — removes the
  10-file edit on every future protocol change). `00_Governance/CLAUDE.md §8` (line 112) is
  updated in the same change: it is the canonical source `PANEL_CORE.md` cites, so leaving
  it stating the old policy re-introduces the drift the sync note guards. Test: a check
  asserts all 13 surfaces reference the new stages.
- [ ] AC-6 (gate independence): this story is gated by
  `codex_refute.py <spec> --gate 7.0`, NOT by `sh:spec-panel`. Rationale: spec-panel scored
  8.6 on the defective ARD spec, so scoring the spec-panel repair with the un-upgraded
  spec-panel is circular and its auto-fixes inherit root cause 4. spec-panel may run for
  coverage; codex is the tiebreaker. Recorded score lands in the spec doc §5.

**Size:** L · **Tags:** `[agentflow]` `[panels]` `[protocol]` `[quality]`
_(Re-sized M→L at DOR: 13 files + a new regression harness exceeds M's 4-8 queue items.)_

### US-AF-04: 7 panel skills load no grounding protocol at all

> Surfaced by the US-AF-03 DOR gate (2026-07-26), pre-existing and independent of it.
> Of 17 `sh-*-panel` skills, only 10 reference `PANEL_PROTOCOL.md`. These 7 reference
> neither it nor `PANEL_CORE.md`: `sh-4-reviewer-panel`, `sh-claude-code-panel`,
> `sh-content-panel`, `sh-devops-panel`, `sh-legal-panel`, `sh-marketing-panel`,
> `sh-visualization-panel`. Grepping them for `grounding|refute|shared core|load protocol`
> returns nothing — the only hit is `sh-claude-code-panel:30`, a verbatim COPY of the
> Verbosity block rather than a load of the shared file (the drift the PANEL_CORE sync
> note exists to prevent, already realized).
>
> Consequence: these panels can report ungrounded, un-refuted findings today, and
> `sh-legal-panel` in particular carries real-world risk. Deliberately excluded from
> US-AF-03's AC-5 to avoid ballooning an already-L story.

**As a** consumer of any `sh:*-panel` verdict,
**I want** every panel skill to load the shared grounding + refute protocol,
**so that** "a panel reviewed it" means the same thing regardless of which panel ran.

**Acceptance Criteria:**
- [ ] AC-1: All 7 listed skills load `PANEL_PROTOCOL.md` and `PANEL_CORE.md`, matching the
  Load-Protocol step used by the existing 10.
- [ ] AC-2: `sh-claude-code-panel`'s copied Verbosity block is replaced by a load of
  `PANEL_CORE.md` — no verbatim duplicates of shared blocks remain.
- [ ] AC-3: A check asserts every `sh-*-panel/SKILL.md` references the shared protocol;
  it fails red before the fix. Coordinate with US-AF-03 AC-5 — whichever lands second
  adopts the other's propagation check rather than adding a second one.

**Size:** S · **Tags:** `[agentflow]` `[panels]` `[protocol]` `[quality]` `[debt]`

## Ready

- **Code-Level Quality Gate Augmentation** → DONE (2026-03-09) `[governance]` `[quality]` · **S** _(project: Governance)_ — Adopt two high-leverage quality patterns from [ryanthedev/code-foundations](https://github.com/ryanthedev/code-foundations) (MIT, v4.0) to add code-level enforcement where DOR/DOD currently operate only at process level. Business panel (5/5 consensus) + spec-panel (pass 1: 2.9/10 → pass 2: 7.6/10) shaped scope.
  - **Source:** *Code Complete* assessment framework (Fix/Investigate/Plan/Decide taxonomy + uncertainty declaration)
  - **Excluded (business panel unanimous):** 614-check rubric, slash commands, model auto-selection, feature branch enforcement, debugging workflow
  - **Risk:** R-LOW — pure documentation change, no runtime dependency. KNOWN_PATTERNS.md is LLM-read only (no programmatic parser).
  - **Rollback:** If FIPD adoption causes friction after 2 sprints, revert to severity-only and log findings in retro.
  - **User Stories:**
    - **US-QG-01:** As a governance consumer, I want every finding classified by action type (Fix/Investigate/Plan/Decide) so that I know what to do next without re-analyzing the issue.
      - **AC-1:** Given KNOWN_PATTERNS.md, when I read any row, then it has an "Action" column with exactly one value from {Fix, Investigate, Plan, Decide}.
      - **AC-2:** Given a new finding from `/sc:analyze` or quality audit, when the finding is reported, then it is prefixed with its FIPD action type (FIPD *replaces* severity as the primary classifier; severity may remain as metadata but is not the leading label).
      - **AC-3:** Given DOD.md, when I read the quality audit enforcement step, then it references the FIPD taxonomy and links to the definitions.
      - **AC-4:** Given the 10 existing KNOWN_PATTERNS rows, when the migration is complete, then all 10 rows have been backfilled with the correct action classification.
      - **FIPD definitions:**
        - **Fix:** Root cause known, solution clear — implement immediately
        - **Investigate:** Symptom observed, root cause unknown — gather data before acting
        - **Plan:** Issue understood, solution *direction* is known but requires design work — add to backlog
        - **Decide:** Trade-off identified, multiple valid directions exist requiring human judgment — escalate to decision-maker
    - **US-QG-02:** As a reviewer, I want every analysis finding to declare what remains unknown or unverified so that I don't act on false confidence.
      - **AC-1:** Given KNOWN_PATTERNS.md, when I read the patterns list, then there is a meta-pattern row stating: "All review/analysis findings must declare what remains unknown or unverified."
      - **AC-2:** Given a finding output, when the action type is Investigate or Decide, then an `Unknown:` clause is mandatory.
      - **AC-3:** Given a finding output, when the action type is Fix or Plan, then an `Unknown:` clause is recommended but optional.
      - **AC-4:** Given an agent that reads the updated KNOWN_PATTERNS, when it classifies a new hypothetical finding, then it produces output matching the FIPD + uncertainty format. Pass criterion: output contains (a) one FIPD prefix, (b) `Unknown:` clause when action is Investigate or Decide, (c) valid sentence structure. No golden answer match required.
  - **Deliverables:** (1) KNOWN_PATTERNS.md schema change + backfill, (2) uncertainty meta-pattern row, (3) DOD.md finding format reference
  - **Test strategy:** Agent acceptance test — read updated KNOWN_PATTERNS, classify a novel finding, verify FIPD + uncertainty output format
  - **Dependencies:** None
  - **Before/After examples:**
    - KNOWN_PATTERNS row — Before: `| 2 | Catching bare Exception | Catch specific exceptions | SVG-PAINT |` → After: `| 2 | Catching bare Exception | Catch specific exceptions | SVG-PAINT | Fix |`
    - Finding output (Fix) — Before: `⚠️ MEDIUM: Unguarded setattr loop in config_service.py:45` → After: `Fix: Unguarded setattr loop in config_service.py:45 · Unknown: whether current PERSISTED_FIELDS whitelist covers all callers`
    - Finding output (Investigate) — `Investigate: Intermittent 500 on /api/collections endpoint · Unknown: whether caused by connection pool exhaustion or upstream timeout`
  - **Spec-panel:** pass 1: 2.9/10 → pass 2: **7.6/10** (gate passed)

- **PO Capabilities: 8 functions** (refining 2026-03-01) · **L** _(project: Governance)_
  - Spec: [requirements/REQ_PO_CAPABILITIES.md](requirements/REQ_PO_CAPABILITIES.md)
  - 8 capabilities: Prioritization, Critical Path, Dependencies, Backlog Review, Planning Rounds, Risk Calendar, Retros, Release Bundling
  - 15 User Stories (US-P-01/02, US-CP-01/02, US-D-01/02, US-BR-01/02, US-SPR-01/02/03, US-R-01/02, US-RT-01/02, US-RB-01/02)
  - 5 open questions: **all resolved** (see spec §Open Questions — Resolved)
  - Spec-panel pass 1: **6.4/10** → 16 improvements applied (precedence rule, Done def, RACI, flag severity, parsing grammar, validation, integrated example, cross-project deps, 150-line rule, planning interactive gates, retro quality bar)
  - **Missing before Ready:** `/sc:spec-panel` re-score >= 7.0, user sign-off on BACKLOG.md format changes

## Critical Path

US-AF-01 and US-AF-02 are independent (no shared dependency) — both are memory-registration/extraction fixes, not blocking each other or downstream work.
