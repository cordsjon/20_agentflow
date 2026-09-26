---
name: sh-dor
description: Run the executable Definition of Ready gate (scripts/dor_gate.py in 20_agentflow) against one BACKLOG entry and quote its verdict. Use before an item moves from Refining to Ready or into a queue.
---

# /sh:dor — Definition of Ready (executable)

The checklist is not restated here; the script is the rule (`~/projects/20_agentflow/DOCTRINE.md` § DOR).

1. Resolve the BACKLOG file (`$ARGUMENTS` may name it; default `./BACKLOG.md`) and the entry: a story id `US-XXX-NN` or a title substring.
2. Run, verbatim, and paste the whole output:
   ```bash
   python3 ~/projects/20_agentflow/scripts/dor_gate.py <BACKLOG.md> "<id-or-title>"
   ```
3. Exit 0 → the entry may move to Ready / a queue. Exit 1 → quote each `FAIL <reason>` line and stop; fix the entry (or run `/sh:spec-panel` if the reason is `no-score`/`score-below-7.0`/`stale-score`), never edit the score line by hand. Exit 2 → `not-found` or `ambiguous-id`: name the entry more precisely.
4. The FINAL line of your reply is the script's own `DOR-VERDICT:` line, unchanged. Consumers (`/goal`, `backlog_dor_pipeline.py`) parse it.

Tracks are read from the entry's tag (`[bug]` → bug-lite, `[hotfix]` → hotfix); `--track` overrides; `--json` for machines.
