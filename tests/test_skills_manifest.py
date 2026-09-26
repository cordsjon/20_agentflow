"""skills_manifest.py — check | promote | retire | record (US-SH2-04 AC-1/2/4).
Everything runs against tmp dirs passed via --skills-dir/--runtime-dir/--manifest,
so the machine's ~/.claude/skills is never touched by the tests."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "scripts" / "skills_manifest.py"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mk_skill(root: Path, name: str, text: str = "# skill\n") -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(text)
    return d


@pytest.fixture
def env(tmp_path):
    skills, runtime, retired = tmp_path / "skills", tmp_path / "runtime", tmp_path / "retired"
    skills.mkdir(); runtime.mkdir()
    manifest = tmp_path / "skills-manifest.json"
    mk_skill(skills, "sh-a"); mk_skill(skills, "sh-b")
    mk_skill(runtime, "sh-a")  # already promoted, identical
    mk_skill(runtime, "_decoy", "# not ours\n")  # never in the manifest
    manifest.write_text(json.dumps({"version": 1, "skills": {
        "sh-a": {"status": "global", "since": "2026-09-26", "synced_sha256": sha(skills / "sh-a" / "SKILL.md")},
        "sh-b": {"status": "repo-local", "since": "2026-09-26"},
    }}, indent=2))
    return {"skills": skills, "runtime": runtime, "retired": retired, "manifest": manifest}


def run(env, *args):
    return subprocess.run([sys.executable, str(TOOL), "--skills-dir", str(env["skills"]),
                          "--runtime-dir", str(env["runtime"]), "--retired-dir", str(env["retired"]),
                          "--manifest", str(env["manifest"]), *args], capture_output=True, text=True)


def load(env):
    return json.loads(env["manifest"].read_text())["skills"]


def test_check_clean(env):
    r = run(env, "check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_check_fails_on_unlisted_dir(env):
    mk_skill(env["skills"], "sh-c")
    r = run(env, "check")
    assert r.returncode == 1 and "unlisted:sh-c" in r.stdout


def test_check_fails_on_missing_dir(env):
    m = json.loads(env["manifest"].read_text()); m["skills"]["sh-ghost"] = {"status": "repo-local", "since": "2026-09-26"}
    env["manifest"].write_text(json.dumps(m))
    r = run(env, "check")
    assert r.returncode == 1 and "missing-dir:sh-ghost" in r.stdout


def test_check_fails_on_duplicate_key(env):
    text = env["manifest"].read_text().replace('"sh-b": {', '"sh-a": {"status":"retired","since":"x"}, "sh-b": {', 1)
    env["manifest"].write_text(text)
    r = run(env, "check")
    assert r.returncode == 1 and "duplicate-key:sh-a" in r.stdout


def test_check_fails_on_empty_dir(env):
    (env["skills"] / "sh-empty").mkdir()
    r = run(env, "check")
    assert r.returncode == 1 and "empty-dir:sh-empty" in r.stdout


def test_check_reports_runtime_drift_without_failing(env):
    (env["runtime"] / "sh-a" / "SKILL.md").write_text("# edited in runtime\n")
    r = run(env, "check")
    assert r.returncode == 0 and "runtime-diverged:sh-a" in r.stdout


def test_promote_copies_and_records_digest(env):
    r = run(env, "promote", "sh-b")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (env["runtime"] / "sh-b" / "SKILL.md").read_text() == "# skill\n"
    e = load(env)["sh-b"]
    assert e["status"] == "global" and e["synced_sha256"] == sha(env["skills"] / "sh-b" / "SKILL.md")


def test_promote_refuses_after_runtime_edit(env):
    assert run(env, "promote", "sh-b").returncode == 0
    (env["runtime"] / "sh-b" / "SKILL.md").write_text("# runtime edit after promote\n")
    (env["skills"] / "sh-b" / "SKILL.md").write_text("# bundle edit\n")
    r = run(env, "promote", "sh-b")
    assert r.returncode == 1 and "runtime-diverged:sh-b" in r.stdout
    assert (env["runtime"] / "sh-b" / "SKILL.md").read_text() == "# runtime edit after promote\n"


def test_retire_moves_bundle_and_removes_runtime_under_guard(env):
    r = run(env, "retire", "sh-a")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (env["skills"] / "sh-a").exists()
    assert (env["retired"] / "sh-a" / "SKILL.md").exists()
    assert not (env["runtime"] / "sh-a").exists()
    assert load(env)["sh-a"]["status"] == "retired"


def test_retire_refuses_on_runtime_divergence(env):
    (env["runtime"] / "sh-a" / "SKILL.md").write_text("# someone edited the live copy\n")
    r = run(env, "retire", "sh-a")
    assert r.returncode == 1 and "runtime-diverged:sh-a" in r.stdout
    assert (env["skills"] / "sh-a").exists() and (env["runtime"] / "sh-a").exists()


def test_record_sets_digest_only_when_identical(env):
    mk_skill(env["skills"], "sh-r", "# same\n"); mk_skill(env["runtime"], "sh-r", "# same\n")
    m = json.loads(env["manifest"].read_text()); m["skills"]["sh-r"] = {"status": "global", "since": "2026-09-26"}
    env["manifest"].write_text(json.dumps(m))
    assert run(env, "record", "sh-r").returncode == 0
    assert load(env)["sh-r"]["synced_sha256"] == sha(env["skills"] / "sh-r" / "SKILL.md")
    (env["runtime"] / "sh-r" / "SKILL.md").write_text("# differs\n")
    r = run(env, "record", "sh-r")
    assert r.returncode == 1 and "not-identical:sh-r" in r.stdout


def test_decoy_runtime_dir_survives_every_subcommand(env):
    for args in (("check",), ("promote", "sh-b"), ("record", "sh-a"), ("retire", "sh-a")):
        run(env, *args)
    assert (env["runtime"] / "_decoy" / "SKILL.md").read_text() == "# not ours\n"


def test_promote_over_unrecorded_runtime_needs_the_reviewed_digest(env):
    """First adoption where the bundle wins (Q13): runtime exists, no digest recorded.
    Plain promote refuses; --expect-runtime-sha must equal the LIVE runtime digest."""
    mk_skill(env["runtime"], "sh-b", "# older runtime copy\n")
    reviewed = sha(env["runtime"] / "sh-b" / "SKILL.md")
    assert "unrecorded-runtime:sh-b" in run(env, "promote", "sh-b").stdout
    r = run(env, "promote", "sh-b", "--expect-runtime-sha", "0" * 64)
    assert r.returncode == 1 and "runtime-diverged:sh-b" in r.stdout
    r = run(env, "promote", "sh-b", "--expect-runtime-sha", reviewed)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (env["runtime"] / "sh-b" / "SKILL.md").read_text() == "# skill\n"
