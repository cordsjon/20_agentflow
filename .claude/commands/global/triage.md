# /triage — INBOX Processor

Process `INBOX.md` items into the pipeline. Never leaves INBOX partially processed.

## Input Convention

**Everything the user sends without a `/q` prefix is loop input.** This means:
- User sends a screenshot → describe the visual, classify as bug/feature, triage immediately
- User sends an error message → root cause assessment, classify as `[bug]` or `[hotfix]`, triage immediately
- User sends a text description → classify and route
- User sends a link or paste → treat as context/constraint or feature input, route accordingly

**`/q` prefix = question only.** Answer conversationally. Do NOT add to INBOX or create queue items.

Triage can be **explicit** (user runs `/triage`) or **implicit** (Claude triages user input inline as it arrives).

---

## Protocol

### Step 1 — Read INBOX
Read `INBOX.md`. Collect all bullet items beneath the `---` separator.
Also check: did the user send any non-`/q` input this session that hasn't been triaged yet? If yes, treat it as an implicit INBOX item and include it in this triage pass.
If nothing to process → report "Nothing to triage" and STOP.

### Step 2 — Classify each item

| Type | Destination |
|------|-------------|
| Bug / regression — **blocking dev** | `[hotfix]` → `TODO-Today.md` directly (see hotfix rule below) |
| Bug / regression — non-blocking | `BACKLOG.md#Ideation` with tag `[bug]` |
| Feature idea / enhancement | `BACKLOG.md#Ideation` with brief description |
| Clarification / context / constraint | Relevant requirements doc or `CLAUDE.md` notes |
| Decision needed / blocked | `TODO-Today.md` as a decision task (if urgent) or `BACKLOG.md#Ideation` |
| Duplicate of existing item | Note the duplicate, discard |

**Hotfix rule:** A bug qualifies as `[hotfix]` (fast-track to TODO-Today) only when:
1. It is **actively blocking the dev loop** (server down, build broken, data corrupt)
2. The INBOX entry contains **root cause + fix plan** — satisfies Bug DOR-lite at triage time
3. If root cause is unknown → route to `BACKLOG#Ideation [bug]` instead (investigate first)

Hotfix task written to `TODO-Today.md` uses this format:
```
- [ ] **[BUG-HOTFIX] One-line description**
  - Root cause: [specific file/mechanism]
  - Fix: [1-3 concrete steps]
  - Regression test: [test file + test name]
  - Risk: CLAUDE.md §3.[N]
```
After the fix task, always append the bug doc tail:
```
- [ ] **[BUG] Doc tail: QUALITY_AUDIT.md + KNOWN_PATTERNS.md**
  - AC: ≥1 new finding in QUALITY_AUDIT.md; pattern added to KNOWN_PATTERNS.md if root cause is reusable
  - Test: n/a — documentation review
  - Risk: CLAUDE.md §3.12
```

### Step 3 — Write to destinations
Append classified items to the appropriate sections in `BACKLOG.md`.
For `BACKLOG.md#Ideation`, use this format:
```
- **[Item title]** (triaged from INBOX YYYY-MM-DD)
  - [Brief description]
  - **Status:** Idea only. Needs spec before Refining.
  - **Next:** [what needs to happen to move to Refining]
```

### Step 4 — Clear INBOX
Replace all bullet content in `INBOX.md` with:
```
_Empty — all items triaged._
```

### Step 5 — Report
List each item and where it was routed. Example:
```
Triaged 3 items:
  → BACKLOG#Ideation: "PDF engine idea" [feature]
  → BACKLOG#Ideation: "Export crash on empty collection" [bug]
  → CLAUDE.md notes: "Contrast ratio clarification for toddler tier"
```

---

## Rules

- `[hotfix]` items MAY go directly to `TODO-Today.md` — this is the only exception to BACKLOG stages
- `[hotfix]` REQUIRES root cause + fix plan in the INBOX entry — no root cause = no fast-track
- Every `[bug]` or `[hotfix]` task in `TODO-Today.md` MUST be followed by a doc tail task
- **Queue item BEFORE implementation — no exceptions:** Write the TODO-Today task(s) FIRST, then stop. Implementation begins only after the queue item exists. Never write code during triage.
- Never create User Stories during triage — triage only classifies and routes
- Never leave INBOX partially processed — all items in, all items out
- If an item is ambiguous, route to `BACKLOG#Ideation` with a clarification note

## Dry Run

When `--dry-run` is passed, **do not modify any files**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| read | `INBOX.md` | List all items to be triaged |
| classify | each item | Show type (bug/feature/hotfix/context) and destination |
| write | `BACKLOG.md#Ideation` | Items that would be appended |
| write | `TODO-Today.md` | Hotfix items that would be fast-tracked (if any) |
| clear | `INBOX.md` | Replace content with "Empty — all items triaged" |

Include the item count, classification breakdown, and routing destinations.
End with confidence: **High** (clear items, obvious classification), **Medium** (ambiguous items present), or **Low** (INBOX empty or items need user clarification).
