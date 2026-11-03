---
name: sh-estimate
description: "Development effort estimation with T-shirt sizing and risk adjustment"
---

# Effort Estimation

Estimate development effort for tasks, features, or projects.
T-shirt sizing aligned with task management. Risk-adjusted.

## When to Use

- Sizing a new feature or user story before committing
- Comparing effort across multiple options
- Planning sprints or task queues
- Assessing feasibility of a proposed change

## Process

### 1. Scope Analysis

- Read relevant code to understand current state
- Identify what needs to change (files, modules, interfaces)
- List dependencies and integration points
- Note unknowns and assumptions

### 2. Decompose Work

Break into concrete sub-tasks:

```
1. [Sub-task] — [what changes]
2. [Sub-task] — [what changes]
3. Tests — [scope of test coverage needed]
4. Integration — [what needs wiring up]
```

### 3. Size Each Sub-task

| Size | Meaning | Typical Scope |
|------|---------|---------------|
| **S** | Contained change | Single file, clear pattern, < 1 hour |
| **M** | Multi-file change | 2-5 files, some design needed, 1-4 hours |
| **L** | Cross-cutting change | 5+ files, new patterns, 4-16 hours |
| **XL** | Requires breakdown | Too large for single task -- split first |

### 4. Risk Adjustment

Identify risk factors that increase effort:

| Risk Factor | Multiplier |
|-------------|-----------|
| Unfamiliar code area | 1.5x |
| No existing tests | 1.3x |
| External API dependency | 1.5x |
| Database migration | 1.3x |
| Cross-platform concerns | 1.5x |
| Unclear requirements | 2x |

Apply the highest applicable multiplier (don't stack).

### 4b. Decision Tier (E1–E4) — count decisions reopened, not hours

Hours are guessed; **decisions reopened** can be counted before the work starts, by reading the spec, DECISIONS.md, and the seams the change touches. Overruns in this fleet live almost entirely in E3, where a "small" change re-syncs artifacts across several settled decisions. Declare the tier next to the size:

| Tier | Meaning | Test |
|------|---------|------|
| **E1 TOUCH** | Nothing reopened | Code, copy, style, a fix inside an existing decision. No new artifact. |
| **E2 EXTENSION** | One decision added, none reopened | A self-contained capability: one DECISIONS.md entry, nothing else moves. |
| **E3 INTERLOCK** | 1–6 existing decisions reopened | Artifacts re-synced across the set (spec + schema + contract + tests). This is where diligence is real. |
| **E4 RECONSTRUCTION** | >6 reopened, or the decision set itself is rewritten | Not a task — a redesign. Route through `for-dec` / a spec panel before sizing sub-tasks. |

How to count: list every existing decision (DECISIONS.md `Q<n>`, a settled schema, a public contract, a naming convention) the change would *change the answer to*. Adding is E2; changing is E3. A task whose tier disagrees with its T-shirt size (an S at E3) is the one to flag — that is the overrun in waiting. (RESEARCH.md R23, after leo Law 43.)

### 5. Present Estimate

```
## Estimate: [Feature/Task Name]

### Sub-tasks
| # | Task | Size | Tier | Risk | Adjusted |
|---|------|------|------|------|----------|
| 1 | [task] | M | E3 (reopens Q12, Q31) | Unfamiliar (1.5x) | M-L |
| 2 | [task] | S | E1 | None | S |
| 3 | Tests | M | E1 | No existing (1.3x) | M |

### Overall: [M-L] · Tier: [E3 — 2 decisions reopened: Q12, Q31]
### Confidence: [High/Medium/Low]
### Key Assumptions: [list]
### Unknowns: [list — each unknown reduces confidence]
```

## Boundaries

**Will**: Analyze scope, decompose work, size tasks, identify risks, present estimate.
**Will not**: Execute the work, create timelines, make commitments, or start implementation.

## Next Step

After estimation, user decides priority and scheduling. Proceed with implementation when ready.
