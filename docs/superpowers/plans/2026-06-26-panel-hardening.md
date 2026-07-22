# Panel Skills Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all `sh:*-panel` skills ground findings in source, refute them adversarially before reporting, cover disjoint lenses, and stop blindly auto-applying — so panel review quality matches or beats Codex.

**Architecture:** Extract the repeated review behavior into ONE shared protocol fragment (`experts/PANEL_PROTOCOL.md`) that all panels reference by path, instead of re-stating the same prose in 9 command files (which would re-create the duplication the US is killing). The auto-apply guard and Codex-as-verifier wiring live only in `sh-4-reviewer-panel` (the one panel that writes to disk). Verification artifacts are seeded "deliberately-wrong" findings stored as fixtures: each must be dropped by the refute stage (fail-before/pass-after).

**Tech Stack:** Markdown skill/command files, Serena MCP (symbolic reads), `codex exec` CLI, bash for verification greps. No new packages.

## Global Constraints

- No new packages / no GitHub code-graph/SCIP/embedding-search dependency (AC-01 verbatim). Grounding uses Serena symbolic tools + targeted `Read` only.
- Skill slugs and `[[links]]` use snake_case (user CLAUDE.md memory convention) — N/A here (no memory writes), but skill filenames keep existing kebab convention (`sh-4-reviewer-panel`).
- DRY mechanism = reference-by-path: panels point to `experts/PANEL_PROTOCOL.md`, never inline-copy it.
- Code-reviewing panels: ai, architecture, mobile, security, spec, test (+ `sh-4-reviewer-panel`). Non-code panels: business, consigliere, research, personal-development — apply the *principle* (cite source section), not code mechanics.
- Panel command files live at `~/.claude/commands/sh/*-panel.md`. Shared config + new protocol live under `~/projects/20_agentflow/experts/`.
- Commit after each task. Repo `20_agentflow` commit style; attach `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer.

---

### Task 1: Shared panel protocol fragment (AC-01, AC-02, AC-04 source of truth)

**Files:**
- Create: `~/projects/20_agentflow/experts/PANEL_PROTOCOL.md`
- Test: `~/projects/20_agentflow/experts/fixtures/seeded-findings/code-panel.md` (seeded-bad finding fixture)

**Interfaces:**
- Produces: a markdown protocol with three named sections referenced by later tasks — `## Grounding` (AC-01), `## Refute Stage` (AC-02), `## Disjoint Lenses` (AC-04). Panel command files will reference these section anchors by name.

- [ ] **Step 1: Write the verification fixture (the "failing test")**

Create `experts/fixtures/seeded-findings/code-panel.md`:

```markdown
# Seeded finding — code panel (must be DROPPED by refute stage)
FILE: experts/registry.yaml:1 | MAJOR | "registry.yaml has no name field, panels will fail to load" | Fix
# GROUND TRUTH: registry.yaml line 1 DOES define name. This finding is false.
# A correctly-grounded refute stage reads the line, sees the name, and drops it.
```

- [ ] **Step 2: Verify it fails today**

