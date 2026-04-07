# /autopilot — Autonomous Task Executor

Run the Inner Loop: read → verify → execute → quality gate → commit → loop.

---

## Before Starting

1. Read `.autopilot` — must contain exactly `run` to proceed. If missing or not `run`: write
   `"Autopilot not armed — run toolbar Resume or set .autopilot to 'run'"` to `.claude-action` and STOP.
2. Read `.claude/memory.md` — load prior session context.
3. Read `DOD.md` and `DOR.md` — internalize the quality gate and entry criteria.

---

## Inner Loop (repeat until stopped)

### Step 1 — Semaphore check (MANDATORY — use Read tool)
**USE THE READ TOOL** to read the file `.autopilot` from disk RIGHT NOW. Do NOT rely on any
previously cached value. The file content must be exactly `run` (trimmed). If it is anything
else, or the file does not exist → write `"Autopilot paused by user"` to `.claude-action` and
**STOP immediately**. Do not start a new task. Do not proceed to Step 2.

### Step 2 — Queue check
Read `TODO-Today.md`. Find the first `- [ ] **Task**` item.
- If none found → write `"Queue complete — no more tasks"` to `.claude-action`, STOP.

### Step 2b — Queue starvation check (informational)
Count unchecked `- [ ]` items in `TODO-Today.md ## Queue`. Also count non-struck-through
bullets in `BACKLOG.md ## Ready` (lines starting with `- **`, not `- ~~**`).

If **both** conditions are true:
- Queue has ≤1 unchecked items remaining
- Ready has ≥3 non-struck-through items

Then write to `.claude-action`:
```
Planning round suggested — queue running low (N unchecked, M ready in backlog). Run /workflow or dismiss.
```

**Rules:**
- Informational only — do NOT pause, do NOT auto-run `/workflow`. The operator decides.
- Fires at most once per loop iteration. If the suggestion was already written this iteration, skip.
- Do NOT block on this — proceed to Step 3 regardless of whether the suggestion fires.

### Step 3 — Readiness check
Detect task type from label:
- `[BUG]` or `[BUG-HOTFIX]` → apply **Bug DOR-lite** (root cause + fix plan + regression test named)
- All other tasks → apply full **DOR.md** checklist

If check fails → write specific gap to `.claude-action`, write `"pause"` to `.autopilot`, STOP.

### Step 4 — Execute
**Feature tasks:** work through the User Story and Acceptance Criteria.

**`[BUG]` / `[BUG-HOTFIX]` tasks:** apply the root cause fix from the task description.
- After the fix, verify the regression test named in the task passes
- If the fix reveals a larger systemic issue → write finding to `.claude-action`, pause, do not expand scope

Follow `CLAUDE.md §3` Implementation Commandments throughout.
Run `python -m app.cli.main greenlight --all` before proceeding to step 5.

### Step 4b — Mid-task semaphore check
**USE THE READ TOOL** to read `.autopilot` again. If not `run` → STOP immediately.
This check runs after execution and before the cleanup sub-loop, giving the user a
second opportunity to pause within a single task cycle.

### Step 5 — Cleanup sub-loop (quality gate)
```
run greenlight → review findings by severity

while Low findings exist:
    fix each Low finding
    re-run greenlight

if any Medium or High findings remain:
    write finding summary to .claude-action
    write "pause" to .autopilot
    STOP — human review required before continuing
```

**For `[BUG] Doc tail` tasks specifically:**
- Add ≥1 finding entry to `QUALITY_AUDIT.md` under the current pass section
- Add a pattern to `KNOWN_PATTERNS.md` if the root cause is a reusable anti-pattern
- This is commandment 12 — it fires as a queue task, not as a side effect

### Step 6 — Commit
Atomic commit per `DOD.md` commit rules.
Message format: describes the *why*, not the *what*.

### Step 7 — Lifecycle
- Mark the task `[x]` in `TODO-Today.md`, then run:
  `python -m app.cli.main queue done --task "Task description"`
  This moves the item to DONE-Today.md with timestamp AND syncs BACKLOG.md
  (strikethrough + unblock detection). If `queue done` reports unblocked items,
  note them for the next planning round.
- Update `Sprint / Last session date` in `.claude/memory.md`

### Step 8 — Loop
**Go to Step 1 NOW.** You MUST use the Read tool to re-read `.autopilot` from disk.
Do NOT assume it still contains `run`. The user may have clicked Pause at any time.
This is non-negotiable — skipping this read is a known bug (KNOWN_PATTERNS.md #58).

---

## Invariants — never bypass

| Rule | Consequence of bypass |
|------|-----------------------|
| No commit without greenlight | Silent regressions ship |
| Medium+ findings pause autopilot | Quality debt accumulates unreviewed |
| Semaphore checked before EVERY task | Human pause is ignored |
| DOR / Bug DOR-lite verified before execution | Incomplete specs or undocumented bugs get implemented |
| `[BUG]` doc tail executed — never skipped | Bug learnings disappear; loop doesn't improve |
| memory.md updated at session end | Next session starts blind |

## Dry Run

When `--dry-run` is passed, **do not execute any loop iterations or modify any files**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| read | `.autopilot` | Check semaphore state (run/pause/missing) |
| read | `TODO-Today.md` | Identify next queued task |
| check | DOR / Bug DOR-lite | Validate readiness of next task |
| execute | task implementation | Describe what the task requires (files, tests, AC) |
| run | `greenlight --all` | Quality gate verification |
| commit | atomic commit | Describe commit scope |
| update | `TODO-Today.md`, `DONE-Today.md` | Mark task done, update lifecycle |

Include the current queue depth, next task description, and DOR status.
End with confidence: **High** (queue populated, DOR passes), **Medium** (DOR gaps detected), or **Low** (queue empty or semaphore not armed).
