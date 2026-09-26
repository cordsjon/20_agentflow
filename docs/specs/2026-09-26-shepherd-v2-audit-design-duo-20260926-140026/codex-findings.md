## Findings — CODEX

**CRITICAL:** (none)

### [IMPORTANT] Score freshness ignores uncommitted specification changes
- What: The proposed revision check accepts an old panel score when the specification has changed without a new commit.
- Where: US-SH2-02, “`<spec-sha>` must equal `git log -1 --format=%h -- <spec path named in the entry>`”.
- Why it matters: Editing the specification leaves that command’s result unchanged, allowing materially changed requirements to pass using earlier review evidence.
- Suggested fix: Bind the score to a digest of the reviewed specification contents and compare it with the current file. Alternatively, require the recorded commit and reject staged, unstaged, or untracked changes to the specification. Add a fixture for edits made after scoring but before committing.
- Confidence: high

### [IMPORTANT] Entry boundaries can include unrelated backlog sections
- What: The parser contract does not terminate entries at higher-level headings or define how bold titles interact with Markdown heading levels.
- Where: US-SH2-02, “An entry spans from the heading or bold-title line that contains the id to the next line of the same level”.
- Why it matters: A story under `###` followed by a new `##` section can absorb unrelated content, potentially borrowing acceptance criteria or panel evidence from another entry.
- Suggested fix: Define supported title forms, terminate heading-based entries at the next heading of equal or higher level, and specify boundaries for bold-title entries. Define AC ownership and count identifier matches only in recognized entry titles. Add fixtures covering section transitions, mixed title forms, and references to other story IDs.
- Confidence: high

### [IMPORTANT] One rejected commit does not validate every DOD gate
- What: The acceptance test proves refusal by one gate, while the design principle requires a positive control for every gate.
- Where: Design principles, “Every gate in v2 … with a positive control”; US-SH2-03 AC-2, “a commit that violates one named v4 gate is rejected”.
- Why it matters: The test can pass while other gates are ineffective, and a commit-only scenario does not exercise gates attached to pre-push.
- Suggested fix: Identify the required gates and their hook events, then require a failing control for each gate, either through referenced existing tests or new controls. Exercise pre-push gates with a push to a disposable local remote, and retain passing controls.
- Confidence: high

### [IMPORTANT] Runtime reconciliation protects only the first promotion
- What: The spec requires reconciliation before the first sync but gives no conflict policy for subsequent runtime edits.
- Where: Design principles, “Runtime is the direction of truth for already-promoted skills”; US-SH2-04 AC-2, “Before the first sync … only then may bundle → runtime copies run”.
- Why it matters: A later bundle-to-runtime copy can overwrite new runtime work even though the initial migration satisfied every acceptance criterion.
- Suggested fix: Record the last synchronized content digest for each managed skill. Before every outward copy, detect runtime changes since that baseline and require reconciliation before overwriting them. Test a runtime edit made after a successful initial sync.
- Confidence: high

### [IMPORTANT] Manifest statuses lack an executable lifecycle
- What: The manifest labels skills as global, repo-local, or retired without defining the operations that establish those states.
- Where: Audit finding 4, “There is no promotion tool”; US-SH2-04, “`global` / `repo-local` / `retired`”; US-SH2-05, retirement candidates receive “status `retired`”.
- Why it matters: A checker can report missing global installations without installing them, and marking an installed skill retired can leave it discoverable and usable indefinitely.
- Suggested fix: Specify a promotion command or a concrete manual procedure, including installation, verification, and retirement behavior. Define whether retired skills move outside discovery directories and how previously managed runtime copies are removed or archived. Require that unrelated runtime skills remain untouched.
- Confidence: high

### [IMPORTANT] Remaining clone inventories omit potentially unique Git state
- What: The deletion checks cover commits on `master` and working-tree status but omit other branches, stashes, and ignored files.
- Where: US-SH2-06, “the check is `git log origin/master..master` + `git status --porcelain` per clone”.
- Why it matters: Both commands can report nothing to preserve while another local branch, a stash, or an ignored local artifact contains unique work that deletion would destroy.
- Suggested fix: Before requesting deletion approval, inventory all local branches and relevant refs against preserved upstream history, list stashes, and inspect ignored files. Record a durable disposition for anything unique, or create and verify an archive covering Git state and required local files.
- Confidence: high

**NIT:** (none)

## Self-flagged uncertainty

- The bundle omits representative backlog entries, so compatibility with the existing format cannot be assessed; the parser finding concerns the stated contract.
- Governance hook implementations and existing tests were not supplied. They may already provide the missing per-gate controls, but the spec does not identify them.
- No promotion implementation or complete skill-directory contents were supplied. Existing external tooling might provide lifecycle behavior, although the audit explicitly says no promotion tool exists.
- The bundle does not establish that the remaining clones contain other branches, stashes, or valuable ignored files. The finding concerns the completeness of the deletion preconditions, not confirmed data loss.
