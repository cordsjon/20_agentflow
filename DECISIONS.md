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


## Q5 — shepherd-v2/decide-1 — tradeoff

**Question:** Decide-1: which command prefix survives (sh: vs agentflow:), and are the 9 unused agentflow:* commands deleted outright or parked under docs/archive/?
**Options considered:** keep sh:, delete the 9 outright / keep sh:, park the 9 under docs/archive / keep agentflow:, retire sh: / keep both
**Chosen:** Keep sh:, retire agentflow:*, delete the 9 unused commands outright. dor.md and dod.md stay as two-line aliases to /sh:dor and /sh:dod until backlog_dor_pipeline.py:494, goal.md:68/79 and mission.md:145 are migrated in the same story (US-SH2-04 AC-3).
**Decided-by:** human
**Justification:** Operator chose option 1 in the /unblock walk on 2026-09-26. Git history preserves the deleted files; the alias-then-migrate step protects the two live callers; spec recommendation and both review rounds converged on it. Skill-sync DAG propagates the deletions to 13 projects at the next 06:00 run.
**Outcome:** applied
**Ref:** ba20e57


## Q6 — shepherd-v2/spec-rev2 — tradeoff

**Question:** agentflow:dor has 105 invocations / 90 days and three named callers — retire the namespace outright or keep compatibility aliases?
**Chosen:** Confirmed as assumed: delete the 9 unused agentflow:* commands, keep dor.md/dod.md as aliases until the three callers migrate, then delete the aliases.
**Decided-by:** human
**Justification:** Operator confirmed via Decide-1 option 1 (see Q5) in the /unblock walk on 2026-09-26.
**Outcome:** applied
**Ref:** ba20e57
**Supersedes:** Q3 — resolved


## Q7 — shepherd-v2/decide-2 — tradeoff

**Question:** Decide-2: does CLAUDE-LOOP.md get archived under docs/archive/ as a design record, or deleted?
**Options considered:** archive under docs/archive/ with a pointer header to dagu nightshift / delete outright
**Chosen:** Delete CLAUDE-LOOP.md outright; git history is the record.
**Decided-by:** human
**Justification:** Operator chose option 2 in the /unblock walk on 2026-09-26, against the spec's archive recommendation: the loop is superseded by dagu nightshift and the reasoning is recoverable from git history. Spec 'Decisions for the operator' item 2 must be updated to record the choice.
**Outcome:** applied
**Ref:** ba20e57


## Q8 — shepherd-v2/decide-3 — tradeoff

**Question:** Decide-3: does Shepherd stay a separate repo (20_agentflow), or become 00_Governance/skills-pack/?
**Options considered:** separate repo / fold into 00_Governance/skills-pack/
**Chosen:** Separate repo: Shepherd stays in 20_agentflow.
**Decided-by:** human
**Justification:** Operator chose option 1 in the /unblock walk on 2026-09-26. Governance already archives skills inward (skills-global/); a second inward path would make Governance both source and archive of the same files and re-open the which-copy-is-authoritative question.
**Outcome:** applied
**Ref:** ba20e57


## Q9 — shepherd-v2/decide-record — tradeoff

**Question:** Where do the operator's Decide-1..3 answers go in the spec: edit the 'Decisions for the operator' body section, or append a section below the review rounds?
**Options considered:** edit the body section in place / append an 'Operator decisions' section after the review rounds
**Chosen:** Append '## Operator decisions — 2026-09-26' at the end of the spec; body section left verbatim, including the archive recommendation Decide-2 overrode.
**Decided-by:** agent
**Justification:** US-SH2-02 binds the 7.75 score to the SHA-256 of the text above the first review heading; editing the Decide section would invalidate the score and force a re-panel over a non-substantive change. The appended section states it wins over the body where they differ. Reversible: fold into the body at the next substantive rev.
**Outcome:** assumed
**Ref:** ba20e57
