#!/usr/bin/env python3
"""nosignups-catalog sync — see docs/superpowers/specs/2026-07-20-nosignups-catalog-sync-design.md.

Weekly sync of the nosignups.net catalog (upstream tools.json) into three sinks:
a source-agnostic JSON artifact, a QMD tool-directories collection, and
`discoverable` rows in the cli-registry. Python 3 stdlib only.
"""
import argparse
import datetime
import hashlib
import json
import logging
import os
import re
import shutil
import sqlite3
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

log = logging.getLogger("nosignups-catalog")

# --- Constants (single source of truth; all paths overridable as params) ----
RAW_URL = "https://raw.githubusercontent.com/BraveOPotato/FckSignups/refs/heads/main/tools.json"
PUBLIC_APIS_URL = "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
STATE_DIR = Path.home() / ".local/state/nosignups-catalog"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"           # 20_agentflow/data
QMD_DIR = DATA_DIR / "tool-directories"
JSON_ARTIFACT = DATA_DIR / "tool_catalog.json"
REGISTRY_DB = Path.home() / ".hermes/cli-registry.db"
TOOLID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
KINDS = ("cli", "js-lib", "self-host", "browser-only", "api")


# ---------------------------------------------------------------------------
# Task 2: normalize + toolid validation
# ---------------------------------------------------------------------------

def normalize_nosignups(payload: dict, source: str) -> list[dict]:
    """Raw upstream {categories,tools} -> normalized records.

    Drops invalid toolids (path-traversal guard).
    """
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


# --- public-apis (README-sourced) ------------------------------------------
# Upstream ships no machine-readable artifact (db/resources.json is 404), so the
# README tables are the source of truth. Real category tables are 5-column
# (API | Description | Auth | HTTPS | CORS); the sponsored APILayer table at the
# top is 3-column. We gate on that *content* shape rather than on position, so
# an upstream reshuffle can't silently pull affiliate rows into the catalog.

_PA_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
_PA_LINK_RE = re.compile(r"^\[([^\]]+)\]\((https?://[^\s)]+)\s*\)$")
# Closed vocabulary observed upstream; anything else means we mis-parsed a row.
_PA_AUTH_VALUES = {"no", "apikey", "oauth", "x-mashape-key", "user-agent"}


def _pa_cells(line: str) -> list[str]:
    """Split a markdown table row, dropping trailing empty cells.

    83 upstream rows carry cosmetic trailing pipes ("| |"). A strict len==5
    check would drop real entries (Dropbox, FRED, SEC EDGAR, ...), so trim
    first and length-check after.
    """
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    while cells and not cells[-1]:
        cells.pop()
    return cells


