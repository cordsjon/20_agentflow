# Seeded finding — code panel (must be DROPPED by refute stage)
FILE: experts/registry.yaml:1 | MAJOR | "registry.yaml has no name field, panels will fail to load" | Fix
# GROUND TRUTH: registry.yaml line 1 DOES define name. This finding is false.
# A correctly-grounded refute stage reads the line, sees the name, and drops it.
