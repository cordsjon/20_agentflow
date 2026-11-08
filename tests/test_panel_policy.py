"""panel_policy.py — deterministic panel resolver (design 2026-11-08-panel-policy-design.md)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import panel_policy as pp  # noqa: E402

STORY = "### US-D-01: {title}\n**As a** dev, **I want** {want}, **so that** y.\n{acs}\n"


def story(title="Thing", want="x", acs="- [ ] AC-01: a"):
    return STORY.format(title=title, want=want, acs=acs)


ROW_BIG = {"project": "00_Governance", "loc": 171994, "test_ratio": 0.41, "src_dirs": 6, "compose": False,
           "db": 110, "svc": 15, "queue": 40, "llm": 80, "cred": 111, "hosts": 46, "mobile": False, "osm": False}
ROW_SMALL = {"project": "25_Hardware", "loc": 6981, "test_ratio": 0.10, "src_dirs": 2, "compose": False,
             "db": 1, "svc": 1, "queue": 0, "llm": 1, "cred": 0, "hosts": 1, "mobile": False, "osm": False}
PROJECTS = {"generated": "2026-11-08", "rows": [ROW_BIG, ROW_SMALL]}


def test_trivial_text_with_two_acs_is_track_none():
    p = pp.resolve(story(want="to add a flag to the exporter", acs="- [ ] AC-01: a\n- [ ] AC-02: b"),
                   None, projects=PROJECTS)
    assert p.track == "none" and p.panels == [] and p.lenses == []
    assert any(r.startswith("trivial:") for r in p.reasons)


def test_trivial_text_with_three_acs_is_normal():
    p = pp.resolve(story(want="to add a flag", acs="- AC-01: a\n- AC-02: b\n- AC-03: c"), None, projects=PROJECTS)
    assert p.track == "normal" and p.panels == ["spec-panel"]


def test_heavy_marker_beats_trivial_text():
    p = pp.resolve(story(want="to add a flag that creates a new table"), None, projects=PROJECTS)
    assert p.track == "heavy" and p.panels[:2] == ["spec-panel", "architecture-panel"]


def test_tags_force_track_and_heavy_wins():
    assert pp.resolve(story(), None, title_tags={"trivial"}, projects=PROJECTS).track == "none"
    p = pp.resolve(story(), None, title_tags={"trivial", "heavy"}, projects=PROJECTS)
    assert p.track == "heavy" and p.basis == "tag"


def test_big_project_gets_architecture_by_measurement():
    p = pp.resolve(story(), "00_Governance", projects=PROJECTS)
    assert p.track == "normal"
    assert p.panels == ["spec-panel", "architecture-panel"]
    assert p.basis == "census:2026-11-08"
    assert "security" in p.lenses  # cred 111 >= 15


def test_low_test_ratio_adds_test_panel():
    p = pp.resolve(story(), "25_Hardware", projects=PROJECTS)
    assert p.panels == ["spec-panel", "test-panel"]


def test_uncensused_project_is_spec_only():
    p = pp.resolve(story(), "99_nope", projects=PROJECTS)
    assert p.panels == ["spec-panel"] and p.basis == "uncensused"
    assert "project:uncensused" in p.reasons


def test_repo_declaration_can_only_add(tmp_path):
    (tmp_path / ".panel-policy.toml").write_text("[policy]\nsecurity = true\narchitecture = false\n")
    p = pp.resolve(story(), "00_Governance", projects=PROJECTS, repo_root=tmp_path)
    assert "security" in p.lenses and "architecture-panel" in p.panels  # false is ignored


def test_project_key_maps_worktree_and_nested_paths(tmp_path):
    home = Path.home() / "projects"
    assert pp.project_key(home / "15_SAAS" / "25_Toolhub" / "BACKLOG.md", use_git=False) == "15_SAAS/25_Toolhub"
    wt = Path.home() / "projects-local" / ".worktrees" / "00_Governance" / "abc123" / "BACKLOG.md"
    assert pp.project_key(wt, use_git=False) == "00_Governance"
    assert pp.project_key(tmp_path / "BACKLOG.md", use_git=False) is None


def test_hash_mismatch_is_rejected(tmp_path):
    doc = {"generated": "2026-11-08", "thresholds": {}, "rows": [ROW_SMALL], "rows_sha256": "00" * 32}
    f = tmp_path / "projects.json"
    f.write_text(json.dumps(doc))
    with pytest.raises(pp.PolicyUnavailable, match="rows_sha256"):
        pp.load_projects(f)


def test_committed_projects_json_hash_is_current():
    doc = pp.load_projects()  # raises PolicyUnavailable on a hand edit
    assert doc["rows"], "projects.json has no rows"


def test_keyword_adds_business_lens_only():
    p = pp.resolve(story(want="to change pricing for the launch"), "25_Hardware", projects=PROJECTS)
    assert "business" in p.lenses and p.panels == ["spec-panel", "test-panel"]


def test_cli_resolve_prints_json(tmp_path, monkeypatch):
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text("# B\n\n## Ready\n\n" + story(title="Thing `[trivial]`"))
    pj = tmp_path / "p.json"
    rows = [ROW_SMALL]
    pj.write_text(json.dumps({"generated": "2026-11-08", "thresholds": {}, "rows": rows,
                              "rows_sha256": pp._rows_hash(rows)}))
    monkeypatch.setenv(pp.PROJECTS_ENV, str(pj))
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "panel_policy.py"), "resolve", str(backlog),
                        "US-D-01", "--json"], capture_output=True, text=True, env=dict(os.environ))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.splitlines()[0])
    assert out["track"] == "none" and out["story"] == "US-D-01"
