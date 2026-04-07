# /health — Pipeline Health Check

Consolidated staleness scan, orphan detection, risk review, and velocity trend.
Combines PO-04 (staleness), PO-06 (risks), and orphan detection into one command.

**Target:** Surface pipeline rot before it costs real time.

---

## Protocol

### Step 1 — Staleness scan

Read `BACKLOG.md`. For each section, check item age using the date in `(→ Section YYYY-MM-DD)` or `(triaged from INBOX YYYY-MM-DD)`:

| Section | Stale threshold | Action |
|---------|----------------|--------|
| Ideation | >14 days without graduation to Refining | Flag as stale |
| Refining | >14 days without spec link or graduation to Ready | Flag as stale |
| Ready | >7 days without being queued via `/workflow` | Flag as idle |

Skip items that are explicitly marked as `SHIPPED`, `FIXED`, `RESOLVED`, `SUPERSEDED`, or struck through (`~~`).

Report format:
```
STALE ITEMS:
  ⚠ Ideation: "{title}" — {N} days (since {date})
  ⚠ Refining: "{title}" — {N} days, no spec link
  ⚠ Ready: "{title}" — idle {N} days, not queued
```

If no stale items: `STALE: None — pipeline is fresh`

### Step 2 — Orphan detection

An orphan is a BACKLOG item that has ALL of:
- No `Next:` action line
- No spec link (`requirements/` or `SPEC_`)
- No `Status:` line
- Not struck through or marked as shipped/resolved

Report format:
```
ORPHANED (no next action):
  ? "{title}" — consider archiving or adding Next: action
```

If none: `ORPHANS: None`

### Step 3 — Risk review

Read `BACKLOG.md` and look for a `## Risks` section (PO-06 format: `R-N · description · L=X I=Y · mitigation · owner`).

If the section exists, list active risks.
If it doesn't exist, report: `RISKS: No risk register found (consider adding ## Risks to BACKLOG.md)`

### Step 4 — Velocity trend

Read `DONE-Today.md` — count items with today's date.
Read `done/` directory — find the two most recent `DONE-{YYYY}-W{WW}.md` files.
Parse each archive file — count total items (lines matching `- [x]`).

Report:
```
VELOCITY:
  Today:      {N} items
  This week:  {N} items (W{WW})
  Last week:  {N} items (W{WW-1})
  Trend:      ↑ / ↓ / → (flat)
```

If archives don't exist or can't be parsed, report what's available and skip the rest.

### Step 5 — Retro counter

Read `MEMORY.md` or the project memory file. Extract `retro_stories_since_last` value.

```
RETRO: {N}/10 stories since last retro
```

If counter >= 8: add `⚠ Retro approaching — {10-N} stories remaining`
If counter >= 10: add `🔴 RETRO OVERDUE — run /kaizen before next task`

### Step 6 — Produce consolidated report

```
HEALTH CHECK — SVG-PAINT — {YYYY-MM-DD}
════════════════════════════════════════════

STALE ITEMS:
  {stale items or "None — pipeline is fresh"}

ORPHANED:
  {orphan items or "None"}

RISKS:
  {risk items or "No risk register"}

VELOCITY:
  Today:      {N} items
  This week:  {N} items (W{WW})
  Last week:  {N} items (W{WW-1})
  Trend:      {↑/↓/→}

RETRO: {N}/10 stories until next retro

════════════════════════════════════════════
SUMMARY: {N} stale · {N} orphans · {N} risks · velocity {↑/↓/→}
```

### Step 7 — STOP

Health check is read-only. Never modify any files. Never start remediation.
If stale/orphan items are found, the user can:
- Run `/triage` or manually move items
- Run `/workflow` to queue idle Ready items
- Add `Next:` actions to orphaned items
- Update the risk register

---

## Rules

- Read-only — never writes to any file
- Graceful degradation — if a file is missing or unparseable, report what you can and skip the rest
- Dates are best-effort — if an item has no date, report "unknown age"
- Struck-through items (`~~`) and items marked SHIPPED/FIXED/RESOLVED/SUPERSEDED are always skipped
- The velocity section should never error — if no archives exist, just show today's count
- Run during planning rounds (PO-05) and on-demand

## Dry Run

When `--dry-run` is passed, **do not perform any scans**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| read | `BACKLOG.md` | Staleness scan across Ideation/Refining/Ready |
| read | `BACKLOG.md` | Orphan detection (items with no next action) |
| read | `BACKLOG.md ## Risks` | Risk register review |
| read | `DONE-Today.md`, `done/` | Velocity trend calculation |
| read | `MEMORY.md` | Retro counter check |
| report | stdout | Consolidated health check report |

Note: This skill is already read-only. Dry run previews which files would be read and which checks would run.
End with confidence: **High** (all pipeline files exist), **Medium** (some files missing), or **Low** (no BACKLOG.md found).
