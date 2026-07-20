# nosignups-catalog-sync — Design Spec

**Date:** 2026-07-20
**Status:** Panel-passed 7.7/10 (2026-07-20, sh:spec-panel, 10 findings auto-fixed)
**Epic:** US-AF-NOSIGNUPS-CATALOG-01 (single US, ~1 session of work)
**Home:** `~/projects/20_agentflow/scripts/nosignups_catalog.py`

## 1. Problem

nosignups.net is a curated directory of 222 no-signup, in-browser, open-source
tools. It exposes no API — the SPA renders one static JSON file:

    https://raw.githubusercontent.com/BraveOPotato/FckSignups/refs/heads/main/tools.json
    (shape: { categories: [10], tools: [222] }; verified 2026-07-20, ~95 KB)

We want that catalog (and later, similar directories) flowing into our
toolchain weekly: as structured JSON for pipelines, as a searchable QMD
collection for discovery, and as "discoverable" entries in the cli-registry
launchpad. The listed tools are overwhelmingly browser UIs — **not** callable
endpoints — so the design must never claim otherwise.

Out of scope: any attempt to invoke the listed tools programmatically; a
search/browse CLI UX; a config-file/plugin system for sources.

## 2. Architecture

One stdlib-only Python script, three sinks, one weekly dagu DAG.

```
dagu (Mon 04:30) → python3 nosignups_catalog.py sync
      │  per source: conditional-GET (ETag) → 304 ⇒ no-op
      ▼
  normalize → uid "<source>:<toolid>" → classify() → kind
      ├── Sink A  data/tool_catalog.json + stdout (emit)
      ├── Sink B  data/tool-directories/<source>/<toolid>.md  (QMD)
      └── Sink C  ~/.hermes/cli-registry.db  (kind ∈ cli|js-lib|self-host only)
```

**Source seam (multi-source ready, no framework):** an in-code list
`SOURCES = [{name, url, normalize_fn}]`. Adding a directory source = append
one dict + one normalize function. Sinks, classifier, diff/prune, and the DAG
are source-agnostic — they only see normalized records.

**Normalized record (contract all sinks read):**

```json
{ "uid": "nosignups:excalidraw", "source": "nosignups", "name": "...",
  "description": "...", "url": "...", "category": "...", "tags": [],
  "github": "...", "license": "...", "stars": 0, "featured": false,
  "kind": "browser-only" }
```

**Classifier** `classify(record) -> kind`, honest by default:

| kind | meaning | rule (first match wins) |
|---|---|---|
| `cli` | installable command-line tool | tags/description regex for cli/command-line AND has github |
| `js-lib` | importable JS/WASM library | wasm/library/npm signals AND has github (e.g. ffmpeg.wasm) |
| `self-host` | runs as a service you host | self-host/docker signals AND has github |
| `browser-only` | interactive web UI only | **default** — no signal or no github ⇒ browser-only |

A github link is a hard precondition for every non-default kind (this is the
invariant AC-4 tests). Expected yield: ~200+ browser-only, low tens combined
across the other three kinds (estimate; will drift with upstream). False
negatives (a real CLI classified browser-only) are acceptable; false positives
(a browser app registered as callable) are not — hence default-down.

## 3. Sinks

**A — JSON (pipeline feed).** `emit` is stateless: fetch + normalize +
print to stdout (network required, no cache read, no sink writes). `sync`
writes the same array atomically (tempfile + `Path.replace`) to
`data/tool_catalog.json` (source-agnostic name — source #2 lands in the
same artifact). No other side effects.

**B — QMD collection (discovery).** One markdown file per tool:
YAML frontmatter (name, source, url, github, license, stars, category, tags,
kind) + description body. Files under `data/tool-directories/<source>/`.
`toolid` is third-party input used as a filename: it MUST match
`^[a-z0-9][a-z0-9._-]{0,63}$` or the record is rejected with a logged
warning (path-traversal guard — a hostile id like `../../x` must never
reach a path join). The same validation gates registry slugs.
One-time setup:
`qmd collection add ~/projects/20_agentflow/data/tool-directories --name tool-directories`
(category-named, so future sources share it; `--name` passed explicitly —
the name is otherwise derived from the path). Writes are atomic; prune
deletes the file.

