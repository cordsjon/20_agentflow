# Seeded finding — code panel (must be DROPPED by refute stage)
FILE: experts/panels/security-panel.yaml:1 | MAJOR | "security-panel.yaml has no name field, the panel will fail to load" | Fix
# GROUND TRUTH: experts/panels/security-panel.yaml line 1 is exactly `name: security-panel`.
# The finding is therefore false. A correctly-grounded refute stage reads line 1, sees the name field, and drops it.
