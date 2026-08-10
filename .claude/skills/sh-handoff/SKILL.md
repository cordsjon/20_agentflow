---
name: sh-handoff
description: Write a session HANDOVER to the centralized store so the next session can resume without context loss. Captures premises (executable), shipped work, gotchas, measurements, open items, and a resume checklist. Triggers — /sh:handoff, "write the handover", session guard firing, end of session.
---

# Handoff — Context Save

Produce a HANDOVER document capturing full session state, in the format
`resume-handover` actually reads.

> **This skill and `resume-handover` are two halves of one contract with no
> compiler between them.** The write path below MUST match that skill's search
> path. `scripts/handover_contract_gate.py` in `00_Governance` asserts they
> agree and fails CI if they drift — do not change the path here without
> running it. (History: the two disagreed from 2026-05-31 to 2026-08-10 —
> this skill wrote `HANDOVER.md` in the project root while `resume-handover`
> searched `00_Governance/HANDOVER-<project>-<timestamp>.md`. The result was
> 16 filed Skill-Unused debt entries across 8 projects, because writing the
> handover by hand was genuinely more correct than invoking this skill.)

## Where the file goes — NOT the project root

```
~/projects/00_Governance/HANDOVER-<project>-<YYYY-MM-DD-HHMM>.md
```

`<project>` is the directory name (`60_funroadtrip`, `20_CONSIGLIERE`), not a
path. Derive the timestamp from the actual clock, never from a guess.

**APPEND-ONLY. Never overwrite a previous handover.** The store is timestamped
and `resume-handover` resolves "newest" by mtime across ~1700 files. Two
handovers from one session (e.g. a session-guard stop at 11:30 and a wrap-up at
11:45) are both legitimate and both readable — the later one states which it
supersedes. Overwriting destroys the history the store exists to keep.

**Do NOT write `HANDOVER.md` in the project root.** Eleven such files exist from
earlier versions of this skill, some months stale, and a session that trusts one
resumes from the wrong commit. If the project you are handing off has one, say
so in the handover so it can be deleted deliberately — do not update it.

## Template

Adapt section by section — omit what does not apply rather than emitting empty
headings. The **Premises block is mandatory**; everything else flexes.

```markdown
# HANDOVER — <project> — <YYYY-MM-DD HH:MM>

**Repo:** `~/projects/<project>` (note any symlink/mount quirk that makes the
path look wrong)
**Branch:** `<branch>` @ `<sha>`, pushed/unpushed, tree clean/dirty
**Why this exists:** session guard at N% | wrap-up | task complete | blocked
(If it supersedes an earlier handover from the same session, name that file.)

## What shipped this session

| Commit | What |
|---|---|
| `<sha>` | <one line, with the US/spec id if there is one> |

## Decisions made (operator rulings)

Numbered. For each: what was decided, and WHY the alternative was rejected.
An override recorded as an override, never as a silent tick.

## Things that will bite you if you do not know them

Numbered gotchas. Each names a specific way the next session fails SILENTLY
while looking correct. Carry forward the ones still true, drop the resolved
ones. This is the section that saves the most time and the one most often
under-written.

## Measurements taken this session (do not re-derive)

Numbers with their units, conditions, and what they justify. The point is that
the next session must not spend an hour re-measuring what is already known.
Mark anything unmeasured as unmeasured — never fabricate.

## Known gaps, deliberately not closed

What was left, and why it was a choice rather than an oversight. Include
carried-item counts ("carried across four sessions") — recurrence is signal.

## Payload artifacts

Every file holding research, compiled lists, or agent output produced this
session. If a payload exists ONLY in the conversation: STOP, write it to disk
now, then list the path. "In-transcript only" is a failed handover.
(2026-08-03: a 50-company research corpus was lost this way and had to be
recovered from raw transcript JSONL.)

## Premises (verify before acting) — MANDATORY

```bash
cd ~/projects/<project>
git rev-parse --short main && git rev-parse --short origin/main   # expect <sha> both
git status --porcelain                                            # expect clean
<the project's canonical test command>                            # expect <N> passed
<any idempotent CLI that asserts corpus/state is unchanged>       # expect 0 changed
```

Every line is EXECUTABLE and carries its EXPECTED OUTPUT as a comment. This is
what separates a handover from a status report: the next session runs this block
and learns in 60 seconds whether the world still matches the document. A premise
without an expected value is not a premise.

## Resume Checklist

- [ ] Run the Premises block above
- [ ] <the next task, concretely — file paths and the first action>
- [ ] <do-NOTs: what must not be re-opened, re-ported, or trusted>
```

## Process

1. **Gather git state from reality** — `git rev-parse`, `git status --porcelain`,
   `git log --oneline`. Never assume a SHA.
2. **Build the Premises block and RUN IT** — every command must have been
   executed this session with its real output pasted as the expected value. A
   premise you have not run is a guess, and a wrong premise is worse than none.
3. **Harvest gotchas** — anything that cost you time this session, especially
   things that looked correct and were not.
4. **Dump payloads to disk** — scan for research/compiled output living only in
   conversation; write each to a file and list the path.
5. **Write to the centralized store** at the path above, with the real timestamp.
6. **Commit and push** — `git add` then
   `git commit -F <msgfile> -- <explicit path>` (bare `git commit` is blocked by
   the governance guard; `-F -` with a heredoc does NOT work in the
   explicit-paths form — write the message to a file).

## Optional inputs — read only if present

`TODO-Today.md`, `DONE-Today.md`, `.autopilot`, `BACKLOG.md`. Most repos have
none of these; skip silently when absent. Earlier versions of this skill
hardcoded them into the process and the resume checklist, which made three of
five checklist items unfollowable in a normal repo — a large part of why the
skill went unused.

## Key rules

- **Append-only, centralized store, timestamped filename.** Not the project root.
- **The Premises block is mandatory and must be executable.**
- Git state comes from real command output, never assumption.
- Prefer carrying a gotcha forward one session too many over dropping it early.
- If the session guard forced the stop mid-task, say so and name the clean
  boundary — a deliberate stop reads very differently from an abandoned one.