**C — cli-registry (discoverable launchpad).** Only `kind ∈
{cli, js-lib, self-host}` rows. Column mapping (schema verified 2026-07-20):

| column | value |
|---|---|
| `slug` (PK) | `ns-<toolid>` (namespaced; never collides with real CLIs) |
| `bucket` | `discoverable` ← **the contract for filtering these out** |
| `source_class` | `external:<source>` |
| `launch_spec` | `install:<github-url>` (NOT NULL column; this is an install hint, not a runnable spec) |
| *(NOT NULL set)* | `slug, lang, launch_spec, description, health_status, enabled, a2a_invokable, not_standalone` — all supplied above |
| `enabled` / `a2a_invokable` | `0` / `0` — invisible to the Hermes a2a bot |
| `health_status` | `unknown` |
| `lang` | `unknown` (NOT NULL column; source data has no language field) |
| `description`, `project`, `path` | description from record; `project='external'`, `path=''` |

Writer: direct sqlite upsert inside the script (`INSERT ... ON CONFLICT(slug)
DO UPDATE`), with `PRAGMA busy_timeout=5000` and all rows in **one
transaction** — the DB is live-consumed (hermes-adapter), so an unattended
04:30 write must tolerate a concurrent reader/writer instead of dying on
`SQLITE_BUSY`. **Not** `register_cli.py` — that tool is built for repo-local
CLIs one-at-a-time post-commit; reusing it dozens of times per sync would
abuse its contract. Same table, clearly-scoped writer, `bucket='discoverable'` marks
ownership. An optional `shutil.which()` probe may flip `health_status` to
`ok` when a matching binary exists locally; absence never deletes a row.

## 4. Diff-aware sync & prune (per source)

State: `~/.local/state/nosignups-catalog/<source>.json` →
`{ etag, payload_sha256, uids: [...], last_sync_iso }`. If upstream stops
sending an ETag, freshness falls back to comparing `payload_sha256`
(fetch still happens, but sinks are skipped on hash match).

1. Conditional-GET with stored ETag. `304` ⇒ log `"<source>: unchanged"`,
   exit 0, touch nothing.
2. Changed ⇒ normalize, diff `uids` vs state: added / changed / removed.
   A non-304 run **rewrites all sink artifacts idempotently** (every md
   file, the JSON artifact, every registry upsert) — the diff exists for
   prune (step 3) and the changelog, not for selective writes.
3. Removed uid ⇒ delete its QMD `.md`; registry row is **soft-removed**
   (row kept, description prefixed `[REMOVED upstream]`, stays `enabled=0`).
   Rationale: the user may have installed the tool; hard-delete loses that.
4. Write new state atomically — **only after every sink write for that
   source succeeded**. This ordering is load-bearing: a crash mid-sync
   leaves old state, so the next run redoes the full write and heals.
   Print one-line changelog per source: `nosignups: +3 ~1 -0 (222→225)`.

Diff and prune are scoped per source — syncing source A can never delete
source B's artifacts.

Failure behavior: network error or malformed JSON ⇒ log, exit non-zero,
**leave all sinks and state untouched** (last-good wins). No partial writes:
sinks are written only after the full payload parses and normalizes. No bare
`except Exception`; HTTP status is checked before parsing.

## 5. DAG

`~/.config/dagu/dags/nosignups-catalog-sync.yaml`, in the dominant house
style (85% of the 135 existing DAGs): comment-header-only — identity from
filename + `# nosignups-catalog-sync — <desc>` header comment, **no**
top-level `name:`/`description:` YAML keys — plus a single bash step with
absolute paths:

- `schedule: "30 4 * * 1"` (Mon 04:30 — weekly freshness floor)
- step: `python3 /Users/jcords-macmini/projects/20_agentflow/scripts/nosignups_catalog.py sync`
- stdlib-only script ⇒ system `python3`, no venv coupling.
- No ports, no services (portmanager not applicable).

## 6. CLI surface

