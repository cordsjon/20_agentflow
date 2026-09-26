"""The DOD is the installed hook chain. This proves each gate refuses its known-bad
input IN A SCRATCH CLONE with the same installer this repo uses (US-SH2-03 AC-2).

Per-gate unit controls live in 00_Governance/tests (verified-tag, reflex,
commit-trailer, spec-hierarchy, decisions-staleness). This file tests the CHAIN:
installer -> hook file -> gate script -> git refuses/warns.

Fixture neutralises the machine's global core.hooksPath (`-c core.hooksPath=.git/hooks`)
so the scratch repo's own hooks fire — feedback_scratch_git_repo_inherits_global_hookspath.
Requires: 00_Governance checked out at ~/projects/00_Governance, python3 on PATH.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

GOV = Path.home() / "projects" / "00_Governance"
INSTALLER = GOV / "scripts" / "install_repo_hooks.py"
TRAILER = "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
FOUR_EPICS = "# Capability: C\n## Solution: S\n" + "".join(
    f"### Epic: E{i}\n#### US-A-0{i}: u\n" for i in range(1, 5))

pytestmark = pytest.mark.skipif(not INSTALLER.exists(), reason="00_Governance not present")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=.git/hooks", *args],
                          capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def _commit(repo: Path, subject: str, *, trailer: bool = True) -> subprocess.CompletedProcess:
    msg = repo.parent / "msg.txt"
    msg.write_text(subject + ("\n\n" + TRAILER + "\n" if trailer else "\n"))
    return _git(repo, "commit", "-q", "-F", str(msg))


def _out(r: subprocess.CompletedProcess) -> str:
    return r.stdout + r.stderr


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "proj"
    r.mkdir()
    for a in (("init", "-q"), ("config", "user.email", "t@t"), ("config", "user.name", "t"),
              ("config", "commit.gpgsign", "false")):
        assert _git(r, *a).returncode == 0
    inst = subprocess.run([sys.executable, str(INSTALLER), str(r)], capture_output=True, text=True)
    assert inst.returncode == 0, _out(inst)
    (r / "README.md").write_text("seed\n")
    _git(r, "add", "README.md")
    seed = _commit(r, "chore: seed")
    assert seed.returncode == 0, _out(seed)
    return r


def test_clean_commit_passes(repo):
    (repo / "ok.py").write_text("def f():\n    return 1\n")
    _git(repo, "add", "ok.py")
    r = _commit(repo, "feat: ok")
    assert r.returncode == 0, _out(r)


def test_verified_tag_gate_blocks(repo):
    (repo / "AUDIT.md").write_text("| W-9 | Investigate | x | no caller | `x.html` | [verified] |\n")
    _git(repo, "add", "AUDIT.md")
    r = _commit(repo, "docs: audit")
    assert r.returncode != 0, "bare [verified] tag was not blocked"
    assert "verified" in _out(r).lower()


def test_spec_hierarchy_gate_blocks(repo):
    p = repo / "docs" / "superpowers" / "specs" / "2026-01-01-bad-design.md"
    p.parent.mkdir(parents=True)
    p.write_text(FOUR_EPICS)
    _git(repo, "add", str(p.relative_to(repo)))
    r = _commit(repo, "docs: spec")
    assert r.returncode != 0, "four-epic spec was not blocked"
    assert "spec-hierarchy" in _out(r)


def test_commit_trailer_gate_blocks(repo):
    (repo / "b.py").write_text("x = 1\n")
    _git(repo, "add", "b.py")
    r = _commit(repo, "feat: no trailer", trailer=False)
    assert r.returncode != 0, "commit without the Co-Authored-By trailer was not blocked"
    assert "commit-trailer" in _out(r)


def test_reflex_gate_warns_but_passes(repo):
    (repo / "app.py").write_text("def f():\n    try:\n        pass\n    except Exception:\n        pass\n")
    _git(repo, "add", "app.py")
    r = _commit(repo, "feat: reflex")
    assert r.returncode == 0, _out(r)
    assert "[reflex]" in _out(r)


def test_decisions_staleness_gate_warns_but_passes(repo):
    ledger = "<!-- AI-maintained, append-only -->\n\n" + "".join(
        f"## Q{i} — t — tradeoff\n\n**Question:** q\n**Chosen:** c\n**Decided-by:** agent\n"
        f"**Justification:** j\n**Outcome:** assumed\n\n" for i in range(1, 13))
    (repo / "DECISIONS.md").write_text(ledger)
    _git(repo, "add", "DECISIONS.md")
    r = _commit(repo, "docs: decisions")
    assert r.returncode == 0, _out(r)
    assert "[decisions-staleness]" in _out(r)
    assert "12 open" in _out(r)


def test_repo_local_gate_runs(repo):
    d = repo / "tools" / "precommit.d"
    d.mkdir(parents=True)
    gate = d / "10-fail"
    gate.write_text("#!/usr/bin/env bash\necho local-gate-ran; exit 1\n")
    gate.chmod(0o755)
    (repo / "c.py").write_text("y = 2\n")
    _git(repo, "add", "c.py", "tools/precommit.d/10-fail")
    r = _commit(repo, "feat: local gate")
    assert r.returncode != 0
    assert "local-gate-ran" in _out(r)
