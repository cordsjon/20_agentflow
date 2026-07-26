# Panel protocol — external-contract conformance + auto-fix re-gate

**Story:** US-AF-03 · **Size:** L · **Status:** Refining
**Date:** 2026-07-26 · **Tags:** `[agentflow]` `[panels]` `[protocol]` `[quality]`
**Revision:** 2 — full rewrite after `CODEX-VERDICT: 3.1` on rev 1 (10 findings, all addressed; see §8).

> **Authoring rules in force** (`00_Governance/docs/reviews/2026-07-15-consolidation-spec-postmortem.md` §6):
> measure first; cite the line that answers the question; `[verified]` requires the command;
> retraction requires a grep sweep; default to `[inference]`; smaller is stronger; no self-scoring.

## 1. Problem

ARD fleet-discovery spec review (`a2a-cli-registry`, 2026-07-26). Two panels passed a spec
that codex then scored 3–4/10 with three CRITICALs.

[verified 2026-07-26: `git log --oneline 10fdc40..61b0ed9`]

| Commit | Role |
|---|---|
| `10fdc40` | ARD fleet discovery design spec — draft |
| `c944241` | ai-panel fixes (panel score 8.4) |
| `c481ddd` | spec-panel fixes (panel score 8.6) — **AC-4 fixture** |
| `61b0ed9` | codex-gate fixes (codex 3–4/10) |

### 1.1 What the evidence supports, and what it does not

Rev 1 tagged all four root causes `[verified]`. Codex finding 6 refuted that. Corrected
tags:

**RC-1 — Grounding has no retrieval step. [verified]**
`PANEL_PROTOCOL.md:5-10` grounds claims in repo source or the reviewed document and closes
with *"No new indexing dependency. Serena + Read only."* There is no fetch verb in the
26-line file. **What this shows:** the protocol never instructs retrieval. **What it does
not show:** that a panel was *unable* to retrieve. Rev 1 claimed "no panel could retrieve";
that is `[inference]` and is now dropped as an argument.

**RC-2 — A disclosed defect passed two panels. [verified as omission, not as motive]**
`c481ddd` lines 330-334 (Risk 2) disclose the exact defect codex later flagged. Both panels
passed the spec. **What this shows:** disclosure did not prevent a pass. Rev 1 said panels
"treated the hedge as mitigation" — motive attribution, unsupported by their outputs.
Retracted.

**RC-3 — An emitted artifact contradicts the document's own claims. [verified]**
Line 134 emits `claude mcp add --transport http cli-registry <url>` with no auth field;
lines 66 and 143 state that endpoint is bearer-gated. **Citation correction (codex finding
6):** lines 66/143 establish *bearer gating*; they do not establish a 401. The 401 comes
from the implementation at `core/mcp/http.py:48`. The internal contradiction is what a
panel can see for free; the 401 is the consequence, provable only against the consumer.
Rev 1 cited 66/143 for the 401 — a right conclusion with a wrong citation, which the
postmortem's KP list calls *"indistinguishable from a fabrication."*

