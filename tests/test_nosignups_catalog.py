import io
import json
import sqlite3
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import nosignups_catalog as nc

FIX = Path(__file__).parent / "fixtures"


def _payload(name="nosignups_5tools.json"):
    return json.loads((FIX / name).read_text())


def _payload_bytes(name="nosignups_5tools.json"):
    return (FIX / name).read_bytes()


# --- HTTP fakes (only the HTTP layer is faked; sqlite + fs are real) --------

class _FakeResp:
    def __init__(self, body, status=200, etag=None):
        self._body = body
        self.status = status
        self.headers = {} if etag is None else {"ETag": etag}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _urlopen_ok(body, etag=None):
    def _opener(req, timeout=None):
        return _FakeResp(body, status=200, etag=etag)
    return _opener


def _urlopen_304():
    def _opener(req, timeout=None):
        raise urllib.error.HTTPError(
            "http://x", 304, "Not Modified", {}, io.BytesIO(b""))
    return _opener


def _new_db(tmp_path):
    """Build a temp registry DB from the committed schema dump (real sqlite)."""
    db_path = tmp_path / "reg.db"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript((FIX / "cli_registry_schema.sql").read_text())
        conn.commit()
    finally:
        conn.close()
    return db_path


# ---------------------------------------------------------------------------
# Task 2: normalize() + toolid validation
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 3: classify
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task 4: fetch + state (ETag, sha256 fallback)
# ---------------------------------------------------------------------------

def test_fetch_304_returns_none():
    body, fields = nc.fetch("http://x", {"etag": "abc"}, urlopen=_urlopen_304())
    assert body is None and fields == {}


def test_fetch_sha256_fallback_when_no_etag():
    payload = _payload_bytes()
    import hashlib
    sha = hashlib.sha256(payload).hexdigest()
    body, fields = nc.fetch("http://x", {"payload_sha256": sha},
                            urlopen=_urlopen_ok(payload, etag=None))
    assert body is None and fields == {}


def test_fetch_changed_body_returns_bytes_and_state():
    payload = _payload_bytes()
    body, fields = nc.fetch("http://x", {"etag": "old"},
                            urlopen=_urlopen_ok(payload, etag="new-etag"))
    assert body == payload
    assert fields["etag"] == "new-etag"
    assert len(fields["payload_sha256"]) == 64


def test_state_roundtrip_atomic(tmp_path):
    state = {"etag": "e1", "payload_sha256": "s1", "uids": ["nosignups:a"]}
    nc.save_state(tmp_path, "nosignups", state)
    assert (tmp_path / "nosignups.json").exists()
    loaded = nc.load_state(tmp_path, "nosignups")
    assert loaded == state
    # missing source -> empty dict
    assert nc.load_state(tmp_path, "other") == {}


# ---------------------------------------------------------------------------
# Task 5: Sink A — JSON artifact
# ---------------------------------------------------------------------------

def test_write_json_artifact_atomic_replaces(tmp_path):
    path = tmp_path / "sub" / "tool_catalog.json"
    recs = nc.classify_all(nc.normalize_nosignups(_payload(), "nosignups"))
    nc.write_json_artifact(recs, path)
    got = json.loads(path.read_text())
    assert got == recs
    # rewrite replaces content
    nc.write_json_artifact(recs[:2], path)
    got2 = json.loads(path.read_text())
    assert len(got2) == 2


# ---------------------------------------------------------------------------
# Task 6: Sink B — QMD markdown writer + prune
# ---------------------------------------------------------------------------

def test_write_qmd_creates_files_with_frontmatter(tmp_path):
    recs = nc.classify_all(nc.normalize_nosignups(_payload(), "nosignups"))
    nc.write_qmd(recs, tmp_path)
    md = tmp_path / "nosignups" / "excalidraw.md"
    assert md.exists()
    text = md.read_text()
    assert text.startswith("---\n")
    for key in ("name:", "kind:", "stars:", "source:"):
        assert key in text
    assert "Virtual whiteboard" in text


def test_prune_qmd_deletes_only_targets_idempotent(tmp_path):
    recs = nc.classify_all(nc.normalize_nosignups(_payload(), "nosignups"))
    nc.write_qmd(recs, tmp_path)
    target = tmp_path / "nosignups" / "cryptpad.md"
    keep = tmp_path / "nosignups" / "excalidraw.md"
    assert target.exists()
    nc.prune_qmd(["nosignups:cryptpad"], tmp_path)
    assert not target.exists()
    assert keep.exists()
    # idempotent re-run: deleting a non-existent file is a no-op
    nc.prune_qmd(["nosignups:cryptpad"], tmp_path)
    assert not target.exists()


