# nosignups-catalog-sync Implementation Plan

> **For agentic workers:** REQUIRED: Use `/sh:execute` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Weekly dagu-scheduled sync of the nosignups.net catalog (via its upstream `tools.json`) into three sinks: a source-agnostic JSON artifact, a QMD `tool-directories` collection, and `discoverable` rows in the cli-registry.

**Architecture:** One stdlib-only script `scripts/nosignups_catalog.py` (source seam → normalize → classify → three sink writers → per-source diff/prune with state-written-last). Tests hit real sqlite + real temp dirs; only HTTP is faked. Spec: `docs/superpowers/specs/2026-07-20-nosignups-catalog-sync-design.md` (panel-passed 7.7 — the spec is the contract; on conflict, spec wins).

**Tech Stack:** Python 3 stdlib only (`urllib.request`, `json`, `sqlite3`, `hashlib`, `argparse`, `pathlib`, `tempfile`, `re`, `shutil`). Tests: pytest via `~/projects/00_Governance/.venv/bin/python -m pytest` (script itself imports nothing outside stdlib). dagu for scheduling; `qmd` CLI for collection registration.

**Canonical test command (use for every "passing" claim):**
```bash
cd ~/projects/20_agentflow && ~/projects/00_Governance/.venv/bin/python -m pytest tests/ -v
```

**Constants (single source of truth, defined once in the script):**
```python
RAW_URL = "https://raw.githubusercontent.com/BraveOPotato/FckSignups/refs/heads/main/tools.json"
STATE_DIR = Path.home() / ".local/state/nosignups-catalog"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"           # 20_agentflow/data
QMD_DIR = DATA_DIR / "tool-directories"
JSON_ARTIFACT = DATA_DIR / "tool_catalog.json"
REGISTRY_DB = Path.home() / ".hermes/cli-registry.db"
TOOLID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
KINDS = ("cli", "js-lib", "self-host", "browser-only")
```
All path constants must be overridable via function parameters (tests inject temp paths); the constants are defaults, not hardwired inside functions.

---

## Chunk 1: Fixtures & pure core (normalize, classify)

### Task 1: Repo scaffolding + fixtures

**Files:**
- Create: `tests/__init__.py` (empty), `tests/fixtures/` (dir)
- Create: `tests/fixtures/nosignups_5tools.json`
- Create: `tests/fixtures/nosignups_4tools.json` (same minus one tool → removal case)
- Create: `tests/fixtures/nosignups_full.json` (live 222-tool snapshot)
- Create: `tests/fixtures/cli_registry_schema.sql` (dump of the real `cli` table DDL)

- [ ] **Step 1: Create dirs and fetch fixtures**

```bash
cd ~/projects/20_agentflow && mkdir -p tests/fixtures && touch tests/__init__.py
curl -sL --max-time 30 "https://raw.githubusercontent.com/BraveOPotato/FckSignups/refs/heads/main/tools.json" -o tests/fixtures/nosignups_full.json
python3 - << 'EOF'
import json, pathlib
d = json.loads(pathlib.Path("tests/fixtures/nosignups_full.json").read_text())
# 5-tool fixture: excalidraw (browser-only), ffmpegwasm (js-lib), a cli-tagged one,
# a self-host one if present, + one more; fall back to first tools if ids missing.
by_id = {t["id"]: t for t in d["tools"]}
want = [t for tid, t in by_id.items() if tid in ("excalidraw", "ffmpegwasm")]
want += [t for t in d["tools"] if "cli" in t.get("tags", [])][:1]
want += [t for t in d["tools"] if any("self" in x for x in t.get("tags", []))][:1]
seen = {t["id"] for t in want}
want += [t for t in d["tools"] if t["id"] not in seen][: 5 - len(want)]
five = {"categories": d["categories"], "tools": want[:5]}
pathlib.Path("tests/fixtures/nosignups_5tools.json").write_text(json.dumps(five, indent=1))
four = {"categories": d["categories"], "tools": want[:4]}  # drops tool #5 → removal case
pathlib.Path("tests/fixtures/nosignups_4tools.json").write_text(json.dumps(four, indent=1))
print("5tools ids:", [t["id"] for t in five["tools"]])
print("removed id:", want[4]["id"])
EOF
```
Expected: prints 5 ids + the removed id. Record the removed id — Task 8's removal test uses it.

- [ ] **Step 2: Dump the real registry schema (read-only against prod DB)**

