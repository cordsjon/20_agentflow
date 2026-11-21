---
name: agentflow-code-review-gate
description: Quality-gate Stage-2 code review. Reviews a diff across four lenses (correctness bugs, CLAUDE.md adherence, missed simplifications, stale docs) in one pass and emits a machine-readable REVIEW-VERDICT line. Not for interactive use — run headless, `claude -p "/agentflow:code-review-gate"` with the diff on stdin (its original caller, quality_gate.py, was removed 2026-09-09). Does NOT invoke the /code-review plugin.
---

# Code-Review Gate (Stage 2)

**Gate:** Must pass BEFORE a ticket advances past code review.

This skill is the quality gate's owned, diff-shaped code reviewer. It does NOT
invoke the `/code-review` plugin (that is PR-centric, comments on GitHub, and
fans out 5+ subagents — wrong shape and side-effects for a gate).

## Procedure

1. You receive a unified diff on **stdin**.
2. Review the diff yourself in a single structured pass across **four lenses**,
   considering only lines the diff modifies:
   - **Correctness** — real bugs: null/None derefs, off-by-one, wrong
     conditionals, unhandled errors, resource leaks, race conditions.
   - **CLAUDE.md adherence** — violations of the repo's stated rules (atomic
     writes, no bare except, status-check before .json(), etc.).
   - **Missed simplifications** — only those a senior engineer would block on,
     not stylistic nits.
   - **Stale docs** — the diff changes a code contract (renamed/removed symbol,
     changed signature, flag, env var, default, port, or path) that a doc/comment
     visible **in this same diff** still describes the old way. Blocking only when
     the contradiction is inside the diff (a changed line beside stale prose, or a
     doc hunk left un-updated). Do NOT go hunting the wider repo for stale docs —
     that is out of a diff-shaped gate's scope; flag only what the diff itself
     exposes. (Highest-yield lens after correctness in real pipelines.)
3. A finding is **blocking** only if it is a real defect on a modified line.
   Ignore: pre-existing issues, nitpicks, lint/type/format, untouched lines,
   general coverage/docs concerns not mandated by CLAUDE.md, likely false
   positives. Count surviving blocking findings → `N`.
4. Print each finding as **one JSON object on its own line**, BEFORE the verdict
   line, so a caller can parse and recheck it:

   ```
   {"path": "scripts/db.py", "line": 42, "severity": "blocking", "summary": "SQL built from user input with an f-string."}
   ```

   - `path` is repo-relative, without the diff's `a/` or `b/` prefix.
   - `line` is the new-file line number of the `+` line the defect is on.
   - `severity` is `blocking` (counts toward `N`) or `advisory` (never counts).
   - `summary` is one sentence.

   Prose lines are allowed before the findings, but any line that starts with
   `{` must be a valid finding object: a malformed one fails the prefilter's
   recheck closed.

## Output Contract (machine-readable verdict)

The caller reads the **verdict from stdout, not the exit
code**. Emit, as the **final line** and **exactly once**, one of:

```
REVIEW-VERDICT: PASS
REVIEW-VERDICT: FAIL: <machine_reason>
```

- `PASS` only when `N == 0`.
- On failure, `<machine_reason>` is `<N>_blocking`, e.g. `3_blocking`, where
  `N` equals the number of `"severity": "blocking"` finding lines you printed.
  The prefilter's recheck fails closed (`recheck_count_mismatch`) when the count
  and the printed findings disagree.
- Emit the line literally, once, as the **last non-empty line** of your output.
  The gate parses only that final line — do NOT place any text after it, and do
  NOT repeat the literal string `REVIEW-VERDICT:` anywhere earlier. Omitting the
  line → gate fails closed `code_review_no_verdict`.
- Your exit code is ignored for the verdict; a non-zero exit is read as
  `code_review_tooling_failed`, never a veto.

## Prefilter pipeline

`~/projects/00_Governance/scripts/review_prefilter.py` wraps this gate in plain
code (US-REVGATE-PREFILTER-01, decision Q1882). It does two things the model
should not decide:

- **`bundle <diff>`** splits the diff into one bundle per top-level directory
  and drops lockfiles, generated files and binaries. It prints
  `{"bundles": [{"dir", "files", "diff"}]}`.
- **`recheck (--diff <diff> | --bundles <bundles.json>) <gate-output>...`**
  keeps a finding only when its `path:line` is a `+` line of the diff, then
  prints the kept findings and one recomputed `REVIEW-VERDICT` line. Each
  dropped finding is listed on stderr with its reason: `context`, `removed`,
  `untouched` or `unknown-path`. It fails closed on an unparsable diff
  (`recheck_bad_diff`, exit 2), a missing gate output
  (`recheck_bundle_count_mismatch`), a gate output without a verdict
  (`code_review_no_verdict`), a malformed finding line
  (`recheck_malformed_finding`) and a gate FAIL its findings do not back
  (`recheck_count_mismatch`).

Run it on a diff file. It needs `jq`, and `timeout` from GNU coreutils
(`brew install coreutils` on macOS):

```bash
GOV=~/projects/00_Governance/scripts/review_prefilter.py
DIFF=change.diff                      # e.g. git diff main...HEAD > change.diff
OUT=$(mktemp -d)
python3 "$GOV" bundle "$DIFF" > "$OUT/bundles.json"
n=$(jq '.bundles | length' "$OUT/bundles.json")
outs=()
for ((i = 0; i < n; i++)); do
  jq -r ".bundles[$i].diff" "$OUT/bundles.json" \
    | timeout 600 claude -p "/agentflow:code-review-gate" --output-format json --tools "" \
    > "$OUT/run$i.json"
  jq -r '.result // ""' "$OUT/run$i.json" > "$OUT/run$i.out"   # timed out: empty, fails closed
  outs+=("$OUT/run$i.out")
done
python3 "$GOV" recheck --bundles "$OUT/bundles.json" "${outs[@]}"
```

`--tools ""` gives each gate run no tools, so text planted in the diff cannot
act on the filesystem. For a single unbundled run, pipe the whole diff into
one gate run and use `recheck --diff "$DIFF" run.out`.

**Trade-off.** A bundle only sees its own directory. A finding that needs two
directories at once is lost, for example a stale-docs contradiction between a
flag renamed in `scripts/` and prose in `docs/`.

**Residual risk.** Recheck only removes findings. A prompt injection in the
diff that makes the gate stay silent is not caught here.
