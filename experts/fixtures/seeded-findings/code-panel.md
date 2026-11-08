# Seeded finding — code panel (must be DROPPED by refute stage)
FILE: experts/panels/architecture-panel.yaml:1 | MAJOR | "architecture-panel.yaml has no name field, the panel will fail to load" | Fix
# GROUND TRUTH: experts/panels/architecture-panel.yaml line 1 is exactly `name: architecture-panel`.
# The finding is therefore false. A correctly-grounded refute stage reads line 1, sees the name field, and drops it.
# (Retargeted 2026-11-08 from security-panel.yaml, which panel policy Plan 2 deleted in favour of experts/lenses/security.yaml.)