def _pa_slug(name: str) -> str:
    """Name -> toolid matching TOOLID_RE (lowercase, [a-z0-9._-])."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:64]


def normalize_public_apis(payload: str, source: str) -> list[dict]:
    """Raw upstream README text -> normalized records.

    Category comes from the enclosing '### Heading'. Auth/HTTPS/CORS are
    preserved as tags because they are the fields that decide whether an API
    is usable at all (key required? browser-callable?).
    """
    records: list[dict] = []
    seen: set[str] = set()
    category = ""
    for raw in payload.splitlines():
        line = raw.strip()
        heading = _PA_HEADING_RE.match(line)
        if heading:
            category = heading.group(1)
            continue
        if not line.startswith("|"):
            continue
        cells = _pa_cells(line)
        if len(cells) != 5:
            continue                              # promo table / malformed row
        name_cell, desc, auth, https, cors = cells
        if set(name_cell) <= set("-: "):
            continue                              # header separator
        link = _PA_LINK_RE.match(name_cell)
        if not link:
            continue                              # header row ("API"), or no link
        auth_norm = auth.strip("`").strip().lower()
        if auth_norm not in _PA_AUTH_VALUES:
            log.warning("%s: skipped row with unexpected auth %r", source, auth[:40])
            continue
        name, url = link.group(1).strip(), link.group(2).strip()
        tid = _pa_slug(name)
        if not TOOLID_RE.match(tid) or tid in seen:
            continue                              # invalid or duplicate name
        seen.add(tid)
        records.append({
            "uid": f"{source}:{tid}",
            "source": source,
            "name": name,
            "description": desc,
            "url": url,
            "category": category,
            "tags": [
                f"auth:{auth_norm}",
                f"https:{https.strip().lower()}",
                f"cors:{cors.strip().lower()}",
            ],
            "github": url if url.startswith("https://github.com/") else None,
            "license": None,
            "stars": 0,
            "featured": False,
            "kind": "api",       # classify() leaves this alone; see classify()
        })
    return records


# ---------------------------------------------------------------------------
# Task 3: classify
# ---------------------------------------------------------------------------

_CLI_RE = re.compile(r"\b(cli|command[- ]line)\b", re.I)
_JSLIB_RE = re.compile(r"\b(wasm|webassembly|library|npm package)\b", re.I)
_SELFHOST_RE = re.compile(r"\b(self[- ]?host\w*|docker)\b", re.I)


def classify(record: dict) -> str:
    """Honest-by-default kind. github is a hard precondition for every non-default kind (AC-4)."""
    # A remote HTTP endpoint is not a runnable artifact; the cli/js-lib/self-host
    # heuristics below don't apply to it. Sources that already know their kind
    # (public-apis) keep it rather than being re-derived from prose.
    if record.get("kind") == "api":
        return "api"
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


# ---------------------------------------------------------------------------
# Task 4: fetch + state (ETag, sha256 fallback)
# ---------------------------------------------------------------------------

def load_state(state_dir: Path, source: str) -> dict:
    p = Path(state_dir) / f"{source}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _atomic_write_text(path: Path, text: str) -> None:
    """Shared atomic-write idiom (tempfile in target dir + Path.replace)."""
    path = Path(path)
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
    _atomic_write_text(Path(state_dir) / f"{source}.json", json.dumps(state, indent=1))


def fetch(url: str, state: dict, urlopen=None):
    """Conditional GET. Returns (payload_bytes | None, fields). None => unchanged."""
    if urlopen is None:                          # resolve at call-time (monkeypatch-friendly)
        urlopen = urllib.request.urlopen
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
        return None, {}                      # ETag fallback: hash match => fresh
    return body, {"etag": etag, "payload_sha256": sha}


# ---------------------------------------------------------------------------
# Task 5: Sink A — JSON artifact
# ---------------------------------------------------------------------------

def write_json_artifact(records: list[dict], path: Path) -> None:
    """Write the normalized records as a JSON array atomically."""
    _atomic_write_text(Path(path), json.dumps(records, indent=1))


# ---------------------------------------------------------------------------
# Task 6: Sink B — QMD markdown writer + prune
# ---------------------------------------------------------------------------

def _frontmatter_value(v) -> str:
    """YAML-safe scalar/list emission using json.dumps (stdlib-only, no yaml)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(json.dumps(str(x)) for x in v) + "]"
    if v is None:
        return "null"
    return json.dumps(str(v))


def _qmd_markdown(record: dict) -> str:
    fields = ("name", "source", "url", "github", "license", "stars",
              "category", "tags", "kind")
    lines = ["---"]
    for k in fields:
        lines.append(f"{k}: {_frontmatter_value(record.get(k))}")
    lines.append("---")
    lines.append("")
    lines.append(record.get("description", ""))
    lines.append("")
    return "\n".join(lines)


def _toolid_from_uid(uid: str) -> str:
    return uid.split(":", 1)[1]


def write_qmd(records: list[dict], qmd_dir: Path) -> None:
    """Write one markdown file per record under qmd_dir/<source>/<toolid>.md."""
    for r in records:
        toolid = _toolid_from_uid(r["uid"])
        if not TOOLID_RE.match(toolid):          # defense-in-depth (spec F2)
            log.warning("qmd: rejected invalid toolid %r", toolid[:80])
            continue
        dest = Path(qmd_dir) / r["source"] / f"{toolid}.md"
        _atomic_write_text(dest, _qmd_markdown(r))


def prune_qmd(removed_uids, qmd_dir: Path) -> None:
    """Delete the QMD file for each removed uid. Missing file => no-op (idempotent)."""
    for uid in removed_uids:
        source = uid.split(":", 1)[0]
        toolid = _toolid_from_uid(uid)
        if not TOOLID_RE.match(toolid):
            log.warning("prune: rejected invalid toolid %r", toolid[:80])
            continue
        dest = Path(qmd_dir) / source / f"{toolid}.md"
        dest.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Task 7: Sink C — cli-registry upsert + soft-remove
