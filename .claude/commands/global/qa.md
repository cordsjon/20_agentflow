# /QA — Refinement Bucket Q&A

Drive unrefined stories in `refinement-bucket.md` to DOR-ready status.
Two modes: **autonomous refinement** (no user needed) and **Q&A mode** (user input required).

---

## Protocol

### Step 1 — Read the bucket

Read `refinement-bucket.md` in full.
Collect all items from both `## Needs Q&A` and `## Self-Refinable` sections.
If both sections are empty → report "Refinement bucket is empty — nothing to refine." and STOP.

Also read `governance/DOR.md` to confirm the current DOR checklist before evaluating any item.

---

### Step 2 — Self-refine autonomous items (no user input)

For each item in `## Self-Refinable`:

1. **Load codebase context** — run `run_pipeline` with the story title as task to surface relevant architecture, patterns, and constraints.
2. **Fill DOR gaps** using retrieved context:
   - Missing architecture decision → derive from existing service/route patterns
   - Missing test strategy → reference `requirements/TESTCASES.md` and `requirements/TEST_CONCEPT.md`
   - Missing dependency list → identify from code graph
   - Missing size estimate → count likely queue items based on AC count
3. **Write spec stub** if spec document is missing — create `requirements/SPEC_<slug>.md` with functional requirements. Use 5–8 FRs derived from the AC.
4. **Update the DOR checklist** in `refinement-bucket.md` — check off newly satisfied items.
5. **Check if all items are now green:**
   - All green → graduate (see Step 4)
   - Still gaps → move item to `## Needs Q&A` with a note on the remaining blockers

---

### Step 3 — Q&A pass for blocked items

Pick **one item** from `## Needs Q&A` — the one with the most blocking questions answered (closest to DOR).

Ask the user targeted questions to fill the remaining DOR gaps. Rules:
- Ask only what is **needed for DOR** — no scope creep questions
- Group related questions (max 4 per turn using `AskUserQuestion` if structured, or numbered list if prose)
- One item per `/QA` invocation — do not jump between items mid-session
- After user responds: update the item's DOR checklist and notes in `refinement-bucket.md` immediately

**Question categories by DOR gap:**

| DOR gap | Ask about |
|---------|-----------|
| No User Story | Role, goal, benefit — "Who does this? What do they want? Why does it matter?" |
| No AC | "What does done look like? What would a tester check?" |
| No spec/architecture | "New API? New model? New module? Or extend existing?" |
| No dependency info | "Does this need X to be done first? Blocked by anything?" |
| No test strategy | "Unit, integration, or E2E? Roughly how many test cases?" |
| Size unknown | "One sprint item or multiple? Rough number of tasks?" |

---

### Step 4 — Graduate ready items

An item is **ready to graduate** when ALL DOR checklist items are checked.

1. **Verify spec panel score** — if spec document exists and score is unknown, note: "Run `/sc:spec-panel requirements/SPEC_<slug>.md` to get score >= 7.0 before final graduation."
   - If score is confirmed >= 7.0 (or not yet run): graduate anyway, note score needed.
2. **Move to `BACKLOG.md#Ready`** using this format:
   ```markdown
   ### [Story Title]
   - **Added:** YYYY-MM-DD (graduated from refinement-bucket)
   - **Summary:** [1-2 sentences]
   - **Spec:** [requirements/SPEC_<slug>.md or inline]
   - **User Stories:** [list]
   - **Size:** S / M / L
   - **Dependencies:** [list or "none"]
   - **Test strategy:** [types + approx count]
   - **Status:** Ready ✓
   ```
3. **Remove item from bucket** — delete its section from `refinement-bucket.md`.
4. **Add to `## Recently Graduated`** log:
   ```markdown
   - **[Story Title]** — graduated YYYY-MM-DD → BACKLOG.md#Ready
   ```

---

### Step 5 — Report

After each `/QA` run, print a brief summary:

```
QA pass complete:
  Self-refined: [N items] — [titles]
  Graduated to BACKLOG#Ready: [N items] — [titles]
  Q&A in progress: [title] — [N] gaps remaining
  Still blocked: [N items] — [titles and top blocker]
```

---

## Rules

- **One item per Q&A turn** — don't mix questions from multiple stories
- **Never implement** — `/QA` is refinement only; no code changes, no queue items created
- **Spec first, score second** — write the spec stub before asking user to run spec-panel
- **Graduate only on full green** — partial DOR = stays in bucket
- **Items arriving during a session** — if user sends a story-shaped idea mid-session (without `/q` prefix), Claude MAY add it to `refinement-bucket.md` directly rather than routing through full INBOX→BACKLOG flow, when the intent is clearly "refine this"
- **Bug DOR-lite items** — route through `triage` instead; `refinement-bucket.md` is for features/stories only
- **Spec panel score** — note as pending if not yet run; do not block graduation purely on missing score if all other DOR criteria are met and the spec exists

## Dry Run

When `--dry-run` is passed, **do not modify any files or ask Q&A questions**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| read | `refinement-bucket.md` | List items in Needs Q&A + Self-Refinable sections |
| read | `governance/DOR.md` | Load current DOR checklist |
| refine | Self-Refinable items | Describe DOR gaps that would be auto-filled |
| create | `requirements/SPEC_<slug>.md` | Spec stubs that would be generated |
| ask | user (Q&A items) | List questions that would be asked per DOR gap |
| graduate | DOR-complete items | Items that would move to `BACKLOG.md#Ready` |

Include item count per section, DOR gap summary, and which items are closest to graduation.
End with confidence: **High** (items have few gaps), **Medium** (significant Q&A needed), or **Low** (bucket empty or all items heavily blocked).