**RC-4 — A fix commit introduced a defect no later pass reviewed as a fix. [verified,
narrowed]**
[verified 2026-07-26: `git log -S "Path/scheme differences" --oneline`] → the phrase enters
at `c944241` (ai-panel's own fix commit); absent from draft `10fdc40`. Rev 1 said "no pass
ever reviewed the fixes" — **false**, and codex was right: spec-panel ran on `c944241`,
which already contained the ai-panel fixes, and produced `c481ddd`. The accurate claim is
narrower: **no stage re-gated the fixes as fixes.** A subsequent panel reviewing the whole
document is not an adversarial pass over the fix diff, and it did not catch the introduced
hole.

**Structural note. [inference]** Panels are personas inside one model context and plausibly
inherit its blind spots. Offered as motivation, not as proven mechanism.

### 1.2 Prior art — and the correction rev 1 missed

Rev 1 quoted `codex_refute.py`'s docstring ("PANEL_PROTOCOL names `codex exec` … ships no
wrapper … that skip is the root of the entire failure chain") as its design foundation.

**That conclusion is retracted at its source.** The postmortem's rule 7 carries it struck
through — `~~That skip is the root of the entire chain.~~ **Falsified — see §8**` — and §8
is titled *"the root cause named above is too generous."* Its finding:

> **Codex used zero information I lacked.** Every disproving fact was already in my
> context, most of it printed by my own commands.

The external reader is a **backstop, not the mechanism.** The actual failure was stopping
at confirming evidence.

**Consequence for this design.** Rev 1's organizing principle — "every stage ships a
callable, because prose gets skipped" — rested on the falsified claim and is **withdrawn**.
A callable does not fix a reviewer who stops at confirming evidence. What the corrected
postmortem supports is narrower and is what §3 now builds on: *an independent reader that
does not share the author's context is a backstop worth having, and it must be reached by
default rather than at the reviewer's discretion.*

## 2. Blast radius

[verified 2026-07-26: `grep -rl PANEL_PROTOCOL ~/.claude/skills --include=SKILL.md | wc -l`
→ 10; `grep -rl PANEL_CORE … | wc -l` → 9; `ls -d ~/.claude/skills/sh-*panel*/ | wc -l` → 17;
`comm -13` protocol-set core-set → empty, so core-loaders ⊂ protocol-loaders]

| Surface | Count |
|---|---|
| `PANEL_PROTOCOL.md` | 1 |
| `PANEL_CORE.md` | 1 |
| `00_Governance/CLAUDE.md §8` (line 112) | 1 |
| `sh-*-panel/SKILL.md` loading the protocol | 10 |
| **In scope** | **13** |
| Panel skills loading neither (see §2.1) | 7 |
| **Total panel skills** | **17** |

**Why the 10 skills matter.** Each names the sections it applies, e.g.
`sh-spec-panel/SKILL.md:20`: *"apply its **Grounding and Refute Stage** sections."* That is
a named-section allowlist: appending a stage to `PANEL_PROTOCOL.md` leaves it **inert**.
`sh-business-panel` loads the protocol but not the core.

### 2.1 Adjacent, out of scope
7 panels reference neither file (`sh-4-reviewer-panel`, `sh-claude-code-panel`,
`sh-content-panel`, `sh-devops-panel`, `sh-legal-panel`, `sh-marketing-panel`,
`sh-visualization-panel`). Filed as **US-AF-04**. `sh-claude-code-panel:30` holds a verbatim
copy of the Verbosity block instead of loading the shared file.

## 3. Functional requirements

**Enforceability is stated per requirement.** Rev 1 promised all stages ship callables and
then admitted two were prose — a contradiction inside one document (codex finding 2). The
honest split:

| FR | Mechanism | Enforceable by code? |
|---|---|---|
| FR-1 | protocol prose + fetch helper | **No** — model-followed |
| FR-2 | protocol prose | **No** — model-followed |
| FR-3 | `panel_regate.py` wrapper | **Yes** |
| FR-4 | propagation + `test_panel_propagation.py` | **Yes** (presence only) |

FR-1/FR-2 are instructions a model may skip. AC-4 is the only evidence they fire. This is
the design's central weakness and is stated, not hidden — see Risk 4.

### FR-1 — External-Contract Conformance stage
When the reviewed artifact names an external spec it implements, the panel MUST retrieve
the authoritative spec text, enumerate the normative clauses the design touches, and verify
each. A disclosed-but-unresolved violation is CRITICAL; an author risk note never downgrades
it.

**Constraint amendment.** `PANEL_PROTOCOL.md:10` ("No new indexing dependency. Serena +
Read only.") is superseded by a scoped exception: `curl`/`WebFetch` permitted **for external
spec documents only**. The no-new-*indexing*-dependency rule stands.

**Retrieval resilience (codex finding 8).** The stage MUST specify:
- **Source precedence:** the spec's own canonical URL; a repo-vendored copy only if it
  records source URL + retrieval date.
- **Pinning:** fetch a tag/commit URL where one exists, never a mutable branch. Record the
  resolved URL **and the sha256 of the fetched bytes** in the finding.
- **Cache:** session scratchpad, keyed by sha256; one fetch per spec per panel run.
- **Failure = fail-closed:** unreachable, redirected off-host, or non-2xx → emit
  `EXTERNAL-SPEC-UNAVAILABLE` and **do not** score conformance as passing. Silence is not
  compliance.

**Worked example — and a correction to the story's own claim.**
[verified 2026-07-26: `curl -sL https://raw.githubusercontent.com/ards-project/ard-spec/main/spec/ard.md`
→ 41163 bytes; `sed -n '47,53p'`]

ARD §3.4 *Strict Value-or-Reference* reads: *"a catalog entry must contain exactly one of
two mutually exclusive keys … **url**: A remote reference to the artifact document."* The
normative MUST is at §4.2: *"Exactly one of the following MUST be present"* — which the ARD
spec **satisfies** (it has `url`, not both).

So the story's framing of a §3.4 "MUST-violation" is **too strong**. The real §3.4 defect is
a *semantic* mismatch: `url` is defined as a reference to the artifact **document**, and the
spec points it at a live `/mcp` protocol endpoint. Still a genuine finding, correctly
CRITICAL under FR-1's "disclosed ≠ resolved" rule (its Risk 2 disclosed it) — but it is a
type/semantics violation, not a cardinality MUST violation.

Fetching also surfaced a **harder violation the story never cited**: §4.2.1 requires
`identifier` to use a domain-anchored URN where `<publisher>` is *a verifiable domain name*.
The spec uses `urn:air:a2a-cli-registry:…` — a project name — and its Risk 4 disclosed it as
*"Fine for self-hosted/tailnet use."* That is a clean MUST violation.

This example is the requirement's own justification: one 25-second fetch corrected one claim
and added a stronger one.

### FR-2 — Consumer dry-run
Any artifact the design emits for a named consumer is checked against that consumer's
contract, asking *"does this run/connect as generated?"* Cross-links
`feedback_verify_contract_against_consumer`.

- **Tier 1 (always):** the emit must not contradict the reviewed document's own claims about
  the endpoint it targets. Contradiction is CRITICAL. Catches the ARD case for free.
- **Tier 2 (mandatory when a real contract is reachable — codex finding 9):** fetch the
  consumer's actual contract. Rev 1 made Tier 2 conditional on Tier 1 being inconclusive,
  which let a **confidently-wrong-but-internally-consistent** document skip it entirely —
  defeating the requirement's purpose. Tier 2 is skipped **only** when no contract is
  reachable (no local source, no published schema), and that skip is reported as
  `CONSUMER-CONTRACT-UNVERIFIED`, never as a pass.

### FR-3 — Auto-fix re-gate
After applying fixes, one adversarial pass runs over the **fix diff** before commit, then
findings against the fixes are fixed and re-gated once.

**Mechanism — new wrapper `scripts/panel_regate.py`** (codex finding 2: `codex_refute.py`
alone does not do this — it reviews a single path and records a path-keyed score; it neither
captures a diff, nor re-invokes itself after edits, nor applies findings). The wrapper:
1. captures the fix diff across all touched repos (`git diff` per repo, concatenated);
2. writes it to a temp artifact and calls `codex_refute.py` on **that**;
3. applies surviving findings, re-gates **once**;
4. enforces the stop bound and exits non-zero on trip.

**Stop bound — corrected semantics (codex finding 7).** Rev 1 described the gate as
detecting "author-introduced defects in two consecutive rounds." The implementation at
`codex_refute.py:126` (`consecutive_fails(rows, gate)`) counts **any two consecutive
sub-gate scores**; it does not classify findings as author-introduced and does not verify a
fix round occurred. FR-3 therefore specifies the *behavioral* bound it actually gets: **two
consecutive sub-gate verdicts halt the loop and escalate to the operator.** Whether the
defects were author-introduced is a human judgment at escalation, not a machine test.

### FR-4 — Propagation
FR-1..FR-3 reach all **13** in-scope surfaces (§2). The **10** protocol-loading SKILL.md
Load-Protocol lines are rewritten to apply the protocol **wholesale** rather than an
enumerated allowlist — so the next protocol addition needs no 10-file edit.
`00_Governance/CLAUDE.md §8` (line 112) is updated in the same change; it is the canonical
source `PANEL_CORE.md` cites twice.

## 4. Test strategy

**Harness.** `parse_panel_verdict()` (`00_Governance/scripts/quality_gate.py:283`) is reused
as the verdict reader [verified: last-line-wins, fail-closed `panel_no_verdict` on absence].
`scripts/panel_regression.sh` follows the `claude -p --output-format json` pattern of
`scripts/measure-panel-vs-analyze.sh`.

**Fixture.** `a2a-cli-registry` `c481ddde9b1bcbc2437ce2e73adf1c748be46074` [verified on
`master`], file `docs/superpowers/specs/2026-07-26-ard-fleet-discovery-design.md`.

**Isolation — mandatory (codex finding 3).** Rev 1's AC-4 claimed detection "without codex
assistance" while FR-3 required the panel to invoke codex, with no mode preventing
contamination. The harness therefore runs the panel with **`PANEL_REGATE=0`**, which
disables FR-3 for the run. A regression run that observes any codex invocation is **void**,
not a pass. `panel_regression.sh` asserts this by failing if the codex-refute ledger gains a
round during the run.

**Detection scoring (codex finding 4).** Signatures are semantic, not line-anchored — a
correct finding cited at an equivalent range must count:

| # | Signature | Matches when the finding names… |
|---|---|---|
| 1 | url-vs-endpoint | the MCP entry's `url` **and** (`server-card`/`type`/artifact-document semantics) |
| 2 | missing auth in emit | the emitted `claude mcp add` command **and** (bearer/auth/401) |
| 3 | scheme downgrade | same-host acceptance **and** (scheme/https/http downgrade) |

Each is a documented regex over the finding text, stored beside the fixture and unit-tested
against a canned findings blob (both a matching and a near-miss case). Line anchors are
**advisory context only** and never gate a match.

**Statistical rule (codex finding 4).** Rev 1 required the stochastic baseline to produce
"exactly median 0" — an observation, not a test. Corrected:
- **Green:** N=5 `--model`-pinned runs on the upgraded protocol; **≥4 of 5 runs** score ≥2
  signatures. (N=5 with a 4/5 floor, not N=3, so one stochastic miss does not flip the gate.)
- **Red:** the same 5 runs on the **current** protocol; **≥4 of 5** score **0**. Committed to
  `tests/fixtures/` as evidence before the green test is accepted.
- If red and green overlap (any current-protocol run scores ≥2), the test is **inconclusive**
  and the signature set is revised — a pass is not claimed from a noisy separation.

**Coverage beyond AC-4 (codex finding 4).** Unit tests for: signature matcher (match +
near-miss); `EXTERNAL-SPEC-UNAVAILABLE` on fetch failure; `CONSUMER-CONTRACT-UNVERIFIED` on
unreachable consumer; `panel_regate.py` stop-bound trip at two; self-refute fallback when
codex is absent; propagation presence-check across all 13 surfaces.

**Presence ≠ behavior (codex finding 4).** The propagation test asserts only that the
surfaces reference the new stages. It is a necessary, not sufficient, check; behavioral
evidence comes solely from AC-4. Stated so no reader mistakes a green propagation test for a
working protocol.

## 5. Cost (codex finding 10)

[inference — not measured; `measure-panel-vs-analyze.sh` exists to measure it and has not
been run for this shape]

| Item | Count |
|---|---|
| Green runs | 5 `claude -p` panel invocations |
| Red runs | 5 `claude -p` panel invocations |
| **Regression total** | **10 per full acceptance**, not 3 |
| Production per-panel-run | +1 external fetch (cached per spec), +1 `codex_refute` call when FR-3 fires |

Controls: regression is on-demand only (never pre-commit); external fetches cached by
sha256 for the session; `panel_regate.py` inherits `codex_refute.py`'s 900s timeout and its
stop bound caps codex calls at 2 per panel run. **Before AC-4 is accepted, one measured run
of `measure-panel-vs-analyze.sh` replaces this estimate with numbers** — per tenet "never
fabricate metrics."

## 6. Dependencies

| Dependency | Status |
|---|---|
| Fixture `c481ddd` on `master` | ✅ verified |
| `codex_refute.py` | ✅ exists (wrapped by FR-3, not used directly) |
| `parse_panel_verdict()` | ✅ `quality_gate.py:283` |
| `measure-panel-vs-analyze.sh` | ✅ exists |
| `feedback_verify_contract_against_consumer` | ✅ exists |
| `00_Governance/CLAUDE.md §8` | ✅ line 112 |
| `scripts/panel_regate.py` | ⬜ **to build** (FR-3) |
| `PANEL_REGATE=0` isolation switch | ⬜ **to build** (test isolation) |
| Red-first evidence committed | ⬜ blocks AC-4 |
| Measured cost run | ⬜ blocks AC-4 |

## 7. Risks

1. **FR-1/FR-2 are unenforced prose.** A model may skip them exactly as `codex exec` was
   skipped. AC-4 is the only evidence they fire; if it proves flaky, per-stage callables are
   the v2 escalation. **This is the design's central weakness, not a footnote.**
2. **External specs are mutable.** Pinning + sha256 recording (FR-1) bounds drift; an
   unpinnable spec means conformance findings carry the retrieval date and are re-verified
   on the next run.
3. **Stochastic separation may not hold.** If red and green overlap, the test is
   inconclusive by construction rather than passing on noise (§4).
4. **Cost is estimated, not measured** — §5 blocks acceptance on a real measurement.
5. **Wholesale protocol loading widens per-panel input tokens** in exchange for removing the
   10-file edit per protocol change. Accepted.

## 8. Gate

**Not `sh:spec-panel`** — it scored 8.6 on the defective ARD spec; scoring its own repair is
circular (AC-6).

**Rev 1: `CODEX-VERDICT: 3.1` — FAIL** (gate 7.0). Ten findings. Disposition:

| # | Finding | Disposition |
|---|---|---|
| 1 | Founded on a retracted root cause | **Accepted** — §1.2 rewritten, "ships a callable" principle withdrawn |
| 2 | "Every stage ships a callable" false | **Accepted** — §3 enforceability table; FR-3 gets a real wrapper |
| 3 | AC-4 cannot exclude codex | **Accepted** — `PANEL_REGATE=0`, void-run rule |
| 4 | Detectors structurally weak | **Accepted** — semantic signatures, N=5/4-of-5, red-green separation, 6 new unit tests |
| 5 | Count correction unswept | **Accepted** — 5 stale hits (133/134/136/181/227) fixed; sweep re-run |
| 6 | Root causes are inference or false | **Accepted** — §1.1 retags; "no pass reviewed the fixes" was **false**, narrowed |
| 7 | Stop-at-two semantics don't exist | **Accepted** — FR-3 states the behavioral bound the code implements |
| 8 | External-contract resilience unspecified | **Accepted** — precedence/pinning/sha256/cache/fail-closed; ARD §3.4 claim corrected, §4.2.1 added |
| 9 | Tier 2 preserves self-grounding | **Accepted** — Tier 2 mandatory when a contract is reachable |
| 10 | Cost model incomplete | **Accepted** — §5, 10 invocations, measurement blocks acceptance |

**Stop bound: 1 consecutive sub-gate round.** A second failing verdict trips
`codex_refute.py`'s stop-at-two and the correct response is reassessing the story's shape,
not a third patch.

**Rev 2 gate result:** _pending._