```
nosignups_catalog.py sync                  # full pipeline (what the DAG runs)
nosignups_catalog.py sync --dry-run        # fetch+diff+changelog, write nothing
nosignups_catalog.py emit                  # normalized JSON to stdout only
nosignups_catalog.py classify              # per-kind counts + non-browser-only list
```

## 7. Acceptance criteria (US-AF-NOSIGNUPS-CATALOG-01)

- **AC-1** `sync` on a fresh machine creates ≥200 QMD md files, the JSON
  artifact, state file, and only `kind≠browser-only` registry rows, all with
  `bucket='discoverable'`, `enabled=0`, `a2a_invokable=0`.
- **AC-2** Immediate re-run hits ETag 304 and exits 0 with zero sink writes
  (verify via mtimes / sqlite `updated_at`).
- **AC-3** Simulated upstream removal (fixture) deletes the QMD file and
  soft-removes the registry row; other sources' artifacts untouched.
- **AC-4** `classify` never emits a `cli|js-lib|self-host` kind for a record
  lacking a github link; spot-check: excalidraw ⇒ `browser-only`,
  ffmpeg.wasm ⇒ `js-lib`.
- **AC-5** `nosignups:excalidraw` appears in the top-5 results of
  `qmd query "whiteboard sketch diagrams"` scoped to the `tool-directories`
  collection (deterministic rank threshold, not "relevant").
- **AC-6** DAG file passes `dagu dry` (or equivalent lint) and appears in the
  dagu UI schedule.

## 8. Testing

Pytest with fixture JSON (trimmed 5-tool payload + a mutated second payload
for the removal case, plus a full 222-tool snapshot fixture over which the
AC-4 invariant — no non-default kind without github — is asserted for every
record). Seams under test are hit for real: temp sqlite DB file created from
a committed `.schema` dump of the real registry (real sqlite3, not mocked;
the dump pins the contract so test-schema drift is a test failure, not a
silent pass), temp dirs for QMD/state/JSON sinks. Only the HTTP fetch is
faked (fixture bytes + injected ETag), since GitHub raw is outside the seam
under test. AC-2/AC-3/AC-4 are covered by tests; AC-1/AC-5/AC-6 verified
live at ship time.

## 9. Risks / trade-offs

- **Registry pollution:** any consumer scanning all `cli` rows now sees a
  few dozen external entries (low tens; matches the §2 yield estimate). Mitigation is the `bucket='discoverable'` contract —
  documented here and in the row's `source_class`. If a consumer breaks, the
  filter goes on the consumer, not by deleting data.
- **Upstream fragility:** the raw URL is a branch ref on a third-party repo;
  a rename/force-push breaks fetch. Failure mode is loud (non-zero DAG exit)
  and safe (last-good sinks stay).
- **Classifier is heuristic:** community descriptions are inconsistent;
  yields will drift. Default-down keeps errors on the harmless side.
- **`launch_spec` semantics bent:** `install:<url>` is a hint, not a
  runnable spec. Acceptable because `enabled=0` rows are never launched.

## Codex review — pre-panel

**2026-07-20 — Codex UNAVAILABLE** (usage limit exhausted until Jul 25;
Gemini leg deprecated). Substitute: independent Sonnet code-reviewer
subagent grounding pass against live systems (registry schema, dagu corpus,
qmd CLI, source URL). **VERDICT: PASS** with 1 MAJOR + 3 MINOR, all fixed
in this revision:

- MAJOR: Section 5 house-style claim refuted — 85% of the 135 DAGs are
  comment-header-only (no `name:`/`description:` keys); spec restated to
  match the dominant pattern.
- MINOR: AC-5 operationalized (top-5 rank threshold); `qmd collection add`
  path + `--name` spelled out; full NOT NULL column set listed in 3C.

Verified-good claims: all Section 3C columns + NOT NULL constraints,
`updated_at` exists, `dagu dry`/`dagu validate` exist, source URL live
(200, {categories:10, tools:222}), AC-4 spot-checks hold against the live
payload. Panel invoked with FORCE_NO_PRECODEX (deliberate, audit-visible).
