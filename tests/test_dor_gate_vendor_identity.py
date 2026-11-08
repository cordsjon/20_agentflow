"""The DOR gate and its panel-policy resolver are vendored byte-identical in
20_agentflow (origin) and 00_Governance (pipeline consumer). This is the only
thing that keeps the two from drifting. Skips when the sibling checkout is absent."""
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
        repo = parts[parts.index(".worktrees") + 1]
    else:
        repo = HERE.name
    other = "20_agentflow" if repo == "00_Governance" else "00_Governance"
    return PROJECTS / other


@pytest.mark.parametrize("rel", VENDORED)
def test_vendored_file_is_byte_identical(rel):
    other = _sibling_root() / rel
    mine = HERE / rel
    if not other.exists():
        pytest.skip(f"sibling checkout missing {other}")
    assert mine.exists(), f"{mine} missing — vendor it"
    assert filecmp.cmp(mine, other, shallow=False), f"{rel} differs from {other}"