# ---------------------------------------------------------------------------

def _registry_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def upsert_registry(records: list[dict], db_path: Path) -> int:
    """Upsert runnable records as discoverable cli-registry rows.

    Excludes browser-only (nothing to install) and api (a remote HTTP endpoint
    is not a runnable artifact — it would land as a row whose launch_spec
    points at nothing). Those stay QMD-only.

    One transaction. Returns number of rows written.
    """
    rows = []
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    for r in records:
        if r["kind"] in ("browser-only", "api"):
            continue
        toolid = _toolid_from_uid(r["uid"])
        if not TOOLID_RE.match(toolid):
            log.warning("registry: rejected invalid toolid %r", toolid[:80])
            continue
        slug = f"ns-{toolid}"
        github = r.get("github") or ""
        # a2a-cli-registry's search/overview/TUI reads no other status marker
        # for "known, not independently runnable" — reuse that exact wire,
        # not an invented bucket value nobody queries.
        health = "ok" if shutil.which(toolid) else "not_standalone"
        rows.append({
            "slug": slug,
            "lang": "unknown",
            "bucket": "discoverable",
            "project": "external",
            "path": "",
            "launch_spec": f"install:{github}",
            "description": r.get("description", ""),
            "source_class": f"external:{r['source']}",
            "health_status": health,
            "enabled": 0,
            "a2a_invokable": 0,
            "not_standalone": 1,
            "last_seen_at": now,
            "updated_at": now,
        })

    if not rows:
        return 0

    sql = """
        INSERT INTO cli (slug, lang, bucket, project, path, launch_spec,
                         description, source_class, health_status, enabled,
                         a2a_invokable, not_standalone, last_seen_at, updated_at)
        VALUES (:slug, :lang, :bucket, :project, :path, :launch_spec,
                :description, :source_class, :health_status, :enabled,
                :a2a_invokable, :not_standalone, :last_seen_at, :updated_at)
        ON CONFLICT(slug) DO UPDATE SET
            lang=excluded.lang,
            bucket=excluded.bucket,
            project=excluded.project,
            path=excluded.path,
            launch_spec=excluded.launch_spec,
            description=excluded.description,
            source_class=excluded.source_class,
            health_status=excluded.health_status,
            enabled=excluded.enabled,
            a2a_invokable=excluded.a2a_invokable,
            not_standalone=excluded.not_standalone,
            last_seen_at=excluded.last_seen_at,
            updated_at=excluded.updated_at
    """
    conn = _registry_conn(db_path)
    try:
        with conn:
            conn.executemany(sql, rows)
    finally:
        conn.close()
    return len(rows)


def soft_remove_registry(removed_uids, db_path: Path) -> None:
    """Soft-remove registry rows for removed uids: prefix description [REMOVED upstream] once."""
    prefix = "[REMOVED upstream] "
    conn = _registry_conn(db_path)
    try:
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        with conn:
            for uid in removed_uids:
                toolid = _toolid_from_uid(uid)
                if not TOOLID_RE.match(toolid):
                    continue
                slug = f"ns-{toolid}"
                row = conn.execute(
                    "SELECT description FROM cli WHERE slug=?", (slug,)
                ).fetchone()
                if row is None:
                    continue
                desc = row[0] or ""
                if desc.startswith(prefix):
                    continue                    # idempotent
                conn.execute(
                    "UPDATE cli SET description=?, updated_at=? WHERE slug=?",
                    (prefix + desc, now, slug),
                )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Task 8: sync orchestration (diff, ordering, changelog, --dry-run)
# ---------------------------------------------------------------------------

def _decode_json(body: bytes):
    return json.loads(body.decode("utf-8"))


def _decode_text(body: bytes) -> str:
    return body.decode("utf-8")


# "decode" turns raw bytes into whatever the source's normalize() expects:
# JSON for nosignups, plain markdown text for public-apis.
SOURCES = [
    {"name": "nosignups", "url": RAW_URL,
     "normalize": normalize_nosignups, "decode": _decode_json},
    {"name": "public-apis", "url": PUBLIC_APIS_URL,
     "normalize": normalize_public_apis, "decode": _decode_text},
]


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _diff(old_uids, new_uids):
    old, new = set(old_uids), set(new_uids)
    added = sorted(new - old)
    removed = sorted(old - new)
    common = old & new
    return added, removed, common


