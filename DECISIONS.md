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


## Q10 — shepherd-v2/US-SH2-01 — deviation

**Question:** AC-1 (0 sc: hits) is unsatisfiable literally: DECISIONS.md is append-only and quotes the dead names as history. Scope?
**Chosen:** The AC-1 test excludes DECISIONS.md only; every other file (81 hits/11 files measured) is fixed. BACKLOG.md:291 reworded.
**Decided-by:** agent
**Justification:** An append-only journal cannot be edited without breaking the schema gate; every living document is fixed.
**Outcome:** assumed
**Ref:** 621c30f (at write time)


## Q11 — shepherd-v2/US-SH2-01 — tradeoff

**Question:** Which /sh: command replaces /sc:cleanup, /sc:design and /sc:implement, none of which has a same-named successor?
**Chosen:** /sc:cleanup -> /sh:verify, /sc:design -> /sh:plan, /sc:implement -> /sh:execute (mapping table in the plan Task 1.4). Found on the way: the pre-existing dangling /sh:poster-analysis in SKILLS.md retargeted to /sh:business-analysis, which renders the DIN poster.
**Decided-by:** agent
**Justification:** The v2 DOD tail drops the cleanup step; verify is where findings are checked. Each target exists in ~/.claude/commands/sh (checked by loop).
**Outcome:** assumed
**Ref:** 621c30f (at write time)


## Q12 — shepherd-v2/US-SH2-02 — deviation

