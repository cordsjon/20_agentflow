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

**Acceptance Criteria:**
- [ ] AC-1: `PANEL_PROTOCOL.md` gains an **External-Contract Conformance** stage: when the
  reviewed artifact names an external spec/protocol it implements (ARD, MCP, A2A, OAuth,
  …), the panel MUST retrieve the authoritative spec text (curl/WebFetch, cached to the
  session scratchpad), enumerate the MUST/SHALL clauses the design touches, and verify
  each. A disclosed-but-unresolved MUST violation is a CRITICAL finding — an author risk
  note never downgrades it (kills root causes 1+2).
- [ ] AC-2: Protocol gains a **Consumer dry-run** rule: any artifact the design emits for a
  named consumer (CLI command, config snippet, API payload) is checked against that
  consumer's actual contract (its docs, config schema, or source when local) with the
  question "does this run/connect as generated?" — cross-linking
  feedback_verify_contract_against_consumer (kills root cause 3).
- [ ] AC-3: `PANEL_CORE.md` Auto-Fix Policy gains a **fix re-gate**: after applying fixes,
  one adversarial refute pass runs over the fix diff (codex where available, self-refute
  otherwise) BEFORE commit; findings against the fixes are fixed and re-gated once (kills
  root cause 4). Sync note honored — PANEL_CORE.md and PANEL_PROTOCOL.md updated together.
- [ ] AC-4 (regression fixture, falsifiable): running the upgraded spec-panel against the
  pre-codex ARD spec revision (`a2a-cli-registry` commit `c481ddd`) catches at least 2 of
  the 3 codex CRITICALs (ARD §3.4 url-vs-endpoint, missing bearer in emits, https→http
  downgrade) WITHOUT codex assistance — verified red-first by confirming the current
  protocol misses all 3 on the same fixture.

**Size:** M · **Tags:** `[agentflow]` `[panels]` `[protocol]` `[quality]`

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
