# /cost-calc — Engineering Value Calculator

Calculate the dollar-equivalent value of Claude's engineering output for a project or time period.
Produces a cost comparison across 4 company archetypes (Solo, Lean Startup, Growth Co, Enterprise).

**Philosophy:** Conservative by default. Every estimate should be defensible to a skeptical CTO. When in doubt, round down. The goal is a credible floor, not a flattering ceiling.

---

## Protocol

### Step 0 — Discovery (MANDATORY)

Before collecting any metrics, ask the user these qualifying questions. Do NOT skip this step. Wait for answers before proceeding.

**Questions to ask:**

1. **Scope** — What period or epic should I estimate? (date range, epic name, or "entire project")
2. **Claude plan** — Which plan are you on? (Pro $20/mo, Max $100/mo, Team $30/seat/mo)
3. **Claude hours** — Roughly how many hours did Claude actively work? (wall-clock, not calendar time)
4. **Your involvement** — How much of your own time went into directing, reviewing, testing, and debugging Claude's output? (hours or %)
5. **Production readiness** — Is this code deployed and serving users, or is it development/staging only?
6. **Missing work** — What work remains that Claude did NOT do? (deployment, monitoring, manual QA, design, product decisions, user research, etc.)

If the user says "just run it" or doesn't want to answer, use the most conservative defaults and note assumptions explicitly.

---

### Step 1 — Establish the functional baseline from project artifacts

**Do NOT start from git diffs.** Start from the PRD, epics, and user stories to understand what was actually built.

1. **Read the PRD / requirements** — identify the scope of what was delivered:
   - Number of user stories (US) completed
   - Number of epics touched
   - Functional domains (auth, CRUD, export, UI, etc.)
   - Integration complexity (external APIs, file I/O, database, etc.)

2. **Map user stories to complexity tiers:**

   | Tier | Description | Human estimate (1 senior dev) |
   |------|-------------|-------------------------------|
   | **S — Trivial** | Config change, copy update, simple bug fix | 2–4 hrs |
   | **M — Standard** | Single CRUD endpoint + UI + tests, straightforward feature | 8–16 hrs |
   | **L — Complex** | Multi-endpoint feature, data model changes, business logic | 16–32 hrs |
   | **XL — Epic** | Cross-cutting concern, new subsystem, major refactor | 32–64 hrs |

   Assign each completed US a tier. If no formal US exist, group deliverables into functional units and tier those instead.

3. **Then validate against git metrics** — use git log to cross-check:
   ```bash
   git log --since="YYYY-MM-DD" --until="YYYY-MM-DD" --oneline --shortstat
   ```
   Git metrics are a sanity check, not the primary input. 500 lines of generated boilerplate != 500 lines of complex logic.

---

### Step 2 — Estimate equivalent human effort

For each US/functional unit, the tier gives a base estimate. Then apply these adjustment factors:

#### 2a. Complexity adjustments (multiply base estimate)

| Factor | Condition | Multiplier |
|--------|-----------|------------|
| **Novel domain** | First time building this type of system (no prior codebase to reference) | 1.3x |
| **Integration density** | 3+ external systems or services | 1.2x |
| **Data model complexity** | 10+ entities with relationships, migrations | 1.2x |
| **Compliance / validation** | Strict business rules, export gates, quality checks | 1.15x |
| **Cross-platform** | Windows + Linux, multiple browsers, responsive | 1.15x |

Apply only factors that genuinely apply. Do not stack all of them by default.

#### 2b. Overhead additions (add to total, not per-US)

| Category | % of engineering hours | Rationale |
|----------|----------------------|-----------|
| **Code review** | +10% | A human dev's PRs get reviewed by peers |
| **Meetings & alignment** | +10% | Standups, planning, retros, ad-hoc discussions |
| **Context switching** | +5% | Task transitions, environment setup, interruptions |
| **Deployment & ops** | +5% | CI/CD, staging verification, rollback planning |

Total overhead: **+30%** on the raw engineering estimate.