```bash
sqlite3 ~/.hermes/cli-registry.db ".schema cli" > tests/fixtures/cli_registry_schema.sql
grep -c "NOT NULL" tests/fixtures/cli_registry_schema.sql
```
Expected: DDL file written; grep prints ≥ 8 (slug, lang, launch_spec, description, health_status, enabled, a2a_invokable, not_standalone).

- [ ] **Step 3: Commit** (explicit paths — repo guard blocks whole-index commits)

```bash
git add tests/__init__.py tests/fixtures/ && git commit -m "test: fixtures for nosignups catalog sync (payloads + registry schema dump)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- tests/__init__.py tests/fixtures/
```

### Task 2: `normalize()` + toolid validation

**Files:**
- Create: `scripts/nosignups_catalog.py`
- Create: `tests/test_nosignups_catalog.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_nosignups_catalog.py
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import nosignups_catalog as nc

FIX = Path(__file__).parent / "fixtures"

def _payload(name="nosignups_5tools.json"):
    return json.loads((FIX / name).read_text())

def test_normalize_shapes_record():
    recs = nc.normalize_nosignups(_payload(), source="nosignups")
    assert len(recs) == 5
    r = next(x for x in recs if x["uid"] == "nosignups:excalidraw")
    for key in ("uid", "source", "name", "description", "url", "category",
                "tags", "github", "license", "stars", "featured", "kind"):
        assert key in r
    assert r["source"] == "nosignups"
    assert isinstance(r["tags"], list)

def test_normalize_rejects_hostile_toolid(caplog):
    payload = _payload()
    payload["tools"][0]["id"] = "../../evil"
    recs = nc.normalize_nosignups(payload, source="nosignups")
    assert len(recs) == 4                       # hostile record dropped
    assert all("evil" not in r["uid"] for r in recs)

def test_normalize_tolerates_missing_optional_fields():
    payload = _payload()
    for k in ("license", "stars", "featured", "github", "tags"):
        payload["tools"][0].pop(k, None)
    recs = nc.normalize_nosignups(payload, source="nosignups")
    r = recs[0]
    assert r["github"] is None and r["stars"] == 0 and r["tags"] == []
```

- [ ] **Step 2: Run to verify failure**

Run: `~/projects/00_Governance/.venv/bin/python -m pytest tests/test_nosignups_catalog.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nosignups_catalog'`

- [ ] **Step 3: Implement**

```python
#!/usr/bin/env python3
"""nosignups-catalog sync — see docs/superpowers/specs/2026-07-20-nosignups-catalog-sync-design.md."""
import json, logging, re
from pathlib import Path

log = logging.getLogger("nosignups-catalog")
TOOLID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

def normalize_nosignups(payload: dict, source: str) -> list[dict]:
    """Raw upstream {categories,tools} → normalized records. Drops invalid toolids (path-traversal guard)."""
    records = []
    for t in payload.get("tools", []):
        tid = str(t.get("id", ""))
        if not TOOLID_RE.match(tid):
            log.warning("%s: rejected invalid toolid %r", source, tid[:80])
            continue
        records.append({
            "uid": f"{source}:{tid}",
            "source": source,
            "name": t.get("name", tid),
            "description": t.get("description", ""),
            "url": t.get("url", ""),
            "category": t.get("category", ""),
            "tags": list(t.get("tags") or []),
            "github": t.get("github") or None,
            "license": t.get("license") or None,
            "stars": int(t.get("stars") or 0),
            "featured": bool(t.get("featured", False)),
            "kind": "browser-only",   # classify() overwrites; safe default stands alone
        })
    return records
```

- [ ] **Step 4: Run tests — expect 3 PASS.** Then **Step 5: Commit**

```bash
git add scripts/nosignups_catalog.py tests/test_nosignups_catalog.py && git commit -m "feat: normalize + toolid path-traversal guard

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- scripts/nosignups_catalog.py tests/test_nosignups_catalog.py
```

### Task 3: `classify()`

**Files:** Modify both files from Task 2.

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_classify_spot_checks():
    recs = {r["uid"]: r for r in nc.classify_all(
        nc.normalize_nosignups(_payload("nosignups_full.json"), "nosignups"))}
    assert recs["nosignups:excalidraw"]["kind"] == "browser-only"
    assert recs["nosignups:ffmpegwasm"]["kind"] == "js-lib"

def test_classify_invariant_no_kind_without_github_full_payload():
    # AC-4 invariant over the whole 222-tool snapshot: default-down.
    recs = nc.classify_all(nc.normalize_nosignups(_payload("nosignups_full.json"), "nosignups"))
    for r in recs:
        if r["kind"] != "browser-only":
            assert r["github"], f"{r['uid']} classified {r['kind']} without github"

