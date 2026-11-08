# Panel Protocol (shared)

Every `sh:*-panel` skill applies this protocol. Read this file at panel start and follow every section before emitting findings.

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

## Invocation

Gate callers run a panel as `claude -p "/sh:<panel> --ticket <US-ID> [--threshold 7.0] [--lenses a,b]"`
(00_Governance `scripts/skill_runner.sh`; `backlog_dor_pipeline.run_stage_e_panel`). The flags arrive
as prompt text, not parsed options; every `sh:*-panel` honours them the same way:

- `--ticket <US-ID>`: the artifact is that story in the current repo's `BACKLOG.md` — the entry body
  plus its linked spec file when one exists. Locate it; do not ask for a paste.
- `--threshold <n>`: report the raw score in `PANEL-VERDICT`; the caller applies the threshold.
- `--lenses <csv>`: spec-panel only; other panels ignore it. For each name read
  `/Users/jcords-macmini/projects/20_agentflow/experts/lenses/<name>.yaml`: append its `experts` to the
  roster (cap `max-experts` 7; 9 when two or more lenses attach) and run each `checklist` item as a
  mandatory pre-scoring check — a miss is a MAJOR finding before deliberation, the same way
  `pre-scoring-checks` in the panel YAML work. Lens packs have no score line of their own; they are
  part of the spec-panel score.
- Which panels and lenses a story needs is decided by `python3 ~/projects/00_Governance/scripts/panel_policy.py
  resolve <BACKLOG.md> <US-ID> --json` (`panels`, `lenses`, `track`). The panel never chooses for itself.
