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

2. **Filter KP candidates**
   - Only process lines where `kp_candidate: true`
   - Skip duplicates (compare insight text against existing KP entries in `~/projects/00_Governance/KNOWN_PATTERNS.md`)

3. **For each KP candidate:**
   - Determine the next available KP-N number (scan for highest `### KP-N:` in the file)
   - Determine the best category section (match against existing H2 sections, or create `## 13. [New Category]` if none fit)
   - Classify the FIPD action type (Fix/Investigate/Plan/Decide)
   - Write the entry in the established format:
     ```markdown
     ### KP-N: Short descriptive title

     **Category:** [section] | **Action:** [FIPD] | **Origin:** [context] ([date])

     [Insight text as prose description of the anti-pattern or lesson]

     **Correct pattern:** [Extracted or inferred correct approach]
     ```

4. **Update the file**
   - Append new entries to the appropriate category section in `~/projects/00_Governance/KNOWN_PATTERNS.md`
   - Update the "Last updated" date

5. **Archive processed insights**
   - Move processed lines from `pending.jsonl` to `~/.local/state/insights/archive/YYYY-MM.jsonl`
   - Non-KP insights (kp_candidate: false) are archived without promotion

6. **Report**
   - List promoted insights with their KP-N numbers
   - List archived non-KP insights
   - Report any duplicates skipped
