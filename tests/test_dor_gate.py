"""dor_gate.py — executable Definition of Ready (US-SH2-02 AC-1/AC-2).
One pass + one fail per track, stale score, ambiguous id, section transition,
mixed title forms, body cross-reference. Fixtures under tests/fixtures/backlog_*.md.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "dor_gate.py"
FIX = ROOT / "tests" / "fixtures"


def body_digest(spec: Path) -> str:
    text = spec.read_text(encoding="utf-8")
    for marker in ("\n## Duo review", "\n## Codex review"):
        if marker in text:
            text = text.split(marker)[0]
            break
    return hashlib.sha256(text.encode()).hexdigest()[:12]


@pytest.fixture
def work(tmp_path):
    """Copy fixtures into tmp_path and fill DIGEST so the score matches spec_ok.md."""
    for p in FIX.glob("*.md"):
        shutil.copy(p, tmp_path / p.name)
    d = body_digest(tmp_path / "spec_ok.md")
    for p in tmp_path.glob("backlog_*.md"):
        p.write_text(p.read_text().replace("DIGEST", d))
    return tmp_path


def run(backlog: Path, selector: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GATE), str(backlog), selector, "--json", *extra],
                          capture_output=True, text=True)


def verdict(r):
    return json.loads(r.stdout.splitlines()[0])


def test_normal_pass(work):
    r = run(work / "backlog_normal_pass.md", "Widget — the epic")
    assert r.returncode == 0, r.stdout + r.stderr
    v = verdict(r)
    assert v["pass"] is True and v["track"] == "normal" and v["reasons"] == []


def test_normal_fail_low_score_and_no_link(work):
    r = run(work / "backlog_normal_fail.md", "Widget — the epic")
    assert r.returncode == 1
    reasons = verdict(r)["reasons"]
    assert any(x.startswith("score-below-7.0") for x in reasons)
    assert "no-spec-link" in reasons


def test_stale_score_after_uncommitted_body_edit(work):
    spec = work / "spec_ok.md"
    spec.write_text(spec.read_text().replace("- AC-2: the widget persists.", "- AC-2: the widget persists forever."))
    r = run(work / "backlog_normal_pass.md", "Widget — the epic")
    assert r.returncode == 1
    assert "stale-score" in verdict(r)["reasons"]


def test_appending_a_review_round_keeps_score_valid(work):
    spec = work / "spec_ok.md"
    spec.write_text(spec.read_text() + "\n## Codex review — round 2\nmore notes\n")
    assert run(work / "backlog_normal_pass.md", "Widget — the epic").returncode == 0


def test_buglite_pass(work):
    r = run(work / "backlog_buglite_pass.md", "Crash on save")
    assert r.returncode == 0, r.stdout
    assert verdict(r)["track"] == "bug-lite"


def test_buglite_fail_names_each_missing_line(work):
    r = run(work / "backlog_buglite_fail.md", "Crash on save")
    assert r.returncode == 1
    reasons = verdict(r)["reasons"]
    assert "dor-lite-missing:regression-test" in reasons
    assert "dor-lite-missing:estimate" in reasons


def test_hotfix_pass(work):
    r = run(work / "backlog_hotfix_pass.md", "Crash on save")
    assert r.returncode == 0, r.stdout
    assert verdict(r)["track"] == "hotfix"


def test_hotfix_fail(work):
    r = run(work / "backlog_hotfix_fail.md", "Crash on save")
    assert r.returncode == 1
    assert "dor-lite-missing:root-cause" in verdict(r)["reasons"]


def test_track_override(work):
    r = run(work / "backlog_buglite_pass.md", "Crash on save", "--track", "normal")
    assert r.returncode == 1  # a bug entry judged as a feature has no US/score
    assert verdict(r)["track"] == "normal"


def test_ambiguous_id_exit_2(work):
    r = run(work / "backlog_ambiguous.md", "US-A-01")
    assert r.returncode == 2
    assert verdict(r)["reasons"] == ["ambiguous-id"]


def test_not_found_exit_2(work):
    r = run(work / "backlog_normal_pass.md", "US-NOPE-99")
    assert r.returncode == 2
    assert verdict(r)["reasons"] == ["not-found"]


def test_section_transition_not_absorbed(work):
    r = run(work / "backlog_section_transition.md", "US-T-01", "--skip-score")
    v = verdict(r)
    assert r.returncode == 0, r.stdout
    assert v["counts"]["ac"] == 1, "AC-99 under ## Critical Path was absorbed into the story"


def test_mixed_title_forms(work):
    assert run(work / "backlog_mixed.md", "US-M-01", "--skip-score").returncode == 0
    assert run(work / "backlog_mixed.md", "List form").returncode == 0


def test_body_crossref_does_not_count_as_title(work):
    r = run(work / "backlog_crossref.md", "US-X-01", "--skip-score")
    assert r.returncode == 0, r.stdout
    assert verdict(r)["story"] == "US-X-01"


def test_skip_score_only_skips_score(work):
    # backlog_normal_fail.md has no spec link: with the score skipped the entry still
    # has no US/AC of its own and nothing to read them from.
    r = run(work / "backlog_normal_fail.md", "Widget — the epic", "--skip-score")
    assert r.returncode == 1, r.stdout
    assert verdict(r)["reasons"] == ["no-user-story"]


def test_human_output_ends_with_verdict_line(work):
    r = subprocess.run([sys.executable, str(GATE), str(work / "backlog_buglite_fail.md"), "Crash on save"],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.rstrip().splitlines()[-1].startswith("DOR-VERDICT: FAIL: dor-lite-missing:")


def test_multi_segment_id_and_body_bullets_mentioning_it(work):
    """Governance ids have several segments (US-GOV-DEBT-41) and story bodies hold
    `- **X** — … US-GOV-DEBT-41/…` bullets. Live run 2026-09-26: 26/39 Governance stories
    failed no-user-story and one was ambiguous-id until both were handled."""
    r = run(work / "backlog_multiseg.md", "US-GOV-DEBT-41", "--skip-score")
    v = verdict(r)
    assert r.returncode == 0, r.stdout
    assert v["story"] == "US-GOV-DEBT-41" and v["counts"] == {"us": 1, "ac": 1}