def test_classify_default_is_browser_only():
    r = {"uid": "x:y", "tags": [], "description": "a nice web app", "github": "https://g", "kind": ""}
    assert nc.classify(r) == "browser-only"
```

- [ ] **Step 2: Run — expect FAIL (`classify` not defined).** 

- [ ] **Step 3: Implement** (append to script)

```python
_CLI_RE = re.compile(r"\b(cli|command[- ]line)\b", re.I)
_JSLIB_RE = re.compile(r"\b(wasm|webassembly|library|npm package)\b", re.I)
_SELFHOST_RE = re.compile(r"\b(self[- ]?host\w*|docker)\b", re.I)

def classify(record: dict) -> str:
    """Honest-by-default kind. github is a hard precondition for every non-default kind (AC-4)."""
    if not record.get("github"):
        return "browser-only"
    blob = " ".join([record.get("description", ""), " ".join(record.get("tags", []))])
    if _CLI_RE.search(blob):
        return "cli"
    if _JSLIB_RE.search(blob):
        return "js-lib"
    if _SELFHOST_RE.search(blob):
        return "self-host"
    return "browser-only"

def classify_all(records: list[dict]) -> list[dict]:
    for r in records:
        r["kind"] = classify(r)
    return records
```

- [ ] **Step 4: Run tests — all PASS.** If `ffmpegwasm` fails, inspect its live record and adjust `_JSLIB_RE` minimally (do NOT drop the github precondition). **Step 5: Commit** (`feat: honest-default classifier`, explicit paths, same trailer).

**Chunk-1 review gate:** re-read Tasks 1-3 output — fixtures committed? invariant test green over all 222? toolid guard live in `normalize`, not deferred to sinks? Fix before Chunk 2.

---

## Chunk 2: Freshness, state, and the three sinks

### Task 4: fetch + state (ETag, sha256 fallback)

**Files:** Modify both. Design: `fetch(url, state) -> (payload_bytes|None, new_state_fields)` — returns `None` payload when fresh (304 or hash match). HTTP faked in tests via injectable `opener`.

- [ ] **Step 1: Failing tests** — three cases: (a) server returns 304 for matching ETag ⇒ `None`; (b) no-ETag server, body hash == `state["payload_sha256"]` ⇒ `None`; (c) changed body ⇒ bytes + new etag/sha in state fields. Fake with a closure standing in for `urlopen` (raise `urllib.error.HTTPError(..., code=304)` for (a)). Also: `load_state`/`save_state` round-trip in `tmp_path`, atomic (`tempfile` + `Path.replace`).

- [ ] **Step 2: FAIL → Step 3: Implement**

```python
import hashlib, tempfile, urllib.request, urllib.error

def load_state(state_dir: Path, source: str) -> dict:
    p = state_dir / f"{source}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text())

