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
