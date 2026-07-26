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

> **SPLIT 2026-07-26 after two failed codex gates (3.1 → 3.0, stop-at-two TRIPPED).**
> The mechanically-verifiable half shipped as **US-AF-05** (Ready/DONE). What remains here
> is the half two independent reviews found structurally unsound. **Do not start a third
> fix round on the old spec** — `codex_refute.py` will refuse without `--force`, and the
> 2026-07-15 precedent (4.2→4.1→3.0) is what that guard exists to stop.
>
> **Refinement conditions — each must be ANSWERED IN DESIGN, not patched in prose,
> before this is re-gated.** All are verified findings from codex round 2:
> 1. **Codex isolation is unsolved.** `PANEL_REGATE=0` does not isolate: `PANEL_PROTOCOL.md:16`
>    independently tells panels to use `codex exec`. Ledger-watching cannot see direct
>    invocations, no-row failures (timeout/no-verdict), or other ledger keys. Until this is
>    solved, AC-4 cannot prove detection "without codex".
> 2. **Fix-diff capture is unsolved.** `git diff` misses untracked + staged files —
>    demonstrated on this very spec (`git diff → 0 bytes` while untracked). New files are the
>    highest-risk fix surface. Needs a real design: repo discovery, provenance, and how
>    unstructured findings get applied.
> 3. **Detector polarity.** The "semantic signatures" match negated statements ("the command
>    correctly includes bearer auth"). No finding-extractor is specified, so matching quoted
>    source can manufacture hits.
> 4. **Run independence.** Panels auto-fix, so run 1 mutates the fixture for runs 2-5; no
>    worktree reset is specified. And 4-of-5 clears 18.75% of the time for a 50%-accurate
>    detector — the statistical rule does not carry the weight placed on it.
> 5. **FR-2 performs no dry-run.** It requires READING a contract, never executing/parsing
>    the emit against the consumer. Title and mechanism disagree.
> 6. **Acceptance taxonomy missing.** `CRITICAL`, `EXTERNAL-SPEC-UNAVAILABLE`,
>    `CONSUMER-CONTRACT-UNVERIFIED` have no mapping to the numeric panel gate — a panel can
>    score >7 while emitting them. Also: `codex_refute.py` REJECTS self-review substitution,
>    so the "self-refute fallback" has no implementation.
> 7. **Open question the split exposes:** FR-1/FR-2 are model-followed prose with no code
>    enforcement. Their only evidence would come from a regression test that conditions 1-4
>    show is currently unsound. **Decide whether they are viable at all before re-speccing** —
>    shelving them is a legitimate outcome.
>
> Spec `docs/specs/2026-07-26-panel-protocol-external-conformance-design.md` (rev 2) is
> retained as the evidence record, NOT as an approved design. Its §1.1/§1.2 corrections and
> §2 counts survived review; its §3-§5 mechanisms did not.

> Origin: ARD fleet-discovery spec review (a2a-cli-registry, 2026-07-26). Two panels
> (ai-panel 8.4, spec-panel 8.6) passed a spec that codex then scored 3-4/10 with three
> CRITICALs. Post-mortem found four protocol-level root causes (all verified, not guessed):
>
> _Root-cause tags corrected after `CODEX-VERDICT: 3.1` on spec rev 1 refuted several as
> inference-or-false. Rev 2 tags below are the surviving claims._
>
> 1. **Grounding has no retrieval step.** [verified] `PANEL_PROTOCOL.md:5-10` resolves
>    claims in repo source or the reviewed document and ends "Serena + Read only" — there is
>    no fetch verb in the 26-line file. Shows the protocol never INSTRUCTS retrieval; does
>    NOT show a panel was unable to (rev 1's "structurally could not" is retracted).
> 2. **A disclosed defect passed two panels.** [verified as omission, NOT motive] Risk 2 at
>    `c481ddd:330-334` disclosed the url-vs-endpoint tension; both panels passed. Rev 1's
>    "both panels treated the hedge as mitigation" is motive attribution their outputs do not
>    support — retracted.
> 3. **An emit contradicts the document's own claims.** [verified] Line 134 emits an
>    unauthenticated `claude mcp add` while lines 66/143 call the endpoint bearer-gated.
>    Citation correction: 66/143 establish GATING; the 401 comes from `core/mcp/http.py:48`
>    — rev 1 cited the wrong line for the right conclusion.
> 4. **A fix commit introduced a defect never re-gated as a fix.** [verified, narrowed]
>    `git log -S "Path/scheme differences"` dates the hole to `c944241`, the ai-panel's own
>    fix commit; absent from draft `10fdc40`. Rev 1's "no pass ever reviewed the fixes" is
>    **FALSE** — spec-panel ran on `c944241` and produced `c481ddd`. The true gap: no stage
>    re-gated the fixes AS fixes.
> 5. **Panels inherit one model context's blind spots.** [inference] Motivation, not proven
>    mechanism. Rev 1's derived principle "the remedy must be deterministic protocol steps /
>    every stage ships a callable" is WITHDRAWN — it rested on a conclusion its own source
>    (`2026-07-15-consolidation-spec-postmortem.md` §8) had already falsified: *"Codex used
>    zero information I lacked."* The external reader is a backstop, not the mechanism.

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
  **Retrieval resilience (required, else the stage is not reproducible):** source precedence
  (canonical URL > vendored copy carrying source URL + retrieval date); pin to a tag/commit
  URL never a mutable branch; record resolved URL + sha256 of fetched bytes in the finding;
  cache in session scratchpad keyed by sha256, one fetch per spec per run; **fail-closed** —
  unreachable / off-host redirect / non-2xx emits `EXTERNAL-SPEC-UNAVAILABLE` and MUST NOT
  score conformance as passing.
  _Note: fetching ARD showed the story's "§3.4 MUST-violation" framing was too strong — the
  normative MUST is §4.2 and it is satisfied; §3.4 is a semantic mismatch (url = reference
  to the artifact document, pointed at a live endpoint). The same fetch surfaced a harder,
  uncited violation: §4.2.1 requires a verifiable-domain publisher, and the spec uses a
  project name. Both are still CRITICAL under "disclosed ≠ resolved"._
- [ ] AC-2: Protocol gains a **Consumer dry-run** rule: any artifact the design emits for a
  named consumer (CLI command, config snippet, API payload) is checked against that
  consumer's actual contract (its docs, config schema, or source when local) with the
  question "does this run/connect as generated?" — cross-linking
  feedback_verify_contract_against_consumer (kills root cause 3).
  **Two tiers:** Tier 1 (always, zero-fetch) — an emit that contradicts the reviewed
  document's OWN claims about the endpoint it targets is CRITICAL (line 134 emits
  unauthenticated vs lines 66/143 "bearer auth"). Tier 2 (**mandatory whenever a real
  contract is reachable**) — fetch the consumer's actual contract; skipped ONLY when none is
  reachable, and that skip reports `CONSUMER-CONTRACT-UNVERIFIED`, never a pass. Rev 1 made
  Tier 2 conditional on Tier 1 being inconclusive, which let a confidently-wrong but
  internally-consistent document skip it entirely — defeating the requirement.
  _Citation correction: lines 66/143 establish bearer GATING; the 401 itself comes from
  `core/mcp/http.py:48`. Tier 1 sees the contradiction; only Tier 2 proves the 401._
- [ ] AC-3: `PANEL_CORE.md` Auto-Fix Policy gains a **fix re-gate**: after applying fixes,
  one adversarial refute pass runs over the fix diff BEFORE commit; findings against the
  fixes are fixed and re-gated once (kills root cause 4, narrowed — a later panel DID review
  `c944241`'s content; what never happened was re-gating the fixes AS fixes).
  **Mechanism — new `scripts/panel_regate.py`.** `codex_refute.py` alone does NOT do this:
  it reviews one path and records a path-keyed score, and never captures a diff, re-invokes
  itself after edits, or applies findings. The wrapper (1) captures the fix diff across all
  touched repos, (2) calls `codex_refute.py` on that artifact, (3) applies survivors and
  re-gates once, (4) enforces the stop bound, exiting non-zero on trip.
  **Loop bound — corrected to what the code implements:** `codex_refute.py:126`
  (`consecutive_fails`) counts ANY two consecutive sub-gate scores; it does NOT classify
  findings as author-introduced nor verify a fix round occurred. So the bound is: **two
  consecutive sub-gate verdicts halt the loop and escalate.** Whether defects were
  author-introduced is a human judgment at escalation, not a machine test.
- [ ] AC-4 (regression fixture, falsifiable): running the upgraded spec-panel against the
  pre-codex ARD spec revision (`a2a-cli-registry` commit `c481ddd`) catches at least 2 of
  the 3 codex CRITICALs (§3.4 url-vs-endpoint semantics, missing auth in emits, scheme
  downgrade) WITHOUT codex assistance.
  **Isolation (mandatory):** the run sets `PANEL_REGATE=0` to disable FR-3; a run that
  observes any codex invocation is VOID, not a pass — `panel_regression.sh` fails if the
  codex-refute ledger gains a round mid-run. Without this, FR-3's own codex call
  contaminates the detector and manufactures a pass.
  **Detection scoring:** signatures are SEMANTIC regexes over finding text (documented,
  stored beside the fixture, unit-tested on a match + near-miss pair); line anchors are
  advisory context and never gate a match.
  **Statistical rule:** N=5 `--model`-pinned runs. Green = ≥4 of 5 score ≥2 signatures.
  Red = ≥4 of 5 runs on the CURRENT protocol score 0, committed to `tests/fixtures/` before
  green is accepted. Any overlap (a current-protocol run scoring ≥2) makes the test
  INCONCLUSIVE and the signature set is revised — no pass claimed from noisy separation.
  Harness `scripts/panel_regression.sh` follows `scripts/measure-panel-vs-analyze.sh` and
  reuses `parse_panel_verdict()` from `00_Governance/scripts/quality_gate.py`.
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
- [x] AC-3: A check asserts every `sh-*-panel/SKILL.md` references the shared protocol;
  it fails red before the fix. **DONE via US-AF-05** — `tests/test_panel_propagation.py`
  provides it; the 6 remaining unwired skills are `xfail` entries in `KNOWN_UNWIRED`, and
  `test_known_unwired_list_is_accurate` forces the list to shrink as each is fixed.

_Scope reduced 7 → 6 by US-AF-05: `sh-claude-code-panel` was fixed (its verbatim Verbosity
copy now references PANEL_CORE), satisfying AC-2 for that skill. Remaining:
`sh-4-reviewer-panel`, `sh-content-panel`, `sh-devops-panel`, `sh-legal-panel`,
`sh-marketing-panel`, `sh-visualization-panel`. Each fix flips an xfail to XPASS._

**Size:** S · **Tags:** `[agentflow]` `[panels]` `[protocol]` `[quality]` `[debt]`

### US-AF-05: Panel protocol propagation — wholesale application + propagation test

> Split from US-AF-03 on 2026-07-26: the mechanically-verifiable half. Its counts
> (10 protocol loaders / 9 core loaders / 17 panel dirs / 7 unwired) were the ONLY claims
> in the US-AF-03 spec to survive both codex rounds unchallenged.
>
> Root cause: every `sh-*-panel/SKILL.md` named the protocol sections it applied
> ("apply its Grounding and Refute Stage sections") — a named-section ALLOWLIST, so any
> stage added to `PANEL_PROTOCOL.md` was inert in all 10 consumers.

**As a** maintainer of the shared panel protocol,
**I want** every panel skill to apply the protocol wholesale and a test to enforce it,
**so that** adding a protocol stage takes effect without a 10-file edit, and drift fails CI.

**Acceptance Criteria:**
- [x] AC-1: All 10 protocol-loading SKILL.md files apply the protocol IN FULL rather than
  enumerating sections. _Verified: 10 files rewritten; test `…apply_protocol_wholesale`
  passes for each._
- [x] AC-2: `sh-claude-code-panel`'s verbatim `PANEL_CORE` Verbosity copy replaced by a
  reference. `sh-business-panel`'s reworded block kept and labelled a deviation — permitted
  by PANEL_CORE's own header. _Verified: `test_no_verbatim_copies_of_shared_blocks` passes._
- [x] AC-3: Propagation test exists, was seen RED first, and is mutation-verified.
  _Verified: red = `11 failed, 13 passed, 7 xfailed`; green = `26 passed, 6 xfailed`;
  mutation (revert one skill to allowlist form) → `1 failed`, detector confirmed live._
- [x] AC-4: Denominator guarded — `test_panel_population_is_discovered` fails if the glob
  returns <15, so the parametrized tests can never pass vacuously.

**Status:** DONE 2026-07-26 · **Size:** S · **Tags:** `[agentflow]` `[panels]` `[protocol]`
**Not claimed:** presence ≠ behavior. These tests prove each skill READS the protocol; they
prove nothing about whether the model FOLLOWS it. That evidence was US-AF-03's job and
remains unbuilt. **Scope:** the live tree `~/.claude/skills` only — see US-AF-06.

### US-AF-06: Resolve the stale agentflow skill fork (18 divergent panel copies)

> Surfaced while shipping US-AF-05 (2026-07-26). `20_agentflow/.claude/skills/` holds 18
> `sh-*panel*` dirs that are a divergent fork of the live `~/.claude/skills` tree.
> [verified] 10 still carry the allowlist Load-Protocol form US-AF-05 removed; 11 of 18
> predate the `PANEL_CORE.md` extraction entirely (they inline Verbosity / Expert Loading /
> Auto-Fix instead of loading the shared core). Newest agentflow copy is dated Jun 26, i.e.
> the `_skills-migration-backup-2026-06-26` cutover.
>
> Risk: `sh:newskill` documents the sync direction as **agentflow → global**
> ("Sync all agentflow skills to global ~/.claude/"). If that ever runs, the stale fork
> overwrites the live tree and silently reverts US-AF-05 plus the whole PANEL_CORE
> extraction. Guarded for now by `test_agentflow_fork_is_not_silently_live`.

**As a** maintainer of the panel skills,
**I want** exactly one source of truth for `sh-*-panel` skills,
**so that** a routine sync cannot silently revert shipped protocol work.

**Acceptance Criteria:**
- [ ] AC-1: Decide and document the authoritative tree (evidence favors `~/.claude/skills`:
  it is what the harness loads and the only one post-PANEL_CORE).
- [ ] AC-2: The non-authoritative tree is deleted, or converted to symlinks, or explicitly
  marked archived — no third state where a sync could resurrect it.
- [ ] AC-3: `sh:newskill`'s documented direction is reconciled with the decision, so the
  command cannot re-introduce the fork.
- [ ] AC-4: `test_agentflow_fork_is_not_silently_live` is updated or removed to match the
  resolution, and the suite still passes.

**Size:** S · **Tags:** `[agentflow]` `[panels]` `[debt]` `[hazard]`

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