def _atomic_write_text(path: Path, text: str) -> None:
    """Shared atomic-write idiom (tempfile in target dir + Path.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise

def save_state(state_dir: Path, source: str, state: dict) -> None:
    _atomic_write_text(state_dir / f"{source}.json", json.dumps(state, indent=1))

def fetch(url: str, state: dict, urlopen=urllib.request.urlopen):
    """Conditional GET. Returns (payload_bytes | None, fields). None ⇒ unchanged."""
    req = urllib.request.Request(url, headers={"User-Agent": "nosignups-catalog-sync"})
    if state.get("etag"):
        req.add_header("If-None-Match", state["etag"])
    try:
        with urlopen(req, timeout=30) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status} from {url}")
            body = resp.read()
            etag = resp.headers.get("ETag")
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return None, {}
        raise
    sha = hashlib.sha256(body).hexdigest()
    if not etag and state.get("payload_sha256") == sha:
        return None, {}                      # ETag fallback: hash match ⇒ fresh
    return body, {"etag": etag, "payload_sha256": sha}
```
(`import os` at module top with the other imports. `_atomic_write_text` is defined here in Task 4, not Task 5 — Sink A and the QMD sink reuse it.)

- [ ] **Step 4: PASS → Step 5: Commit** (`feat: conditional fetch + atomic per-source state`).

### Task 5: Sink A — JSON artifact + `emit`

- [ ] **Step 1: Failing test** — `write_json_artifact(records, path)` writes valid JSON array atomically to `tmp_path`; re-write replaces content; file parses back equal.
- [ ] **Step 2-4: TDD** — implementation is ~3 lines: `_atomic_write_text(path, json.dumps(records, indent=1))` (helper already exists from Task 4).
- [ ] **Step 5: Commit** (`feat: json artifact sink`).

### Task 6: Sink B — QMD markdown writer + prune

- [ ] **Step 1: Failing tests** — `write_qmd(records, qmd_dir)`: creates `qmd_dir/nosignups/<toolid>.md` per record; file starts with `---\n` frontmatter containing `name:`, `kind:`, `stars:`, `source:`; body contains the description. `prune_qmd(removed_uids, qmd_dir)`: deletes exactly those files, leaves others; deleting a non-existent file is a no-op (idempotent re-run).
- [ ] **Step 2-4: TDD.** Frontmatter via manual YAML-safe emission (quote strings with `json.dumps` — stdlib-only, no yaml import). Filename: `uid.split(":", 1)[1] + ".md"` — toolid already validated in normalize, assert `TOOLID_RE` again before the path join (defense-in-depth, spec F2).
- [ ] **Step 5: Commit** (`feat: qmd markdown sink + prune`).

### Task 7: Sink C — cli-registry upsert + soft-remove

**Files:** Modify both. Tests build a temp DB: `sqlite3.connect(tmp_path/'reg.db')` + `executescript(fixtures/cli_registry_schema.sql)` — schema drift vs prod becomes a test failure.

- [ ] **Step 1: Failing tests**
  - `upsert_registry(records, db_path)` with the 5-tool fixture ⇒ only `kind != browser-only` rows appear; every row has `slug` prefixed `ns-`, `bucket='discoverable'`, `enabled=0`, `a2a_invokable=0`, `health_status IN ('unknown','ok')`, `lang='unknown'`, `launch_spec` starting `install:https://`, `source_class='external:nosignups'`, `not_standalone=1`.
  - Second upsert of same records ⇒ row count unchanged (ON CONFLICT path), `updated_at` refreshed.
  - `soft_remove_registry(removed_uids, db_path)` ⇒ row kept, `description` gains `[REMOVED upstream] ` prefix exactly once (idempotent).
  - Connection opened with `busy_timeout`: assert `PRAGMA busy_timeout` ≥ 5000 via the module's `_registry_conn(db_path)` helper.
- [ ] **Step 2: FAIL → Step 3: Implement** — `_registry_conn` sets `PRAGMA busy_timeout=5000`; `upsert_registry` runs one transaction (`with conn:`); `shutil.which(toolid)` probe may set `health_status='ok'`; skip records whose kind is `browser-only`.
- [ ] **Step 4: PASS → Step 5: Commit** (`feat: registry discoverable sink (busy_timeout, single txn, soft-remove)`).

**Chunk-2 review gate:** every sink test uses real sqlite/real temp dirs (no mocked seams)? atomic-write helper shared not duplicated? busy_timeout asserted, not assumed? Fix before Chunk 3.

---

## Chunk 3: Orchestration, CLI, live verify, DAG

### Task 8: `sync` orchestration (diff, ordering, changelog, --dry-run)

- [ ] **Step 1: Failing tests** (inject all paths + fake urlopen):
  - Fresh sync with 5-tool payload ⇒ 5 md files, JSON artifact, state file with 5 uids, registry rows for non-browser kinds. Changelog line matches `nosignups: +5 ~0 -0 (0→5)`.
  - Re-sync with same ETag ⇒ 304 ⇒ **zero** writes (capture mtimes of artifact+state before/after; assert equal) — AC-2.
  - Sync with `nosignups_4tools.json` payload (new ETag) ⇒ removed tool's md gone, registry row soft-removed, other source dirs untouched (create a decoy `qmd_dir/othersource/x.md` first) — AC-3.
  - Crash ordering: monkeypatch `save_state` to raise after sinks written ⇒ state file still holds OLD content (state-written-last) — spec F9.
  - `--dry-run` ⇒ changelog printed, zero filesystem/DB writes.
- [ ] **Step 2: FAIL → Step 3: Implement** `sync_source(source_cfg, *, state_dir, qmd_dir, artifact_path, db_path, dry_run=False, urlopen=...)` then `sync_all(...)` looping `SOURCES = [{"name": "nosignups", "url": RAW_URL, "normalize": normalize_nosignups}]`. Order per spec §4: fetch → normalize+classify → (dry-run stops here) → write all sinks → prune → save_state LAST → changelog. Failure = log + re-raise; caller exits non-zero.
- [ ] **Step 4: PASS → Step 5: Commit** (`feat: diff-aware sync orchestration`).

### Task 9: CLI surface

- [ ] **Step 1: Failing tests** — `argparse` wiring via `nc.main(["emit"])` etc.: `emit` prints JSON array to stdout (capsys, fake urlopen); `classify` prints per-kind counts + lists non-browser-only uids; `sync --dry-run` reaches sync with `dry_run=True`; unknown subcommand exits 2.
- [ ] **Step 2-4: TDD** — `main(argv=None)` + `if __name__ == "__main__": raise SystemExit(main())`; `logging.basicConfig(level=INFO)` in main only.
- [ ] **Step 5: Run FULL suite** (canonical command) — all green. **Commit** (`feat: cli surface (sync/emit/classify)`).

### Task 10: Live verify (AC-1, AC-5) — real network, real sinks

- [ ] **Step 1: Backup the production registry first**

```bash
sqlite3 ~/.hermes/cli-registry.db ".backup '/private/tmp/claude-501/-private-tmp/74f46521-1a3a-4c6a-b3fd-c61a42b681ff/scratchpad/cli-registry.pre-nosignups.bak'"
```

- [ ] **Step 2: First live sync + AC-1 checks**

```bash
cd ~/projects/20_agentflow && python3 scripts/nosignups_catalog.py sync
ls data/tool-directories/nosignups/*.md | wc -l          # expect ≥ 200
python3 -c "import json;print(len(json.load(open('data/tool_catalog.json'))))"   # expect ≥ 200
sqlite3 ~/.hermes/cli-registry.db "SELECT count(*), min(enabled), max(enabled), min(a2a_invokable) FROM cli WHERE bucket='discoverable'"  # expect N|0|0|0
cat ~/.local/state/nosignups-catalog/nosignups.json | python3 -m json.tool | head -5
```

- [ ] **Step 3: AC-2 live: immediate re-run** — expect `nosignups: unchanged`, exit 0.

- [ ] **Step 4: Register + verify QMD (AC-5)**

```bash
qmd collection add ~/projects/20_agentflow/data/tool-directories --name tool-directories
qmd query "whiteboard sketch diagrams" 2>/dev/null | head -20   # scope per qmd syntax; expect excalidraw in top-5
```
If scoping flag differs, check `qmd query --help` and use the collection filter it documents. Excalidraw absent from top-5 ⇒ investigate frontmatter/indexing before proceeding (AC-5 is a gate, not a hope).

- [ ] **Step 5: Commit generated data policy** — commit the JSON artifact + md files ONLY if repo convention keeps generated data (check `.gitignore`; `data/` currently holds no generated corpus). Default: add `data/tool-directories/` and `data/tool_catalog.json` to `.gitignore` (regenerable weekly; 200+ churning files pollute diffs), commit the `.gitignore` change (`chore: ignore generated catalog sinks`).

### Task 11: DAG (AC-6)

- [ ] **Step 1: Write** `~/.config/dagu/dags/nosignups-catalog-sync.yaml` — dominant comment-header house style:

```yaml
# nosignups-catalog-sync — weekly pull of nosignups.net tools.json into
# JSON artifact + QMD tool-directories + cli-registry discoverable rows.
# Spec: ~/projects/20_agentflow/docs/superpowers/specs/2026-07-20-nosignups-catalog-sync-design.md
# 304/hash-match ⇒ no-op. Failure leaves last-good sinks (state written last).
schedule: "30 4 * * 1"
steps:
  - name: sync
    command: python3 /Users/jcords-macmini/projects/20_agentflow/scripts/nosignups_catalog.py sync
```

- [ ] **Step 2: Validate**: `dagu dry nosignups-catalog-sync` (fall back to `dagu validate` if dry needs args) — expect success; then confirm it lists: `dagu status nosignups-catalog-sync` or presence in dagu UI.

### Task 12: Finish

- [ ] **Step 1: Full suite green** (canonical command) + `git status` clean.
- [ ] **Step 2: Merge & push per session git ops**: merge `feat/nosignups-catalog` into `master`, push both. (Standard ops — no prompt needed; force-push stays forbidden.)
- [ ] **Step 3: Update spec Status** line to `Shipped YYYY-MM-DD` in the same merge commit or a follow-up docs commit.

**Chunk-3 review gate:** AC-1..AC-6 each verified with quoted command output? Registry backup exists? DAG validated, not just written? Evidence lines recorded for the handover.