def sync_source(source_cfg, *, state_dir, qmd_dir, artifact_path, db_path,
                dry_run=False, urlopen=None):
    """Sync one source. Returns a one-line changelog string.

    Order (spec §4): fetch -> normalize+classify -> (dry-run stops) ->
    write all sinks -> prune -> save_state LAST -> changelog.
    """
    name = source_cfg["name"]
    url = source_cfg["url"]
    normalize_fn = source_cfg["normalize"]
    decode_fn = source_cfg.get("decode", _decode_json)   # JSON stays the default

    state = load_state(state_dir, name)
    body, new_fields = fetch(url, state, urlopen=urlopen)
    if body is None:
        log.info("%s: unchanged", name)
        return f"{name}: unchanged"

    payload = decode_fn(body)
    records = classify_all(normalize_fn(payload, source=name))

    old_uids = state.get("uids", [])
    new_uids = [r["uid"] for r in records]
    added, removed, common = _diff(old_uids, new_uids)
    # "changed" = uids present in both runs (idempotent rewrite; heuristic count)
    changed = len(common)
    changelog = (f"{name}: +{len(added)} ~{changed} -{len(removed)} "
                 f"({len(old_uids)}->{len(new_uids)})")

    if dry_run:
        log.info("%s (dry-run): %s", name, changelog)
        return changelog

    # Write all sinks idempotently.
    write_json_artifact(records, artifact_path)
    write_qmd(records, qmd_dir)
    upsert_registry(records, db_path)

    # Prune removed records (scoped per source).
    if removed:
        prune_qmd(removed, qmd_dir)
        soft_remove_registry(removed, db_path)

    # State written LAST — crash before this leaves old state, next run heals.
    new_state = dict(state)
    new_state.update(new_fields)
    new_state["uids"] = new_uids
    new_state["last_sync_iso"] = _now_iso()
    save_state(state_dir, name, new_state)

    log.info("%s: %s", name, changelog)
    return changelog


def sync_all(*, state_dir=STATE_DIR, qmd_dir=QMD_DIR, artifact_path=JSON_ARTIFACT,
             db_path=REGISTRY_DB, dry_run=False, urlopen=None,
             sources=None):
    """Sync every configured source. Re-raises on failure (caller exits non-zero)."""
    if sources is None:
        sources = SOURCES
    lines = []
    for cfg in sources:
        line = sync_source(cfg, state_dir=state_dir, qmd_dir=qmd_dir,
                           artifact_path=artifact_path, db_path=db_path,
                           dry_run=dry_run, urlopen=urlopen)
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Task 9: CLI surface
# ---------------------------------------------------------------------------

def _emit(urlopen=None, sources=None):
    """Fetch + normalize + classify all sources, return combined records (no cache, no sinks)."""
    if sources is None:
        sources = SOURCES
    all_records = []
    for cfg in sources:
        body, _ = fetch(cfg["url"], {}, urlopen=urlopen)
        if body is None:
            continue
        payload = cfg.get("decode", _decode_json)(body)
        all_records.extend(classify_all(cfg["normalize"](payload, source=cfg["name"])))
    return all_records


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(prog="nosignups_catalog.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="full pipeline (what the DAG runs)")
    p_sync.add_argument("--dry-run", action="store_true",
                        help="fetch+diff+changelog, write nothing")
    sub.add_parser("emit", help="normalized JSON to stdout only")
    sub.add_parser("classify", help="per-kind counts + non-browser-only list")

    args = parser.parse_args(argv)

    if args.command == "emit":
        records = _emit()
        print(json.dumps(records, indent=1))
        return 0

    if args.command == "classify":
        records = _emit()
        counts = {k: 0 for k in KINDS}
        for r in records:
            counts[r["kind"]] = counts.get(r["kind"], 0) + 1
        for k in KINDS:
            print(f"{k}: {counts.get(k, 0)}")
        for r in records:
            if r["kind"] not in ("browser-only", "api"):
                print(f"{r['kind']}\t{r['uid']}")
        return 0

    if args.command == "sync":
        try:
            sync_all(dry_run=args.dry_run)
        except (urllib.error.URLError, OSError, sqlite3.Error,
                json.JSONDecodeError, RuntimeError) as e:
            log.error("sync failed: %s", e)
            return 1
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
