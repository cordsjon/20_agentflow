# /backlog-grooming — Backlog Cleanup & Archive Pass

Automated backlog hygiene. Scans for shipped/stale/orphaned items, archives completed work,
and produces a clean backlog focused on active pipeline items only.

**Trigger:** Lightsout chain (end-of-day), planning rounds (PO-05), kickoff suggestion (>5 stale), or on-demand.
**Cadence:** Weekly minimum. Daily if autopilot velocity is high (>5 items/day).

> **Note:** `/kickoff` runs a lightweight auto-archive pass (struck-through items only) at every session start.
> This command performs the **full** analysis: staleness scan, orphan detection, duplicate merge, dependency fix, and platform flagging.

---

## Protocol

### Step 1 — Staleness Scan (read-only)

Read `BACKLOG.md`. For each active (non-struck-through) item, check age using the date in `(→ Section YYYY-MM-DD)`:

| Section | Stale threshold | Action |
|---------|----------------|--------|
| Ideation | >14 days without graduation | Flag as stale |
| Refining | >14 days without spec link or graduation | Flag as stale |
| Ready | >7 days without being queued | Flag as idle |

Report:
```
STALENESS SCAN:
  {N} stale items found (or "None — pipeline is fresh")
  {list of stale items with age}
```

### Step 2 — Orphan Detection (read-only)

An orphan has ALL of:
- No `Next:` action line
- No spec link
- No `Status:` line
- Not struck through or marked shipped/resolved

Report:
```
ORPHANS:
  {N} orphaned items (or "None")
  {list with suggested action: archive / add Next}
```

### Step 3 — Shipped Item Inventory (read-only)

Count all struck-through (`~~`) items and items marked SHIPPED/FIXED/RESOLVED/SUPERSEDED/DONE across all sections.

Report:
```
ARCHIVE CANDIDATES:
  Ideation:  {N} shipped/resolved
  Refining:  {N} graduated/shipped
  Ready:     {N} shipped/done
  Risks:     {N} retired
  Total:     {N} items ready to archive
```

If total = 0: skip to Step 6.

### Step 4 — Archive (write)

**Only execute if Step 3 found >0 candidates AND user has not passed `--dry-run`.**

1. **Read or create** `done/BACKLOG-ARCHIVE.md`
   - If file exists: append new items under a dated section header `## Archived {YYYY-MM-DD}`
   - If file doesn't exist: create with header + all archived items

2. **For each section** (Ideation, Refining, Ready, Risks):
   - Extract all struck-through / SHIPPED / FIXED / RESOLVED / SUPERSEDED / DONE items
   - Append them to the archive file under the appropriate section
   - Remove them from `BACKLOG.md`

3. **Preserve** in BACKLOG.md:
   - All active (non-struck-through) items — NEVER touch these
   - Section headers and HTML comments
   - The `## Critical Path` section (clean up only fully-shipped chain entries)
   - The `## Risks` section (remove only RETIRED risks)

4. **Add archive link** to BACKLOG.md header if not present:
   ```
   > **Archive:** Shipped/superseded/resolved items → [done/BACKLOG-ARCHIVE.md](done/BACKLOG-ARCHIVE.md)
   ```

### Step 5 — Cleanup Fixes (write)

Apply these targeted fixes during the archive pass:

1. **Duplicate detection:** If two items reference the same feature/US, flag for manual merge or auto-merge if one is a pointer (e.g., `→ See existing item above`).

2. **Oversized shipped descriptions:** If a SHIPPED/SUPERSEDED item has >5 lines of description, trim to 1-line summary in the archive.

3. **Broken dependency references:** If an active item has `needs: X` where X is now SHIPPED/DONE, add `✅` after the dep: `needs: ~~X~~ ✅`.

4. **Missing follow-up dates:** If an item is `Status: Blocked` with no follow-up date, add `Follow-up by: {today + 7 days}`.

5. **Platform staleness:** Flag items referencing deprecated platforms (e.g., WinForms/PowerShell on macOS) with `⚠️ Platform review needed`.

### Step 6 — Produce Summary Report

```
BACKLOG GROOMING — {project} — {YYYY-MM-DD}
════════════════════════════════════════════════
BEFORE:  {N} lines in BACKLOG.md
AFTER:   {N} lines in BACKLOG.md ({-N%} reduction)
ARCHIVED: {N} items → done/BACKLOG-ARCHIVE.md

STALENESS:
  {stale items or "None — pipeline is fresh"}

ORPHANS:
  {orphan items or "None"}

FIXES APPLIED:
  {list of cleanup fixes or "None needed"}

ACTIVE COUNTS:
  Ideation:  {N} items
  Refining:  {N} items
  Ready:     {N} items
  Risks:     {N} active
════════════════════════════════════════════════
```

### Step 7 — STOP

Never start implementation. Never modify active items. Never change priorities.
The user decides what to do with stale/orphaned items.

---

## Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Steps 1–3 only (scan + report). No file modifications. |
| `--archive-only` | Skip staleness/orphan scan. Only archive shipped items. |
| `--force` | Archive without confirmation prompt. |

---

## Rules

- **Never modify active items** — only touch struck-through / SHIPPED / RESOLVED items
- **Never change priorities** — `#N` ordering is human-owned
- **Atomic writes** — use temp file + rename for BACKLOG.md updates
- **Idempotent** — running twice produces the same result (already-archived items aren't re-archived)
- **Archive preserves history** — items in archive retain their full original text
- **Graceful on missing files** — if `done/` or archive doesn't exist, create them
- **Section separators preserved** — HTML comments and `---` rulers stay in place

---

## Lightsout Integration

This command is part of the **Lightsout Chain** (SP-5 in agentflow):

```
/health → /backlog-grooming → /session-handoff
```

**Trigger conditions (any one):**
- Autopilot semaphore is `run` AND queue is empty (natural end-of-day)
- User invokes `/backlog-grooming` directly
- Planning round (PO-05) includes it as agenda item #2 (after INBOX scan)

**Agentflow wiring:**
- Chain: `SP-5: Lightsout Hygiene`
- Position: After last autopilot task completes, before session-handoff
- Frequency: End-of-day or weekly minimum
