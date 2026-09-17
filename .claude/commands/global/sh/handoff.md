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
>
> **A second consumer reads by heading prefix.** The Hermes adapter's
> `POST /v1/claude/resume` (`hermes_adapter/claude_routes.py`,
> `_extract_handover_sections`) takes the newest handover and extracts exactly
> two sections with `line.startswith("## Open Items")` and
> `line.startswith("## Resume Checklist")`, stop-at-next-`##`. Any other
> heading text yields an empty section. This drifted too: the template said
> `## Known gaps, deliberately not closed` until 2026-09-17, so 109 of the 226
> September handovers handed the adapter an empty Open Items. The gate now
> asserts both prefixes are present in the template.

## Where the file goes — NOT the project root

```
~/projects/00_Governance/HANDOVER-<project>-<YYYY-MM-DD-HHMM>.md
```

`<project>` is the directory name (`60_funroadtrip`, `20_CONSIGLIERE`), not a
path. Take the timestamp from the clock **once** and use that one value for
both the filename and the `# HANDOVER — … — <YYYY-MM-DD HH:MM>` heading:

```bash
STAMP=$(date +%Y-%m-%d-%H%M)     # one call; filename AND heading derive from $STAMP
```

The wrong idiom is reading the time twice — a `date` call for the filename and
a second one (or a time remembered from earlier in the conversation) for the
heading — which lets the two disagree. Measured 2026-09-17 with
`python3 ~/projects/00_Governance/scripts/handover_store_lint.py --since 2026-09`:
2 of 226 September handovers carry a heading stamp that does not match their
filename stamp (one by 27 minutes); across the whole store it is 174 of 2135,
105 of them from May 2026 alone, before this rule existed. `resume-handover`
parses the project token out of the FILENAME; a stamp copied from a previous
handover's name, or typed from memory, resolves to the wrong session.

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

## Open Items — known gaps, deliberately not closed

What was left, and why it was a choice rather than an oversight. Include
carried-item counts ("carried across four sessions") — recurrence is signal.
(Heading prefix `## Open Items` is load-bearing — see the contract note at the
top. Do not rename it to "Known gaps" / "Carry forward" / "Left open".)

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

**Probe every ref the handover makes a claim about — `main` included.** The
wrong idiom is a Premises block whose only ref probe is `git rev-parse --short HEAD`
or `git log -1`: it passes on the feature branch and asserts nothing about
`main`. On 2026-08-09 a `60_funroadtrip` handover stated "`main` untouched at
`22c97bd`"; its premises probed only the branch, all passed, and `main` had in
fact been merged to `f621755` mid-story — the premise gate cleared and the
stale claim silently under-scoped the whole-branch review to the unmerged
commits. Measured 2026-09-17 with
`python3 ~/projects/00_Governance/scripts/handover_store_lint.py`: 104 of the
447 handovers in the store that carry a `rev-parse` premise probe HEAD only
(21 of 177 in September alone). If the text says "main untouched at X",
"not yet merged", or "branched from Y", the block carries the matching
`git rev-parse main   # expect X` line.

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
   **The handover is the LAST artifact of the session.** The wrong idiom is
   writing it at the start of `/lightsout` and then continuing to work: on
   2026-04-30 a SHIELD-tablet handover was written at 13:55 and the session
   then pushed the DS2 blobs at 14:02, so the next session resumed on
   "blobs not pushed yet" and re-diagnosed a state that no longer existed
   (KP-4893, KP-1420). If any state changes after the file is written —
   a commit, a push, a device flash — write a second, later-stamped handover
   that names the first as superseded. Never edit the first in place.
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
- **The Premises block is mandatory and must be executable**, and it probes
  every ref the prose names — `HEAD`-only probes are the 2026-08-09 failure.
- Every SHA in the document was printed by a `git rev-parse` / `git log` run
  **in this session, after the last commit**. A SHA copied from a `git log`
  output earlier in the conversation is stale the moment anything is committed
  after it — that is an assumed SHA wearing a real one's clothes.
- Prefer carrying a gotcha forward one session too many over dropping it early.
- If the session guard forced the stop mid-task, say so and name the clean
  boundary — a deliberate stop reads very differently from an abandoned one.