Sum all US estimates (with complexity adjustments) + overhead → **Total Human Hours**.

---

### Step 3 — Apply conservative discount factors

These reduce the headline number to account for what Claude did NOT deliver:

| Discount | Reduction | Rationale |
|----------|-----------|-----------|
| **No production deployment** | -15% | Code exists but wasn't deployed, monitored, or operated. If deployed, skip this. |
| **No user-facing QA** | -10% | Claude tests its own code but doesn't do exploratory QA, accessibility testing, or user acceptance testing |
| **No design/product work** | -5% | Claude implements specs, doesn't create them. If user provided PRD, the product thinking was human work |
| **Human review overhead** | -5% to -15% | User spent time reviewing, correcting, re-prompting. Scale based on user's answer to Q4 |
| **Maintenance unknown** | -5% | Code quality over time is unproven — bugs may surface later |

Apply only relevant discounts. Sum → **Discount %**. Calculate **Adjusted Human Hours** = Total Human Hours × (1 - Discount %).

---

### Step 4 — Calculate cost comparison

Use these rate cards (US market averages, 2025–2026):

| Archetype | Blended hourly rate | Team composition | Calendar multiplier |
|-----------|-------------------|------------------|-------------------|
| **Solo** | $110/hr | 1 senior full-stack | 1.0x |
| **Lean Startup** | $110/hr | 1 senior + 0.5 junior + 0.25 QA | 1.4x |
| **Growth Co** | $115/hr | 2 senior + 1 mid + 0.5 QA + 0.5 PM | 2.0x |
| **Enterprise** | $125/hr | 2 senior + 2 mid + 1 QA + 1 PM + 0.5 DevOps | 2.5x |

Note: rates use $110 base (not $125) for Solo/Lean — $125 is top-quartile, not median. Enterprise rate stays at $125 due to overhead costs.

For each archetype:
- **Total hours** = Adjusted Human Hours x Calendar multiplier
- **Total cost** = Total hours x Blended rate
- **Calendar time** = Total hours / (productive hours/day x team size)
  - Solo: 5.5 productive hrs/day x 1 person
  - Lean Startup: 5.5 hrs/day x 1.75 people
  - Growth Co: 5 hrs/day x 4 people (larger teams = more coordination overhead)
  - Enterprise: 5 hrs/day x 6.5 people

---

### Step 5 — Calculate Claude metrics

- **Speed multiplier** = Adjusted Human Hours (Solo) / Claude Active Hours
- **Claude cost** = Plan cost prorated for calendar days. Add user's own time at their rate (ask, or default $0 — note as assumption)
- **Net savings** = Solo Total Cost - Claude Cost
- **ROI** = Solo Total Cost / Claude Cost (expressed as "every $1 -> $X of value")
- **$/Claude hour** = Solo Total Cost / Claude Active Hours

---

### Step 6 — Output the report

Print the full report using this template:

