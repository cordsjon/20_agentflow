---
name: sh-mobile-panel
description: "Mobile lens on the spec panel — runs /sh:spec-panel with --lenses mobile (platform fitness, lifecycle, device testability, store readiness)"
---

# /sh:mobile-panel — alias for `/sh:spec-panel --lenses mobile`

Since 2026-11-08 (panel policy, `docs/superpowers/specs/2026-11-08-panel-policy-design.md` §Roster) mobile is a
lens pack, not a standalone panel: `/Users/jcords-macmini/projects/20_agentflow/experts/lenses/mobile.yaml`
(experts + checklist) attaches to one spec-panel run. `scripts/panel_policy.py` adds it automatically for
projects the census marks; this command is the manual path.

## Behavior

Run `/sh:spec-panel <every argument given here> --lenses mobile`. Everything else is spec-panel's:
`/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` applied in full, scoring, the
`PANEL-VERDICT` line, score recording. There is no `mobile-panel.yaml` under `experts/panels/` any more — do not look for one.
