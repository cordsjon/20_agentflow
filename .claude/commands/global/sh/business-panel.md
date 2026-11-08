---
name: sh-business-panel
description: "Business lens on the spec panel — runs /sh:spec-panel with --lenses business (positioning, pricing/launch assumptions, tail risk)"
---

# /sh:business-panel — alias for `/sh:spec-panel --lenses business`

Since 2026-11-08 (panel policy, `docs/superpowers/specs/2026-11-08-panel-policy-design.md` §Roster) business is a
lens pack, not a standalone panel: `/Users/jcords-macmini/projects/20_agentflow/experts/lenses/business.yaml`
(experts + checklist) attaches to one spec-panel run. `scripts/panel_policy.py` adds it automatically for
projects the census marks; this command is the manual path.

## Behavior

Run `/sh:spec-panel <every argument given here> --lenses business`. Everything else is spec-panel's:
`/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` applied in full, scoring, the
`PANEL-VERDICT` line, score recording. There is no `business-panel.yaml` under `experts/panels/` any more — do not look for one.