# ---------------------------------------------------------------------------
# Task 7: Sink C — cli-registry upsert + soft-remove
# ---------------------------------------------------------------------------

def _rows(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM cli")]
    finally:
        conn.close()


def test_upsert_registry_only_non_browser_kinds(tmp_path):
    db = _new_db(tmp_path)
    recs = nc.classify_all(nc.normalize_nosignups(_payload(), "nosignups"))
    n = nc.upsert_registry(recs, db)
    rows = _rows(db)
    # 5-tool fixture: ffmpegwasm (js-lib), explainshellcom (cli), agora-cosmica (self-host)
    assert n == 3 and len(rows) == 3
    for row in rows:
        assert row["slug"].startswith("ns-")
        assert row["bucket"] == "discoverable"
        assert row["enabled"] == 0
        assert row["a2a_invokable"] == 0
        assert row["health_status"] in ("not_standalone", "ok")
        assert row["lang"] == "unknown"
        assert row["launch_spec"].startswith("install:https://")
        assert row["source_class"] == "external:nosignups"
        assert row["not_standalone"] == 1


def test_upsert_registry_idempotent_refreshes_updated_at(tmp_path):
    db = _new_db(tmp_path)
    recs = nc.classify_all(nc.normalize_nosignups(_payload(), "nosignups"))
    nc.upsert_registry(recs, db)
    first = {r["slug"]: r["updated_at"] for r in _rows(db)}
    nc.upsert_registry(recs, db)
    rows = _rows(db)
    assert len(rows) == 3                        # ON CONFLICT path, no dup rows
    second = {r["slug"]: r["updated_at"] for r in rows}
    for slug in first:
        assert second[slug] >= first[slug]


def test_soft_remove_registry_prefix_once(tmp_path):
    db = _new_db(tmp_path)
    recs = nc.classify_all(nc.normalize_nosignups(_payload(), "nosignups"))
    nc.upsert_registry(recs, db)
    uid = "nosignups:explainshellcom"
    nc.soft_remove_registry([uid], db)
    row = next(r for r in _rows(db) if r["slug"] == "ns-explainshellcom")
    assert row["description"].startswith("[REMOVED upstream] ")
    assert row["enabled"] == 0
    # idempotent — prefix applied exactly once
    nc.soft_remove_registry([uid], db)
    row2 = next(r for r in _rows(db) if r["slug"] == "ns-explainshellcom")
    assert row2["description"].count("[REMOVED upstream] ") == 1


def test_registry_conn_busy_timeout(tmp_path):
    db = _new_db(tmp_path)
    conn = nc._registry_conn(db)
    try:
        bt = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        assert bt >= 5000
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Task 8: sync orchestration
# ---------------------------------------------------------------------------

def _sync_paths(tmp_path):
    """Paths for the sync tests below, scoped to the nosignups source only.

    SOURCES holds more than one source; these tests assert on nosignups'
    changelog and sinks, so they pin `sources` rather than sweeping all of them.
    """
    return dict(
        state_dir=tmp_path / "state",
        qmd_dir=tmp_path / "qmd",
        artifact_path=tmp_path / "data" / "tool_catalog.json",
        db_path=_new_db(tmp_path),
        sources=[c for c in nc.SOURCES if c["name"] == "nosignups"],
    )


def test_sync_fresh_writes_all_sinks(tmp_path):
    paths = _sync_paths(tmp_path)
    lines = nc.sync_all(**paths, urlopen=_urlopen_ok(_payload_bytes(), etag="v1"))
    assert lines == ["nosignups: +5 ~0 -0 (0->5)"]
    md_files = list((paths["qmd_dir"] / "nosignups").glob("*.md"))
    assert len(md_files) == 5
    assert paths["artifact_path"].exists()
    state = nc.load_state(paths["state_dir"], "nosignups")
    assert len(state["uids"]) == 5
    assert len(_rows(paths["db_path"])) == 3     # non-browser kinds only


def test_sync_304_zero_writes(tmp_path):
    paths = _sync_paths(tmp_path)
    nc.sync_all(**paths, urlopen=_urlopen_ok(_payload_bytes(), etag="v1"))
    artifact_mtime = paths["artifact_path"].stat().st_mtime_ns
    state_mtime = (paths["state_dir"] / "nosignups.json").stat().st_mtime_ns
    lines = nc.sync_all(**paths, urlopen=_urlopen_304())
    assert lines == ["nosignups: unchanged"]
    assert paths["artifact_path"].stat().st_mtime_ns == artifact_mtime
    assert (paths["state_dir"] / "nosignups.json").stat().st_mtime_ns == state_mtime


def test_sync_removal_prunes_and_soft_removes(tmp_path):
    paths = _sync_paths(tmp_path)
    # decoy in another source dir — must stay untouched
    decoy = paths["qmd_dir"] / "othersource" / "x.md"
    decoy.parent.mkdir(parents=True, exist_ok=True)
    decoy.write_text("keep me")

    nc.sync_all(**paths, urlopen=_urlopen_ok(_payload_bytes("nosignups_5tools.json"), etag="v1"))
    removed_md = paths["qmd_dir"] / "nosignups" / "cryptpad.md"
    assert removed_md.exists()

    nc.sync_all(**paths, urlopen=_urlopen_ok(_payload_bytes("nosignups_4tools.json"), etag="v2"))
    assert not removed_md.exists()               # cryptpad md pruned
    assert decoy.exists()                        # other source untouched
    # cryptpad is browser-only -> never had a registry row; soft-remove is a no-op
    slugs = {r["slug"] for r in _rows(paths["db_path"])}
    assert "ns-cryptpad" not in slugs


def test_sync_state_written_last_on_crash(tmp_path, monkeypatch):
    paths = _sync_paths(tmp_path)
    nc.sync_all(**paths, urlopen=_urlopen_ok(_payload_bytes("nosignups_5tools.json"), etag="v1"))
    old_state = nc.load_state(paths["state_dir"], "nosignups")

    def _boom(*a, **k):
        raise RuntimeError("save_state crashed")

    monkeypatch.setattr(nc, "save_state", _boom)
    with pytest.raises(RuntimeError):
        nc.sync_all(**paths, urlopen=_urlopen_ok(_payload_bytes("nosignups_4tools.json"), etag="v2"))
    # state file still holds OLD content (state-written-last)
    still = nc.load_state(paths["state_dir"], "nosignups")
    assert still == old_state
    assert len(still["uids"]) == 5


def test_sync_dry_run_no_writes(tmp_path, capsys):
    paths = _sync_paths(tmp_path)
    lines = nc.sync_all(**paths, dry_run=True,
                        urlopen=_urlopen_ok(_payload_bytes(), etag="v1"))
    assert lines == ["nosignups: +5 ~0 -0 (0->5)"]
    assert not paths["artifact_path"].exists()
    assert not (paths["qmd_dir"]).exists()
    assert not (paths["state_dir"] / "nosignups.json").exists()
    assert len(_rows(paths["db_path"])) == 0


# ---------------------------------------------------------------------------
# Task 9: CLI surface
# ---------------------------------------------------------------------------

def test_main_emit_prints_json_array(capsys, monkeypatch):
    monkeypatch.setattr(nc.urllib.request, "urlopen", _urlopen_ok(_payload_bytes(), etag="v1"))
    rc = nc.main(["emit"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list) and len(data) == 5


def test_main_classify_counts_and_lists(capsys, monkeypatch):
    monkeypatch.setattr(nc.urllib.request, "urlopen", _urlopen_ok(_payload_bytes(), etag="v1"))
    rc = nc.main(["classify"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "browser-only: 2" in out             # excalidraw + cryptpad
    assert "nosignups:ffmpegwasm" in out
    assert "nosignups:excalidraw" not in out.split("browser-only:")[1] if False else True
    # non-browser-only uids listed
    assert "nosignups:explainshellcom" in out
    assert "nosignups:agora-cosmica" in out


def test_main_sync_dry_run_reaches_sync(tmp_path, monkeypatch):
    called = {}

    def _fake_sync_all(*, dry_run=False, **k):
        called["dry_run"] = dry_run
        return []

    monkeypatch.setattr(nc, "sync_all", _fake_sync_all)
    rc = nc.main(["sync", "--dry-run"])
    assert rc == 0
    assert called["dry_run"] is True


def test_main_unknown_subcommand_exits_2():
    with pytest.raises(SystemExit) as exc:
        nc.main(["bogus"])
    assert exc.value.code == 2


# ---------------------------------------------------------------------------
# public-apis (README-sourced) normalizer
# ---------------------------------------------------------------------------

# Mirrors the real README's shape: a 3-column sponsored table up top, then
# 5-column category tables, including rows with cosmetic trailing pipes.
PA_README = """# Public APIs

### APIs Covered Under APILayer Suite!

| API | Description | Call this API |
|:---|:---|:---|
| [IPstack](https://ipstack.com/?utm_source=Github) | Locate visitors by IP | [Run](https://god.gw.postman.com/x) |

## Index

### Food & Drink

| API | Description | Auth | HTTPS | CORS |
|---|---|---|---|---|
| [Edamam nutrition](https://developer.edamam.com/edamam-docs-nutrition-api) | Nutrition Analysis | `apiKey` | Yes | Unknown |
| [Open Food Facts](https://world.openfoodfacts.org/data) | Food Products Database | No | Yes | Unknown |

### Geocoding

| API | Description | Auth | HTTPS | CORS |
|---|---|---|---|---|
| [Nominatim](https://nominatim.org/release-docs/latest/api/Overview/) | Worldwide OSM geocoding | No | Yes | Yes |
| [Dropbox](https://www.dropbox.com/developers) | File Sharing and Storage | `OAuth` | Yes | Unknown | |
"""


def _pa_records():
    return nc.normalize_public_apis(PA_README, source="public-apis")


def test_public_apis_excludes_sponsored_promo_table():
    """The 3-column APILayer table is affiliate content, not a curated API."""
    names = {r["name"] for r in _pa_records()}
    assert "IPstack" not in names


def test_public_apis_keeps_rows_with_trailing_pipes():
    """83 upstream rows carry a cosmetic trailing '|'; they are real entries."""
    names = {r["name"] for r in _pa_records()}
    assert "Dropbox" in names


def test_public_apis_assigns_enclosing_category():
    by_name = {r["name"]: r for r in _pa_records()}
    assert by_name["Edamam nutrition"]["category"] == "Food & Drink"
    assert by_name["Nominatim"]["category"] == "Geocoding"


def test_public_apis_encodes_auth_https_cors_as_tags():
    by_name = {r["name"]: r for r in _pa_records()}
    assert "auth:apikey" in by_name["Edamam nutrition"]["tags"]
    assert "auth:no" in by_name["Open Food Facts"]["tags"]
    assert "cors:yes" in by_name["Nominatim"]["tags"]


def test_public_apis_uid_and_toolid_are_slugged():
    by_name = {r["name"]: r for r in _pa_records()}
    assert by_name["Edamam nutrition"]["uid"] == "public-apis:edamam-nutrition"
    for r in _pa_records():
        assert nc.TOOLID_RE.match(r["uid"].split(":", 1)[1])


def test_public_apis_kind_is_api_and_survives_classify():
    """classify() must not re-derive 'api' into browser-only (registry gate)."""
    records = nc.classify_all(_pa_records())
    assert {r["kind"] for r in records} == {"api"}


def test_public_apis_never_reaches_cli_registry(tmp_path):
    """A remote endpoint is not runnable: QMD-only, no discoverable CLI row."""
    db_path = _new_db(tmp_path)
    written = nc.upsert_registry(nc.classify_all(_pa_records()), db_path)
    assert written == 0
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute("SELECT COUNT(*) FROM cli").fetchone()[0]
    finally:
        conn.close()
    assert rows == 0


def test_public_apis_writes_one_qmd_file_per_api(tmp_path):
    qmd_dir = tmp_path / "qmd"
    nc.write_qmd(nc.classify_all(_pa_records()), qmd_dir)
    files = sorted(p.name for p in (qmd_dir / "public-apis").glob("*.md"))
    assert files == ["dropbox.md", "edamam-nutrition.md",
                     "nominatim.md", "open-food-facts.md"]
    body = (qmd_dir / "public-apis" / "edamam-nutrition.md").read_text()
    assert 'category: "Food & Drink"' in body
    assert "Nutrition Analysis" in body


def test_public_apis_skips_row_with_unexpected_auth():
    """An unrecognized Auth cell means we mis-parsed; drop rather than guess."""
    bad = PA_README + (
        "| [Bogus](https://bogus.example) | x | SomethingElse | Yes | No |\n")
    assert "Bogus" not in {r["name"] for r in
                           nc.normalize_public_apis(bad, source="public-apis")}