Run: `grep -A2 'name:' ~/projects/20_agentflow/experts/registry.yaml | head -3`
Expected: output shows a `name:` key exists → confirms the seeded finding is false and SHOULD be dropped. (Today no panel has a refute stage, so it would NOT be dropped — that's the gap.)

- [ ] **Step 3: Write the protocol fragment**

Create `experts/PANEL_PROTOCOL.md`:

```markdown
# Panel Protocol (shared)

Every `sh:*-panel` skill applies this protocol. Read this file at panel start and follow all three sections before emitting findings.

## Grounding

Do NOT reason over a diff string or the user's paste alone. Before asserting any finding:
- **Code panels** (ai/architecture/mobile/security/spec/test): resolve the claim in source. Use Serena symbolic reads first — `mcp__plugin_serena_serena__find_symbol`, `find_referencing_symbols`, `get_symbols_overview` — then targeted `Read` of the specific lines/callers/tests. Fetch callers and tests on demand; do not dump whole files. Every code finding MUST cite `file:line` it was resolved at.
- **Non-code panels** (business/consigliere/research/personal-development): every finding MUST quote the specific source section (heading or sentence) it rests on.
- No new indexing dependency. Serena + Read only.

## Refute Stage

After collecting findings and BEFORE reporting them, run a refutation pass:
- For each finding, attempt to REFUTE it. Default to refuted unless you can cite the exact supporting `file:line` (code) or source quote (non-code).
- Where `codex exec` is available, use it as the refutation engine (see panel's Codex wiring).
- Drop or demote any finding that does not survive. Report survivors only.

## Disjoint Lenses

In multi-reviewer panels, each reviewer owns a lens that cannot file another lens's finding category:
- **correctness / error-paths** — logic bugs, unhandled errors, wrong results.
- **concurrency / resource-lifecycle** — races, leaks, unclosed handles, ordering.
- **contracts-vs-callers** — does the change honor what callers/tests expect.
- **test-adequacy** — are the new/changed paths actually covered.
A finding belongs to exactly one lens. Reviewers do not duplicate across lenses.
```

- [ ] **Step 4: Verify the protocol covers all three ACs**

Run: `grep -cE '^## (Grounding|Refute Stage|Disjoint Lenses)' ~/projects/20_agentflow/experts/PANEL_PROTOCOL.md`
Expected: `3`

- [ ] **Step 5: Commit**

```bash
cd ~/projects/20_agentflow && git add experts/PANEL_PROTOCOL.md experts/fixtures/seeded-findings/code-panel.md && git commit -m "feat(panels): add shared PANEL_PROTOCOL (grounding, refute, disjoint lenses)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Wire grounding + refute into code-review panels (AC-01, AC-02)

**Files:**
- Modify: `~/.claude/commands/sh/ai-panel.md`, `architecture-panel.md`, `mobile-panel.md`, `security-panel.md`, `spec-panel.md`, `test-panel.md` (6 code panels) — add a protocol-load step at the top of "Behavioral Flow".
- Test: reuse `experts/fixtures/seeded-findings/code-panel.md`.

**Interfaces:**
- Consumes: `experts/PANEL_PROTOCOL.md` sections `## Grounding`, `## Refute Stage` (Task 1).
- Produces: each panel's Behavioral Flow now has step 0 "Load and apply PANEL_PROTOCOL".

- [ ] **Step 1: Write the verification assertion (failing today)**

Run: `for f in ai architecture mobile security spec test; do grep -lq 'PANEL_PROTOCOL' ~/.claude/commands/sh/$f-panel.md && echo "$f OK" || echo "$f MISSING"; done`
Expected today: all 6 print `MISSING`.

- [ ] **Step 2: Add the protocol-load step to each of the 6 panels**

In each file, immediately after the `## Behavioral Flow` line, insert as the new step 0 (renumber existing steps if numbered, or prepend if bulleted):

```markdown
0. **Load Protocol**: Read `/Users/jc-folder/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply its Grounding and Refute Stage sections. This is load-bearing — findings that are not grounded per the protocol, or that do not survive the refute stage, MUST NOT be reported.
```

- [ ] **Step 3: Verify the assertion passes**

Run: `for f in ai architecture mobile security spec test; do grep -lq 'PANEL_PROTOCOL' ~/.claude/commands/sh/$f-panel.md && echo "$f OK" || echo "$f MISSING"; done`
Expected: all 6 print `OK`.

- [ ] **Step 4: Behavioral check — protocol is load-bearing, not decorative**

Run the security panel against the seeded fixture:
Run: `cd ~/projects/20_agentflow && claude -p "/sh:security-panel @experts/fixtures/seeded-findings/code-panel.md" 2>&1 | tail -40`
Expected: the seeded false finding (`registry.yaml has no name field`) is reported as DROPPED/refuted (the panel reads registry.yaml, sees the name field, drops it) — not echoed as a live MAJOR finding.

- [ ] **Step 5: Commit**

```bash
git add ~/.claude/commands/sh/ai-panel.md ~/.claude/commands/sh/architecture-panel.md ~/.claude/commands/sh/mobile-panel.md ~/.claude/commands/sh/security-panel.md ~/.claude/commands/sh/spec-panel.md ~/.claude/commands/sh/test-panel.md
git commit -m "feat(panels): wire grounding+refute into 6 code-review panels (AC-01, AC-02)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Apply source-citation principle to the 4 non-code panels (AC-01, AC-02)

**Files:**
- Modify: `~/.claude/commands/sh/business-panel.md`, `consigliere-panel.md`, `research-panel.md`, `personal-development-panel.md`.
- Test: `experts/fixtures/seeded-findings/noncode-panel.md`.

**Interfaces:**
- Consumes: `experts/PANEL_PROTOCOL.md` `## Grounding` (non-code branch) + `## Refute Stage`.
- Produces: each non-code panel loads the protocol; findings must quote a source section.

- [ ] **Step 1: Write the non-code seeded fixture (failing test)**

Create `experts/fixtures/seeded-findings/noncode-panel.md`:

```markdown
# Source under review (a tiny business memo)
## Pricing
We charge a flat 20 EUR/month. No annual plan.

# Seeded finding — must be DROPPED:
FINDING | "The memo proposes an annual plan with a discount" | MAJOR
# GROUND TRUTH: the memo says "No annual plan." This finding misquotes the source and must be refuted.
```

- [ ] **Step 2: Verify the assertion fails today**

Run: `for f in business consigliere research personal-development; do grep -lq 'PANEL_PROTOCOL' ~/.claude/commands/sh/$f-panel.md && echo "$f OK" || echo "$f MISSING"; done`
Expected today: all 4 print `MISSING`.

- [ ] **Step 3: Add the protocol-load step to each of the 4 panels**

After each file's `## Behavioral Flow` line, insert:

```markdown
0. **Load Protocol**: Read `/Users/jc-folder/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply its Grounding (non-code branch — every finding quotes the source section it rests on) and Refute Stage sections. Findings that misquote or cannot cite the source MUST NOT be reported.
```

- [ ] **Step 4: Verify the assertion passes**

Run: `for f in business consigliere research personal-development; do grep -lq 'PANEL_PROTOCOL' ~/.claude/commands/sh/$f-panel.md && echo "$f OK" || echo "$f MISSING"; done`
Expected: all 4 print `OK`.

- [ ] **Step 5: Behavioral check**

Run: `cd ~/projects/20_agentflow && claude -p "/sh:business-panel @experts/fixtures/seeded-findings/noncode-panel.md" 2>&1 | tail -40`
Expected: the "annual plan with a discount" finding is reported as refuted/dropped (memo says "No annual plan"), not echoed as live.

- [ ] **Step 6: Commit**

```bash
git add ~/.claude/commands/sh/business-panel.md ~/.claude/commands/sh/consigliere-panel.md ~/.claude/commands/sh/research-panel.md ~/.claude/commands/sh/personal-development-panel.md experts/fixtures/seeded-findings/noncode-panel.md
git commit -m "feat(panels): apply source-citation grounding+refute to 4 non-code panels (AC-01, AC-02)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Redefine disjoint lenses in multi-reviewer panels (AC-04)

**Files:**
- Modify: `~/.claude/skills/sh-4-reviewer-panel/SKILL.md` (Step 2 reviewer definitions).
- Modify: `~/.claude/commands/sh/architecture-panel.md` (focus-area overlap note) — only the doc prose, not the YAML experts.
- Test: grep assertion that lens categories are unique.

**Interfaces:**
- Consumes: `experts/PANEL_PROTOCOL.md` `## Disjoint Lenses` (Task 1).
- Produces: `sh-4-reviewer-panel` Step 2 reviewers each own exactly one of {correctness/error-paths, concurrency/resource-lifecycle, contracts-vs-callers, test-adequacy}.

- [ ] **Step 1: Write the uniqueness assertion (failing today)**

Today the 4 reviewers are code-reviewer(bugs/security), architecture, analyze(smells/security/perf), codex(style) — "security" appears in 2+, so categories overlap.

Run: `grep -cE 'security' ~/.claude/skills/sh-4-reviewer-panel/SKILL.md`
Expected today: ≥2 (overlap present).

- [ ] **Step 2: Rewrite Step 2 reviewer definitions to disjoint lenses**

In `sh-4-reviewer-panel/SKILL.md`, replace the "Why 4 reviewers" list and the 4 reviewer dispatch blocks so each maps to one lens (per PANEL_PROTOCOL ## Disjoint Lenses):
- Reviewer A → **correctness / error-paths** (logic bugs, unhandled errors, wrong results)
- Reviewer B → **concurrency / resource-lifecycle** (races, leaks, unclosed handles, ordering)
- Reviewer C → **contracts-vs-callers** (does the change honor callers/tests; resolve via Serena `find_referencing_symbols`)
- Reviewer D (codex) → **test-adequacy** (are changed paths covered) — AND serves as refute engine in Task 6.

Add a line at the top of Step 2: `Apply experts/PANEL_PROTOCOL.md ## Disjoint Lenses — no reviewer files another lens's category.`

- [ ] **Step 3: Verify lenses are disjoint**

Run: `grep -cE 'correctness / error-paths|concurrency / resource-lifecycle|contracts-vs-callers|test-adequacy' ~/.claude/skills/sh-4-reviewer-panel/SKILL.md`
Expected: `4` (each lens named exactly once in the reviewer definitions).

- [ ] **Step 4: Commit**

```bash
git add ~/.claude/skills/sh-4-reviewer-panel/SKILL.md ~/.claude/commands/sh/architecture-panel.md
git commit -m "feat(panels): redefine reviewers as 4 disjoint lenses (AC-04)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Kill blind auto-apply in 4-reviewer panel (AC-03)

**Files:**
- Modify: `~/.claude/skills/sh-4-reviewer-panel/SKILL.md` (Step 4).
- Test: `experts/fixtures/seeded-findings/nonmechanical-fix.md`.

**Interfaces:**
- Consumes: refute stage output (Task 1 `## Refute Stage`), disjoint findings (Task 4).
- Produces: Step 4 applies a finding only if (verified AND mechanical); else surfaces.

- [ ] **Step 1: Write the seeded non-mechanical Fix (failing test)**

Create `experts/fixtures/seeded-findings/nonmechanical-fix.md`:

```markdown
# A Fix-* finding that is NOT mechanical — must be SURFACED, not auto-written:
FILE: src/auth.py:55 | MAJOR | "Change auth check from `==` to constant-time compare to fix timing attack" | Fix
# This is a logic/security change, not a typo/import/rename. Step 4 must surface it for confirmation.
```

- [ ] **Step 2: Verify Step 4 currently auto-applies everything**

Run: `grep -nA3 'Auto-fix Fix' ~/.claude/skills/sh-4-reviewer-panel/SKILL.md`
Expected today: text says "all Fix-* findings are auto-applied without asking" → confirms the gap.

- [ ] **Step 3: Rewrite Step 4 with the two-gate guard**

Replace Step 4's auto-apply text with:

```markdown
### Step 4 — Apply only verified + mechanical Fix-* findings (AC-03)

A Fix-* finding is auto-applied ONLY IF BOTH hold:
1. It survived the Refute Stage (PANEL_PROTOCOL ## Refute Stage).
2. It is mechanical: unused import, rename, typo, formatting, dead-code removal — no behavior change.

For each verified Fix-* finding:
- If mechanical → apply directly (Edit/Write), mark ✓ Applied.
- If non-mechanical (logic, security, control-flow, API change) → DO NOT write. Surface it under Step 5 for confirmation.

Never auto-apply a finding that changes behavior, even if classed Fix.
```

- [ ] **Step 4: Verify the guard is present**

Run: `grep -cE 'mechanical|DO NOT write|both hold|BOTH hold' ~/.claude/skills/sh-4-reviewer-panel/SKILL.md`
Expected: ≥3.

- [ ] **Step 5: Behavioral check**

Run: `claude -p "/sh:4-reviewer-panel --diff ~/projects/20_agentflow/experts/fixtures/seeded-findings/nonmechanical-fix.md" 2>&1 | tail -30`
Expected: the constant-time-compare finding is SURFACED for confirmation, not reported as auto-applied/written to disk.

- [ ] **Step 6: Commit**

```bash
git add ~/.claude/skills/sh-4-reviewer-panel/SKILL.md experts/fixtures/seeded-findings/nonmechanical-fix.md
git commit -m "feat(panels): gate auto-apply on verified+mechanical only (AC-03)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Wire Codex as the refutation engine (AC-05)

**Files:**
- Modify: `~/.claude/skills/sh-4-reviewer-panel/SKILL.md` (Step 2 Reviewer D + a new refute hook in Step 3).

**Interfaces:**
- Consumes: collected findings from Step 2 (Task 4), `## Refute Stage` (Task 1).
- Produces: `codex exec` invocation that takes the merged findings and returns a refuted/survives verdict per finding — replacing its old "style/naming only" role.

- [ ] **Step 1: Verify Codex is currently style-only (failing test)**

Run: `grep -nA3 'codex' ~/.claude/skills/sh-4-reviewer-panel/SKILL.md | grep -iE 'style|naming|convention'`
Expected today: matches → codex is scoped to style/naming.

- [ ] **Step 2: Add a Codex refute step**

In Step 3 (merge), after collecting findings, insert before the triage table:

```markdown
**Refute pass (Codex as engine, AC-05):** Pass the merged findings to codex for refutation:

\`\`\`bash
codex exec "For each finding below, read the cited file:line in this repo and decide: does the exact code support the finding? Output per finding: SURVIVES or REFUTED + the line you read. Default REFUTED if the cited line does not clearly support it.

<merged findings list>"
\`\`\`

Drop every REFUTED finding before building the triage table. Only SURVIVES findings proceed to Step 4.
```

Also update Step 2 Reviewer D note: codex's primary role is the refute engine above; test-adequacy lens is secondary.

- [ ] **Step 3: Verify Codex is wired to refute, not just style**

Run: `grep -cE 'SURVIVES|REFUTED|refut' ~/.claude/skills/sh-4-reviewer-panel/SKILL.md`
Expected: ≥3.

- [ ] **Step 4: Behavioral check (end-to-end)**

Run: `claude -p "/sh:4-reviewer-panel --diff ~/projects/20_agentflow/experts/fixtures/seeded-findings/code-panel.md" 2>&1 | tail -40`
Expected: the false `registry.yaml has no name field` finding is marked REFUTED by the codex pass and does not appear in the final triage table.

- [ ] **Step 5: Commit**

```bash
git add ~/.claude/skills/sh-4-reviewer-panel/SKILL.md
git commit -m "feat(panels): use codex exec as refutation engine, not style voice (AC-05)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Done criteria (maps to US-PANEL-01 ACs)

- AC-01 Grounding → Tasks 1, 2, 3 (protocol + 6 code panels + 4 non-code panels load it; Serena/Read only; no new packages).
- AC-02 Adversarial verify → Task 1 (`## Refute Stage`) + behavioral checks in Tasks 2, 3.
- AC-03 Kill blind auto-apply → Task 5.
- AC-04 Disjoint lenses → Tasks 1 (`## Disjoint Lenses`) + 4.
- AC-05 Codex as verifier → Task 6.