```
## Engineering Value Report — [Project Name]
**Period:** [start date] -> [end date] ([N] calendar days)
**Estimation basis:** [N] user stories across [N] epics from [PRD name / source]

---

### Functional Scope

| Epic / Domain | User Stories | Complexity Tier | Base Hours | Adjusted Hours |
|---------------|-------------|-----------------|------------|----------------|
| [Epic name] | US-XX, US-YY | M, L | N hrs | N hrs |
| ... | ... | ... | ... | ... |
| **Subtotal** | **N US** | | **N hrs** | **N hrs** |

Complexity adjustments applied: [list which factors and multipliers]
Overhead (+30%): +N hrs
**Gross Human Hours: N hrs**

### Conservative Discounts Applied

| Discount | % | Hours Removed | Rationale |
|----------|---|---------------|-----------|
| [discount name] | -N% | -N hrs | [why] |
| ... | ... | ... | ... |
| **Total discount** | **-N%** | **-N hrs** | |

**Adjusted Human Hours: N hrs** (this is the defensible estimate)

---

### Value per Claude Hour

| Value Basis | Total Value | Claude Hours | $/Claude Hour |
|-------------|-------------|--------------|---------------|
| Engineering only (Solo) | $X | N hrs | **$X/Claude hr** |
| Full team (Growth Co) | $X | N hrs | **$X/Claude hr** |

### Speed vs. Human Developer
- Adjusted human hours for same work: **N hours**
- Claude active hours: **N hours**
- Speed multiplier: **Nx**
- Note: Human developer also handles deployment, monitoring, on-call — Claude does not

### Cost Comparison
- Human developer cost (Solo): $X (at $110/hr)
- Claude cost: ~$X ([plan] prorated for N days)
- User's own time: [N hrs noted / not included — see assumptions]
- Net savings: ~$X
- ROI: ~Nx (every $1 spent on Claude produced ~$X of engineering value)

---

### Grand Total Summary

| Metric | Solo | Lean Startup | Growth Co | Enterprise |
|--------|------|--------------|-----------|------------|
| Calendar Time | ~N months | ~N months | ~N months | ~N months |
| Total Hours | N | N | N | N |
| Total Cost | $XK | $XK | $XK | $XK |

---

### The Headline

_Claude produced approximately N adjusted human-hours of engineering work
across N calendar days, valued at $XK-$XK depending on team structure.
A solo developer would need ~N months; a growth-stage team ~N months.
Claude cost was ~$X for the period — an estimated Nx return on investment._

---

### Assumptions & Caveats

1. Rates based on US market median (not top-quartile) for 2025-2026
2. Senior full-stack developer (5+ years experience) as baseline
3. Estimates derived from [PRD / user stories / functional groupings] — not raw line counts
4. Conservative discounts applied for: [list applied discounts]
5. Does NOT include: product/design work, user research, marketing, legal, hosting, or ongoing maintenance
6. User's own time directing Claude is [included at $X/hr / not included — add $X if valued]
7. Code is [deployed / not yet deployed] — production reliability is [proven / unproven]
8. [Any domain-specific caveats]

### What this estimate does NOT capture
- Long-term maintenance cost of the codebase
- Opportunity cost of the user's time spent prompting/reviewing
- Value of institutional knowledge a human developer would accumulate
- Risk premium for AI-generated code in production
```

---

## Rules

- **Discovery first** — ALWAYS ask the Step 0 questions before calculating. Do not produce a report without user input on scope and context.
- **PRD-grounded** — estimates must trace to user stories, epics, or functional units — never to raw line counts or file counts alone. Lines of code are a sanity check, not an input.
- **Lower-bound bias** — when a range exists (e.g., 8-16 hrs), use the lower bound unless complexity factors justify higher. Never cherry-pick the high end.
- **Discount honestly** — apply all relevant discounts from Step 3. Omitting discounts to inflate the number is not allowed.
- **Transparent assumptions** — every number must be traceable to a source (git, PRD, user statement, or stated assumption). List all assumptions at the bottom.
- **No implementation** — this command produces a report only. No code changes, no queue items.
- **Scope flexibility** — user can specify a date range, a specific epic, or "entire project". Default to entire project if unspecified.
- **Reusable** — the report format is designed to be copy-pasted into proposals, investor decks, or blog posts.
- **Currency** — default USD. If user specifies another currency, convert at current rates.
- **Invite challenge** — end the report by inviting the user to challenge any assumption or rate. Offer to recalculate with different inputs.

## Dry Run

When `--dry-run` is passed, **do not produce the full report or ask discovery questions**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| ask | user (Step 0) | 6 discovery questions about scope, plan, hours, involvement |
| read | PRD / epics / user stories | Identify functional scope and complexity tiers |
| read | git log | Cross-check metrics against commit history |
| calculate | human effort estimate | Apply complexity adjustments + overhead |
| calculate | cost comparison | 4 archetypes (Solo/Lean/Growth/Enterprise) |
| report | stdout | Full engineering value report with assumptions |

Include which PRD/epic sources are available and estimated US count.
End with confidence: **High** (PRD exists, clear scope), **Medium** (partial docs), or **Low** (no PRD, estimation from git only).