**Question:** dor_gate.py: how are entries without a story id, stories held only in a linked spec, nested headings, and a score on a bug-lite entry handled?
**Chosen:** Selector accepts a title substring when not an id; US/AC are read from the linked spec when the entry body has none; entries nest (every title line starts one — the plan's i=j loop skipped every ### story inside ## Ready and failed 15/16 tests); bug-lite ignores a present score.
**Decided-by:** agent
**Justification:** 20_agentflow's own entry title has no US- id and its 7 stories live in the spec (live check: us=7 ac=13, PASS). Governance uses ### US-ID headings under ## Ready, which the non-nesting loop could never select.
**Outcome:** assumed
**Ref:** a5a708f (at write time)


## Q13 — shepherd-v2/US-SH2-04 — tradeoff

**Question:** sh-4-reviewer-panel: bundle (2026-06-26, 9789 B) is newer than runtime (2026-06-20, 6640 B) — which copy is truth? And the 18 runtime-truth copies: replace the bundle dir or copy over it?
**Chosen:** Bundle wins for sh-4-reviewer-panel: promote after the manifest exists. The 18 others: runtime copied OVER the bundle in place (not rm -rf + cp), because sh-ux-design's bundle holds wireframe-rules.md, concept-compare.md, handoff.md that both SKILL.md copies read and the runtime lacked; the three were also restored into ~/.claude/skills/sh-ux-design.
**Decided-by:** agent
**Justification:** The reviewer-panel diff is authored content (disjoint lenses per experts/PANEL_PROTOCOL.md, codex refute pass, gated auto-apply), not a stale skeleton; the protocol sections it cites exist. The plan's rm -rf step would have deleted three files a live skill references.
**Outcome:** assumed
**Ref:** ae345d1 (at write time)


## Q14 — shepherd-v2/US-SH2-04 — deviation

**Question:** skills_manifest.py: check exits 1 only on structural errors and reports runtime drift; record added; and the plan's guard made a bundle-wins promote impossible (record needs identical, promote needs recorded). How is the first bundle-wins adoption done?
**Chosen:** check: structural errors exit 1, drift is reported only. promote gets --expect-runtime-sha <sha of the reviewed runtime SKILL.md>: proceeds only while the live file still has that digest. Used once for sh-4-reviewer-panel (Q13) after backing the runtime copy up and carrying its runtime-only evals/ into the bundle.
**Decided-by:** agent
**Justification:** The runtime is where skills get edited, so drift must be visible but not block commits. An explicit reviewed digest keeps the race guard (a runtime edit after review still refuses) without a blanket --force.
**Outcome:** assumed
**Ref:** bfd5266 (at write time)


## Q15 — shepherd-v2/spec-edits — deviation

**Question:** The verified-tag gate (installed in Chunk 2) scans the WHOLE staged spec and blocks on 8 bare [verified] tags in the frozen, panel-scored body. Editing them breaks digest 5176cdbc81e4 and the 7.75 score. How are append-only spec edits committed?
**Chosen:** ALLOW_UNCHECKABLE_VERIFIED=1 on spec-append commits only, after checking the added lines carry 0 [verified] tags (git diff | grep '^+' | grep -ci verified -> 0). The plan's assumption that only new edits are checked was wrong.
**Decided-by:** agent
**Justification:** The gate's documented escape valve downgrades to a loud warning; the 8 tags predate the gate and are frozen by the digest contract. Durable fix (not done here): make the gate judge added lines only, or re-panel the spec with checkable tags.
**Outcome:** assumed
**Ref:** 534c433 (at write time)


## Q16 — shepherd-v2/spec-edits — deviation

**Question:** The verified-tag gate (installed in Chunk 2) scans the WHOLE staged spec and blocks on 8 bare verified-tags in the frozen, panel-scored body. Editing them breaks digest 5176cdbc81e4 and the 7.75 score. How are append-only spec edits committed?
**Chosen:** Fix the verified-tag gate to judge only added lines of the staged diff (Governance change, own story); ALLOW_UNCHECKABLE_VERIFIED=1 procedure stays as interim until it lands.
**Decided-by:** human
**Justification:** The gate exists to police new claims; pre-existing tags in frozen/legacy files should not block current work. Only option that removes the recurring manual bypass without editing the digest-frozen spec.
**Outcome:** applied
**Ref:** ce86d79 (at write time)
**Supersedes:** Q15 — resolved


## Q17 — shepherd-v2/spec-rev2 — tradeoff

**Question:** FIPD table is defined only in agentflow KNOWN_PATTERNS.md:9-17 while the spec says rules live in Governance — where does the single authoritative copy go?
**Chosen:** Confirmed: the single FIPD definition lives in 00_Governance/KNOWN_PATTERNS.md (KP-4974); 20_agentflow DOCTRINE.md links to it.
**Decided-by:** human
**Justification:** Shared rules live in Governance next to its ~10 existing uses; the dependency runs agentflow -> Governance, consistent with Q335 keeping the Governance pipeline self-contained.
**Outcome:** applied
**Ref:** 8a7bd4f (at write time)
**Supersedes:** Q2 — resolved


## Q18 — shepherd-v2/decide-record — tradeoff

**Question:** Where do the operator's Decide-1..3 answers go in the spec: edit the 'Decisions for the operator' body section, or append a section below the review rounds?
**Options considered:** edit the body section in place / append an 'Operator decisions' section after the review rounds
**Chosen:** Keep the appended "Operator decisions" section AND add a one-line pointer under the original "Decisions for the operator" section naming the override (decision 2: CLAUDE-LOOP.md deleted, not archived).
**Decided-by:** human
**Justification:** Operator: a reader stopping at the original section must not take the overridden archive recommendation as what happened. Accepted cost: the spec body digest 5176cdbc81e4 changes, so the 7.75 score line on the (Done) Shepherd v2 BACKLOG entry reads stale-score.
**Outcome:** applied
**Ref:** 447dc34 (at write time)
**Supersedes:** Q9 — resolved


## Q19 — shepherd-v2/US-SH2-01 — deviation

**Question:** AC-1 (0 sc: hits) is unsatisfiable literally: DECISIONS.md is append-only and quotes the dead names as history. Scope?
**Chosen:** Confirmed: the AC-1 no-sc: test exempts DECISIONS.md only; every other file stays free of sc: names.
**Decided-by:** human
**Justification:** The decision log is append-only history; rewriting quoted names would falsify it, and a new entry quoting an old name is itself history.
**Outcome:** applied
**Ref:** 9b459bf (at write time)
**Supersedes:** Q10 — resolved


## Q20 — shepherd-v2/US-SH2-01 — tradeoff

**Question:** Which /sh: command replaces /sc:cleanup, /sc:design and /sc:implement, none of which has a same-named successor?
**Chosen:** Confirmed: /sc:cleanup->/sh:verify, /sc:design->/sh:plan, /sc:implement->/sh:execute; /sh:poster-analysis->/sh:business-analysis.
**Decided-by:** human
**Justification:** Operator confirmed via /mop "all confirmed" after the /unblock review walk.
**Outcome:** applied
**Ref:** f4972fa (at write time)
**Supersedes:** Q11 — resolved


## Q21 — shepherd-v2/US-SH2-02 — deviation

**Question:** dor_gate.py: how are entries without a story id, stories held only in a linked spec, nested headings, and a score on a bug-lite entry handled?
**Chosen:** Confirmed as shipped: title-substring selector, US/AC from linked spec, nested entries, bug-lite ignores score.
**Decided-by:** human
**Justification:** Operator confirmed via /mop "all confirmed" after the /unblock review walk.
**Outcome:** applied
**Ref:** f4972fa (at write time)
**Supersedes:** Q12 — resolved


## Q22 — shepherd-v2/US-SH2-04 — tradeoff

**Question:** sh-4-reviewer-panel: bundle (2026-06-26, 9789 B) is newer than runtime (2026-06-20, 6640 B) — which copy is truth? And the 18 runtime-truth copies: replace the bundle dir or copy over it?
**Chosen:** Confirmed as shipped: bundle wins for sh-4-reviewer-panel; the 18 runtime copies copied over the bundle in place.
**Decided-by:** human
**Justification:** Operator confirmed via /mop "all confirmed" after the /unblock review walk.
**Outcome:** applied
**Ref:** f4972fa (at write time)
**Supersedes:** Q13 — resolved


## Q23 — shepherd-v2/US-SH2-04 — deviation

**Question:** skills_manifest.py: check exits 1 only on structural errors and reports runtime drift; record added; and the plan's guard made a bundle-wins promote impossible (record needs identical, promote needs recorded). How is the first bundle-wins adoption done?
**Chosen:** Confirmed as shipped: check exits 1 only on structural errors; promote --expect-runtime-sha for bundle-wins adoption.
**Decided-by:** human
**Justification:** Operator confirmed via /mop "all confirmed" after the /unblock review walk.
**Outcome:** applied
**Ref:** f4972fa (at write time)
**Supersedes:** Q14 — resolved


## Q24 — US-AF-07 — deviation

**Question:** Should the 20_agentflow top-level command mirror be synced or retired?
**Options considered:** sync it with the source / retire it
**Chosen:** Retire the 19 top-level files after porting the 7 lines the source never had. Keep global/sh and global/remotion.
**Decided-by:** agent
**Justification:** No reader found in 20_agentflow, Governance tooling, hooks, scripts, LaunchAgents or dagu config. crontab was not searched because the permission layer denied it. Claude Code may also load project commands in a 20_agentflow session; that is unverified. Git restores the files.
**Outcome:** assumed
**Ref:** a3ab0bb, 00_Governance 8aa1c0bbf


## Q25 — US-AF-07 — deviation

**Question:** Should the 20_agentflow top-level command mirror be synced or retired?
**Options considered:** sync it with the source / retire it
**Chosen:** Keep: the 19 top-level mirror files stay retired, with global/sh and global/remotion unchanged.
**Decided-by:** human
**Justification:** Operator confirmed the default when walked through the review queue on 2026-11-01.
**Outcome:** applied
**Ref:** 69a7f07 (at write time)
**Supersedes:** Q24 — resolved


## Q26 — US-AF-09 — deviation

**Question:** Should the config sync keep depending on sync-repos, an accepted cost in the DAG comment since 2026-08-07?
**Options considered:** keep / run in parallel / run config sync first
**Chosen:** Run claude-config-sync first, with sync-repos and report after it.
**Decided-by:** agent
**Justification:** The accepted cost assumed the next tick would run the sync, but permanent repo failures meant it never did. Drilled on dagu 2.24 with scratch DAGs: a sync-repos failure still ends Failed and pages, and a config failure still lets sync-repos run. Reversible by moving the step back.
**Outcome:** assumed
**Ref:** janitor-nightly-sync.yaml


## Q27 — US-AF-09 — irreversible-action

**Question:** How should the 22 peer commits be taken on the Mini, given a plain run replaces newer files?
**Options considered:** plain run / fast-forward then Mini wins / fast-forward then per-file choice
**Chosen:** Fast-forward, keep incoming only for the 11 files where it repairs a foreign home path, Mini copy wins elsewhere, and drop the 13 Paperclip files again. 5 active-tier Paperclip memories were tombstoned in the local archive.
**Decided-by:** agent
**Justification:** Governance sources match the Mini copy for all 7 commands, and 7 of those files are older Mini versions by blob history. Paperclip was decommissioned in cbc8c97 and 7783f5a. Rehearsed in a fake home with a control. Pushed without force; undo with a revert of 99d5c75.
**Outcome:** assumed
**Ref:** 99d5c75 (claude-config)


## Q28 — US-AF-09 — gate-resolution

**Question:** Should the debt sweep run again? It has not run since 2026-09-18 because debt-sweep-nightly aborts it when janitor-nightly-sync fails, and the fix for the config sync deliberately left that unchanged.
**Options considered:** leave off / clear the repo failures so it returns / run it regardless of repo failures
**Chosen:** —
**Decided-by:** agent
**Justification:** Turning it on starts unattended agent spend of up to the DAG setting of MAX_COST 40 per night, after six weeks off. The last log, 2026-09-18, ended with 46 errors. Only the operator can accept that spend.
**Outcome:** escalated
**Ref:** debt-sweep-nightly.yaml


## Q29 — US-AF-09 — gate-resolution

**Question:** Do the two facts Q28 rests on hold: the last log ended with 46 errors, and a restart costs up to MAX_COST 40 a night? Q28 stays open; this entry only corrects its evidence.
**Options considered:** keep the Q28 wording / record the measured figures next to it
**Chosen:** Neither holds as worded. Q28 stays escalated, with the measured figures recorded here.
**Decided-by:** agent
**Justification:** Errors: the progress line counts http_error and delivery_unknown across the whole ledger, latest per batch key (hermes_debt_dispatch.py progress_report), so it read 46 on every night from 09-10 to 09-18. Those 46 date from 07-28 to 09-08: 30 are the cwd 400 that adapter commit 6ae1f34 fixed on 09-08, 13 are refused or dropped connections on 07-28, 3 are API 500s on 07-29 and 07-30. From 09-09 to the last dispatch on 09-14: 49 ok, 1 partial, $177.65. The nights of 09-15 to 09-18 dispatched nothing for $0. Lifetime: $302.41, 211 rows fixed, 175 skipped, 14 failed; whether the fixes were real is unmeasured. Cost: MAX_COST is split across two legs and checked after each batch, so the main leg stops at $20 plus one batch, $27.21 at the measured largest batch of $7.21. The second leg has never dispatched: findings auto exits 5 on P-0013, which spans 11 projects, and no findings-plan.json exists. Nights above $40 (top $51.34) predate the split of 09-14. Tonight, by dry run on a scratch plan: 19 dispatch rows in 7 batches, of which 2 batches and 5 rows would go, because 00_Governance and 30_SVG-PAINT are dirty; about $6 to $7 at the batch mean of $2.94 to $3.69 (inference). New hazard: 3 of those 5 rows target 15_belegfluss, frozen by the operator on 2026-09-28, so a restart would commit into a frozen repo. Unexplained: the findings step is in the script at 09-16 and 09-18 yet absent from the logs of 09-15 to 09-18.
**Outcome:** applied
**Ref:** Q28; debt_sweep_nightly.sh; dispatch-ledger.jsonl


## Q30 — US-AF-09 — tradeoff

**Question:** How should janitor commits get past the commit-trailer gate that has rejected them in gated repos since 2026-09-18, given that succeeding also unlocks the janitor merge into main?
**Options considered:** fixed scripted trailer / audited ALLOW_MISSING_TRAILER override / exclude gated repos from the janitor
**Chosen:** Fixed scripted trailer from the gate, and the rejection reason kept in the nightly report. The janitor merge behaviour is unchanged.
**Decided-by:** agent
**Justification:** commit_trailer_gate.py names MANDATED_TRAILER as the default for commits with no session behind them, and beehive-claude-sync.sh and backup-memory.sh already do this; an override would disable the gate for the one writer that runs unattended. Replay on a throwaway index in 20_CONSIGLIERE and 55_Nebenkosten: pre-commit rc 0, commit-msg rejected with the old message and accepted with the new one. Cost: commits resume, so a clean repo merges its feature branch into main and pushes. 55_Nebenkosten has no concord hold on its 2 staged files, so its 10-commit branch legal/research-deadlines-formal merges at the next nightly unless the merge conflicts (main is 1 ahead). 20_CONSIGLIERE merges feat/caploop-d1-gap-engine once the claim on BACKLOG.md is released. Both are revertable, and merging is the documented purpose of the DAG step. Timing also suggests this gate is what stopped the sweep: installed 09-18 13:43, last sweep log 09-18 02:13; dagu history for that night is gone, so this is inference. The sweep stays off: the two permanent push failures still fail sync-repos.
**Outcome:** assumed
**Ref:** Governance fix(janitor) commit; commit_trailer_gate.py


## Q31 — US-AF-09 — gate-resolution

**Question:** Should the debt sweep run again? It has not run since 2026-09-18 because debt-sweep-nightly aborts it when janitor-nightly-sync fails, and the fix for the config sync deliberately left that unchanged.
**Options considered:** leave off / clear the repo failures so it returns / run it regardless of repo failures
**Chosen:** Restart the debt sweep: exclude 60_wot-garage and whatcable from the nightly sync and park the 15_belegfluss rows, starting after the 02:00 run of 2026-11-02 has proven AC-03 and the janitor fix.
**Decided-by:** human
**Justification:** Operator picked option A via /unblock on 2026-11-01, on the evidence in Q29: about $6 to $7 the first night, about $27 ceiling, unmeasured quality of the rows marked fixed.
**Outcome:** applied
**Ref:** 1433813 (at write time)
**Supersedes:** Q28 — resolved


## Q32 — Q31 resume 2026-11-02 — gate-resolution

**Question:** The 02:00 run on 2026-11-02 still failed to commit 20_CONSIGLIERE (56 files): its verified-tag gate blocked BACKLOG.md:1216, whose [verified 2026-11-01 from source: ...] tag named no command. FAILED to commit counts toward the janitor's exit, so the Q31 excludes alone would not restart the sweep. Fix the tag in another project's staged file, or leave it and report?
**Options considered:** re-run the claims and rewrite the tag as command -> output / downgrade the whole tag to [inference] / ALLOW_UNCHECKABLE_VERIFIED override / leave it for the CONSIGLIERE session
**Chosen:** re-run the claims and rewrite the tag as command -> output; the one claim with no command (register_cli.py:181 unguarded) became [inference]
**Decided-by:** agent
**Justification:** The handover checklist says a reasoned commit failure is fixed first. Re-running keeps three claims at verified strength with evidence; the override would wave new bad tags through. Verified: CONSIGLIERE pre-commit replayed on a throwaway index with all 56 files -> rc=0. Excludes then added per Q31: matcher pipeline -> excluded 60_wot-garage, excluded whatcable, kept 20_CONSIGLIERE. US-AF-09 closed, AC-03 ticked (claude-config bc4789b == origin). Next 02:00 tick runs the sweep.
**Outcome:** assumed
**Ref:** 20_CONSIGLIERE/BACKLOG.md:1216; ~/.config/janitor/nightly-exclude.txt


## Q33 — US-AF-09 — deviation

**Question:** Should the config sync keep depending on sync-repos, an accepted cost in the DAG comment since 2026-08-07?
**Options considered:** keep / run in parallel / run config sync first
**Chosen:** Run claude-config-sync first, with sync-repos and report after it.
**Decided-by:** human
**Justification:** Operator ruling 2026-11-02 in /unblock: accept every assumed default as recommended (one ruling covering all 288 assumed review-queue entries). The original entry's reasoning stands.
**Outcome:** applied
**Ref:** b992fd1 (at write time)
**Supersedes:** Q26 — resolved


## Q34 — US-AF-09 — irreversible-action

**Question:** How should the 22 peer commits be taken on the Mini, given a plain run replaces newer files?
**Options considered:** plain run / fast-forward then Mini wins / fast-forward then per-file choice
**Chosen:** Fast-forward, keep incoming only for the 11 files where it repairs a foreign home path, Mini copy wins elsewhere, and drop the 13 Paperclip files again. 5 active-tier Paperclip memories were tombstoned in the local archive.
**Decided-by:** human
**Justification:** Operator ruling 2026-11-02 in /unblock: accept every assumed default as recommended (one ruling covering all 288 assumed review-queue entries). The original entry's reasoning stands.
**Outcome:** applied
**Ref:** b992fd1 (at write time)
**Supersedes:** Q27 — resolved


## Q35 — US-AF-09 — tradeoff

**Question:** How should janitor commits get past the commit-trailer gate that has rejected them in gated repos since 2026-09-18, given that succeeding also unlocks the janitor merge into main?
**Options considered:** fixed scripted trailer / audited ALLOW_MISSING_TRAILER override / exclude gated repos from the janitor
**Chosen:** Fixed scripted trailer from the gate, and the rejection reason kept in the nightly report. The janitor merge behaviour is unchanged.
**Decided-by:** human
**Justification:** Operator ruling 2026-11-02 in /unblock: accept every assumed default as recommended (one ruling covering all 288 assumed review-queue entries). The original entry's reasoning stands.
**Outcome:** applied
**Ref:** b992fd1 (at write time)
**Supersedes:** Q30 — resolved


## Q36 — Q31 resume 2026-11-02 — gate-resolution

**Question:** The 02:00 run on 2026-11-02 still failed to commit 20_CONSIGLIERE (56 files): its verified-tag gate blocked BACKLOG.md:1216, whose [verified 2026-11-01 from source: ...] tag named no command. FAILED to commit counts toward the janitor's exit, so the Q31 excludes alone would not restart the sweep. Fix the tag in another project's staged file, or leave it and report?
**Options considered:** re-run the claims and rewrite the tag as command -> output / downgrade the whole tag to [inference] / ALLOW_UNCHECKABLE_VERIFIED override / leave it for the CONSIGLIERE session
**Chosen:** re-run the claims and rewrite the tag as command -> output; the one claim with no command (register_cli.py:181 unguarded) became [inference]
**Decided-by:** human
**Justification:** Operator ruling 2026-11-02 in /unblock: accept every assumed default as recommended (one ruling covering all 288 assumed review-queue entries). The original entry's reasoning stands.
**Outcome:** applied
**Ref:** b992fd1 (at write time)
**Supersedes:** Q32 — resolved


## Q37 — Q31 sweep restart, 2026-11-03 — gate-resolution

**Question:** The 2026-11-03 02:00 and 15:00 janitor runs failed to commit 00_Governance: the verified-tag gate blocked 5 tags in two unheld files (HANDOVER-merged-2026-10-18-2152.md:59-62, bare [verified]; the svg-tracealpha-02 plan:30, a well-formed tag whose regex holds a ']' that ends the gate's match before the arrow). The sweep was aborted both times, $0 spent. Fix the tags, override, or leave them?
**Options considered:** move the evidence into the tags and mark tags with no command as [recall] / ALLOW_UNCHECKABLE_VERIFIED override / change the gate regex / leave for the authors
**Chosen:** move the adjacent command -> output into the two handover tags, mark the two with no command as [recall], put the plan's command in backticks; committed a37ba018d
**Decided-by:** agent
**Justification:** Same route as Q32. Verified: the full 00_Governance pre-commit replayed on the janitor's exact commit set (held files reset) -> rc=0; the plan's claim re-run -> 0. The gate regex was left alone: a fail-closed gate shared by every repo needs its own test, and backticks work around it. Still at risk: the held KETO 2026-10-14 and rootmap 2026-10-18-2151 handovers carry 5 more bare tags and will block once their claims are released.
**Outcome:** assumed
**Ref:** 00_Governance a37ba018d


## Q38 — interactive/panel-policy — gate-resolution

**Question:** May the panel policy rule skip spec-panel entirely for a trivial change (one CLI flag, tweak of an existing feature), or must spec-panel always run with the rule only adding lenses?
**Options considered:** skip entirely (new dor_gate track none) / spec-panel always runs, rule adds lenses only
**Chosen:** Skip entirely. dor_gate.py gains a `none` track; stories on it need no score line.
**Decided-by:** human
**Justification:** Operator ruling 2026-11-08 in the panel-policy brainstorm (question A carried from HANDOVER-20_agentflow-2026-11-08-0949.md). Recorded in docs/superpowers/specs/2026-11-08-panel-policy-design.md §Intent ruling 3.
**Outcome:** applied
**Ref:** 1d8c8eb (HEAD when logged, not the work commit)


## Q39 — interactive/panel-policy — gate-resolution

**Question:** Is a project default panel set derived from the census (measured) or from a per-project human label (declared)? Test case: 00_Governance, second-largest and most componentized repo, spec-panel only so far.
**Options considered:** measured: census table decides, 00_Governance gets architecture / declared: human label, 00_Governance marked tooling-off
**Chosen:** Measured. The census-generated projects.json decides; per-repo declaration can only add (security for data sensitivity), never remove.
**Decided-by:** human
**Justification:** Operator ruling 2026-11-08 in the panel-policy brainstorm (question B carried from HANDOVER-20_agentflow-2026-11-08-0949.md). Recorded in docs/superpowers/specs/2026-11-08-panel-policy-design.md §Intent ruling 4 and §Layer 2.
**Outcome:** applied
**Ref:** 1d8c8eb (HEAD when logged, not the work commit)


## Q40 — interactive/panel-policy — tradeoff

**Question:** When a census refresh adds a panel to a project default, do Ready stories scored under the old policy re-run the new panel (churn) or keep passing on a stored policy basis (grandfather)?
**Options considered:** accept churn, refresh PR lists affected stories / grandfather via stored panel list + census date per story
**Chosen:** Accept churn for the transition period. No stored basis. Revisit once roster and thresholds settle.
**Decided-by:** human
**Justification:** Operator ruling 2026-11-08, answering the builder-check question on re-gating; design doc §Intent ruling 5 and §Layer 2 refresh.
**Outcome:** applied
**Ref:** 1d8c8eb (HEAD when logged, not the work commit)


## Q41 — panel-policy/plan1 — tradeoff

**Question:** Keyword table for layer 3: YAML file (design) or Python constant?
**Chosen:** Python constant in panel_policy.py — stdlib-only module, one row today.
**Decided-by:** agent
**Justification:** dor_gate/panel_policy are stdlib-only vendored files; PyYAML would break that. Revisit at the third keyword row.
**Outcome:** applied
**Ref:** a667201 (HEAD when logged, not the work commit)


## Q42 — panel-policy/plan1 — deviation

**Question:** Data dir name next to panel_policy.py?
**Chosen:** scripts/panel_policy_data/ (design said panel_policy/)
**Decided-by:** agent
**Justification:** A sibling dir named like the module shadows it as a namespace package under some import orders.
**Outcome:** applied
**Ref:** a667201 (HEAD when logged, not the work commit)


## Q43 — panel-policy/plan1 Task 2 — deviation

**Question:** Keep the scratch census service regex verbatim (plan) or fix it?
**Options considered:** verbatim / fix
**Chosen:** Fixed: word boundaries only on word-edged alternatives.
**Decided-by:** agent
**Justification:** Probe: \b(FastAPI\(|...)\b never matches FastAPI()/express(), and \b@app never matches a decorator. Old vs fixed census over the same 41 repos: svc moves in 8 rows, derived default moves in 1 (25_Hardware gains architecture-panel, svc 1->2); no other field differs.
**Outcome:** applied
**Ref:** a667201 (HEAD when logged, not the work commit)


## Q44 — panel-policy/plan1 Task 6 — deviation

**Question:** Route missing-panel:* to the panel stage now, or leave dor_needs_score_only to Plan 2 (plan)?
**Options considered:** Plan 2 / now
**Chosen:** Now, in 00_Governance backlog_dor_pipeline._is_score_reason, with a test.
**Decided-by:** agent
**Justification:** Without it every normal story in a census-architecture project goes to the stage D LLM rewrite nightly (00_Governance: 52/52 Ready stories gain missing-panel:architecture-panel, 18 of them pass today). Stage E still scores spec-panel only, so pipeline promotion is unchanged until Plan 2; direct gate users block on the missing score.
**Outcome:** applied
**Ref:** a667201 (HEAD when logged, not the work commit)


## Q45 — panel-policy/plan1 Task 7 — deviation

**Question:** Census refresh DAG: GOV-only commit + PR (plan) or both repos via managed_commit?
**Options considered:** GOV + PR / both repos, direct land
**Chosen:** Both repos via managed_commit.py, change judged by rows_sha256; no PR.
**Decided-by:** agent
**Justification:** projects.json is vendored, so a GOV-only refresh fails the identity test; no sibling DAG opens PRs (backlog-cleanup lands via managed_commit). generated= changes every run, so git diff would commit a date-only change monthly.
**Outcome:** applied
**Ref:** a667201 (HEAD when logged, not the work commit)


## Q46 — panel-policy/plan2 — deviation

**Question:** Where does the lens-pack "loader" live?
**Chosen:** Prose: PANEL_PROTOCOL.md §Invocation + spec-panel.md steps 0.5/2.5, pinned by tests/test_lens_packs.py over the YAML
**Decided-by:** agent
**Justification:** The panel executor is an LLM reading YAML; there is no Python executor to extend. The test pins shape, expert ids, lens set == LENS_ORDER and alias wiring.
**Outcome:** applied
**Ref:** 9da43b0 (HEAD when logged, not the work commit)


## Q47 — panel-policy/plan2 — tradeoff

**Question:** ai-panel retirement: keep a retired copy of the command file?
**Chosen:** git rm only; .claude/skills-retired/sh-ai-panel already preserves the roster
**Decided-by:** agent
**Justification:** No commands-retired convention exists; inventing one for a single file is more structure than the artefact is worth.
**Outcome:** applied
**Ref:** 9da43b0 (HEAD when logged, not the work commit)


## Q48 — panel-policy/plan2 — tradeoff

**Question:** Per-panel stage E results: new stage names or a panel field?
**Chosen:** StageResult.panel field; stage stays "panel"
**Decided-by:** agent
**Justification:** Ledger consumers filter on stage; a new name per panel would hide architecture runs from every digest written so far.
**Outcome:** applied
**Ref:** 9da43b0 (HEAD when logged, not the work commit)


## Q49 — panel-policy/plan2 — deviation

**Question:** HEAVY_RE: which markers were dropped?
**Chosen:** bare token/auth (now need a creating verb), bare across, bare ios/swift (now platform names); second pass: verb->noun window stops at , ; without/or/row(s), and platform names never match inside a hyphenated story id
**Decided-by:** agent
**Justification:** Measured on 00_Governance Ready (GOV d099bf0f8): heavy 29 -> 10 (plan regex) -> 5 of 53 after the one allowed extra iteration; the 5 left are real (2x Flutter, Android/Termux, new table, row deletion). token = LLM tokens, across = branches, swift = adverb in this corpus.
**Outcome:** applied
**Ref:** 9da43b0 (HEAD when logged, not the work commit)


## Q50 — panel-policy/plan2 — tradeoff

**Question:** Foundations for 20_agentflow are undeclared (bin/foundations open). Proceed with Plan 2?
**Chosen:** Proceeded: Plan 2 completes an operator-ruled design (2026-11-08 rulings 1-5), not optimization work.
**Decided-by:** agent
**Justification:** TENET-11 undeclared branch: judged from the design doc; FOUNDATIONS.md for 20_agentflow remains to be written.
**Outcome:** applied
**Ref:** 9da43b0 (HEAD when logged, not the work commit)


## Q51 — panel-policy/plan2 — deviation

**Question:** Stage E implementation details the plan text and its own tests disagreed on
**Chosen:** run_stage_e_panels passes lenses to spec-panel only; an empty per-panel .panel takes the requested panel; resolve_policy fails closed on OSError
**Decided-by:** agent
**Justification:** The plan test asserts stub kwargs (not just argv) carry no lenses for architecture-panel; a bare StageResult stub would otherwise write a second spec-panel line; an unreadable BACKLOG crashed run_story with FileNotFoundError instead of policy_unavailable (GOV commit for Task 7).
**Outcome:** applied
**Ref:** 9da43b0 (HEAD when logged, not the work commit)


## Q52 — interactive/unblock-all-2026-11-14 — gate-resolution

**Question:** Ratify Q37: fix the 5 verified-tag gate blocks that aborted the 2026-11-03 janitor runs, override, or leave them?
**Chosen:** move the adjacent command -> output into the two handover tags, mark the two with no command as [recall], put the plan's command in backticks; committed a37ba018d
**Decided-by:** human
**Justification:** Operator blanket approval 2026-11-14: "/unblock -all and /assumed" — keep the default already taken.
**Outcome:** applied
**Ref:** fb749db (HEAD when logged, not the work commit)
**Supersedes:** Q37 — superseded
