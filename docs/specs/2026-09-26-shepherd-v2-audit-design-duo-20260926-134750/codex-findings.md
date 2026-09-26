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
