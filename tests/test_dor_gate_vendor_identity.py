"""The DOR gate and its panel-policy resolver are vendored byte-identical in
20_agentflow (origin) and 00_Governance (pipeline consumer). This is the only
thing that keeps the two from drifting. Skips when the sibling checkout is absent.

Inside a session worktree (.worktrees/<repo>/<sid>) the sibling is the SAME session's
worktree of the other repo when one exists, else the other repo's main checkout. Both
repos' land.check runs this suite, so main-vs-worktree alone deadlocks a paired change:
neither side can land first (measured 2026-11-08, git-land exit 6 on both). After the
first side lands its worktree is gone and the second side compares against that main."""
from __future__ import annotations

import filecmp
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
PROJECTS = Path.home() / "projects"
VENDORED = [
    "scripts/dor_gate.py",
    "scripts/panel_policy.py",
    "scripts/panel_policy_data/projects.json",
]


def _sibling_root() -> Path:
    # Worktrees live under projects-local/.worktrees/<repo>/<sid>; map to the main checkout.
    parts = HERE.parts
    if ".worktrees" in parts:
        i = parts.index(".worktrees")
        repo = parts[i + 1]
        other = "20_agentflow" if repo == "00_Governance" else "00_Governance"
        paired = Path(*parts[: i + 1], other, *parts[i + 2 : i + 3])  # .worktrees/<other>/<sid>
        if paired.is_dir():
            return paired
        return PROJECTS / other
    other = "20_agentflow" if HERE.name == "00_Governance" else "00_Governance"
    return PROJECTS / other


@pytest.mark.parametrize("rel", VENDORED)
def test_vendored_file_is_byte_identical(rel):
    other = _sibling_root() / rel
    mine = HERE / rel
    if not other.exists():
        pytest.skip(f"sibling checkout missing {other}")
    assert mine.exists(), f"{mine} missing — vendor it"
    assert filecmp.cmp(mine, other, shallow=False), f"{rel} differs from {other}"
