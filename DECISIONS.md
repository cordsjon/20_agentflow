<!-- AI-maintained, append-only -->


## Q1 — shepherd-v2/spec-rev2 — deviation

**Question:** US-SH2-01 deletes DOD.md while US-SH2-03 (ordered after it) rewrites its queue tail — which story owns the queue-tail rewrite?
**Chosen:** US-SH2-01 writes the new DOD section (queue tail included) into DOCTRINE.md; US-SH2-03 keeps only the executable half (hook list + positive control). Order 01 -> 03 unchanged.
**Decided-by:** agent
**Justification:** Codex pre-panel finding C1 in docs/specs/2026-09-26-shepherd-v2-audit-design.md (Duo review round 1): following rev-1 order left US-03 without a target. Folding is the smallest change that keeps AC-1 (0 sc: hits) satisfiable after US-01.
**Outcome:** applied
**Ref:** ff80046 (at write time)


## Q2 — shepherd-v2/spec-rev2 — tradeoff

**Question:** FIPD table is defined only in agentflow KNOWN_PATTERNS.md:9-17 while the spec says rules live in Governance — where does the single authoritative copy go?
**Chosen:** Move the FIPD table + Unknown rule into 00_Governance/KNOWN_PATTERNS.md as a new entry; agentflow DOCTRINE.md links to it (US-SH2-01 AC-2).
**Decided-by:** agent
**Justification:** Design principle "one source per rule, rules live in Governance"; Governance KP uses FIPD 10x (e.g. KP-806) without defining it, so this fills a gap rather than duplicating. Cross-project write, so the operator may prefer agentflow-owned; cheap to reverse before US-SH2-01 runs.
**Outcome:** assumed
**Ref:** ff80046 (at write time)


## Q3 — shepherd-v2/spec-rev2 — tradeoff

**Question:** agentflow:dor has 105 invocations / 90 days and three named callers — retire the namespace outright or keep compatibility aliases?
**Chosen:** Delete the 9 unused agentflow:* commands; keep dor.md and dod.md as two-line aliases to /sh:dor and /sh:dod until backlog_dor_pipeline.py:494, goal.md:68/79 and mission.md:145 are migrated in the same story, then delete the aliases (US-SH2-04 AC-3).
**Decided-by:** agent
**Justification:** Observation log ~/.local/state/claude-observations 2026-06-28..09-26 and grep of ~/.claude, 00_Governance/scripts, 20_agentflow/.claude; Codex finding C7 asked for a consumer dependency. Least-surprising path: nothing breaks between the two steps. Still subject to operator Decide-1.
**Outcome:** assumed
**Ref:** ff80046 (at write time)


## Q4 — shepherd-v2/spec-rev2 — gate-resolution

**Question:** US-SH2-05 (panel usage measurement) was listed NOT DONE in the handover — run it inline during spec revision or leave it as a story?
**Chosen:** Ran it inline (40-line stdlib script over the observation jsonl) and recorded the table + coverage caveats in the spec; the story keeps only its Plan tail (subagent-coverage check).
**Decided-by:** agent
**Justification:** Spec rev 1 sized US-SH2-05 at <= 2 h and 'anytime'; reviewers D6 and C9 both needed the log location and coverage to judge the retirement rule, so the measurement was a prerequisite for the panel, not extra scope.
**Outcome:** applied
**Ref:** ff80046 (at write time)
