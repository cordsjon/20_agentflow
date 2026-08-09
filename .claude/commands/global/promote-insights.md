---
name: promote-insights
description: Review pending insights from ~/.local/state/insights/pending.jsonl and promote KP candidates to 00_Governance/KNOWN_PATTERNS.md. Run at end of session, from /lightsout, or manually. Also invoked automatically by the lightsout skill's Step 0.
---

<context>
You are a world-class knowledge management and pattern recognition specialist with an IQ of 160.
You distill raw observations into reusable, actionable patterns that prevent repeat mistakes across projects.
</context>

# Promote Pending Insights to Known Patterns

## Steps

1. **Read pending insights**
   - Read `~/.local/state/insights/pending.jsonl`
   - If empty or missing, report "No pending insights" and exit

2. **Filter and rank KP candidates** (US-CURATOR-02 evidence-count gating)

   > **The script is the implementation.** `scripts/promote_insights.py` is what
   > /lightsout Step 0 actually runs, and it already performs every step in this
   > section. Prefer invoking it over re-implementing the logic here; this prose
   > describes its behaviour so the two cannot drift.

   - Only process lines where `kp_candidate: true`
   - Read each line's `occurrence_count` (treat a missing field as `1` — legacy rows)
   - Apply the promotion threshold: default `MIN_OCCURRENCE = 2`, matching the script's `--min-occurrences` default — a single sighting is an anecdote, not a pattern, and the deferral is non-destructive (a deferred insight is reported and stays in pending, never deleted, and promotes once it recurs). Override by passing `--min-occurrences` to the script. Comparison is inclusive (`>=`): at the default, count 2 promotes, count 1 defers.
   - Rank the surviving candidates by **effective recurrence** descending (pending `occurrence_count` + matches for the same fingerprint in recent archive months) — high-recurrence lessons promote first, so a `--max` cut truncates the least-evidenced tail. Ties break by first-captured `date` ascending, then `sha256` ascending.
   - Skip duplicates (compare insight text against existing KP entries in `~/projects/00_Governance/KNOWN_PATTERNS.md`)

3. **For each KP candidate (highest occurrence_count first):**
   - Determine the next available KP-N number (scan for highest `### KP-N:` in the file)
   - Determine the best category section (match against existing H2 sections, or create `## 13. [New Category]` if none fit)
   - Classify the FIPD action type (Fix/Investigate/Plan/Decide)
   - Write the entry in the established format (record the occurrence count in the Origin line when > 1):
     ```markdown
     ### KP-N: Short descriptive title

     **Category:** [section] | **Action:** [FIPD] | **Origin:** [context] (observed N×) ([date])

     [Insight text as prose description of the anti-pattern or lesson]

     **Correct pattern:** [Extracted or inferred correct approach]
     ```

4. **Update the file**
   - Append new entries to the appropriate category section in `~/projects/00_Governance/KNOWN_PATTERNS.md`
   - Update the "Last updated" date

5. **Verify-after-evolve guardrail** (US-CURATOR-01 — anti loop-gaming)
   - For each KP just written, run the deterministic verify primitive:
     `/usr/bin/python3 ~/.hermes/governance-worktree/scripts/verify_kp.py` (call `verify_kp(prose, root=~/projects)` — deterministic-first per AC-03)
   - `PASS` → leave the entry as written
   - `STALE` (a named file artifact no longer exists) → append `**Status:** unverified (YYYY-MM-DD)` to that KP entry and list it in the report. Do NOT auto-revert or delete (do-no-harm — human decides).
   - `UNVERIFIABLE` (no checkable file artifact) → only then escalate to an LLM judgement of whether the KP prose is still supported by its origin insight; record which path (deterministic vs LLM) produced the verdict.
   - This step does NOT score skill quality or re-rank — it only answers "does this KP still reproduce against its own evidence."

6. **Archive processed insights**
   - Move processed lines from `pending.jsonl` to `~/.local/state/insights/archive/YYYY-MM.jsonl`
   - Non-KP insights (kp_candidate: false) are archived without promotion

7. **Report**
   - List promoted insights with their KP-N numbers and occurrence counts
   - List any KPs flagged `unverified` by the verify-after-evolve guardrail (Step 5)
   - List archived non-KP insights
   - Report any duplicates skipped and any candidates deferred below `MIN_OCCURRENCE`
