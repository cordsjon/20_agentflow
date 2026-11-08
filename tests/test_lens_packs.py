"""Lens packs — experts/lenses/<name>.yaml — are what panel_policy.Policy.lenses names and
what /sh:spec-panel loads on `--lenses`. Design: docs/superpowers/specs/2026-11-08-panel-policy-design.md
§Roster. Shape + wiring only; whether the model then applies a checklist is not claimed here."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
LENSES = ROOT / "experts" / "lenses"
PANELS = ROOT / "experts" / "panels"
INDIVIDUALS = ROOT / "experts" / "individuals"
COMMANDS = ROOT / ".claude" / "commands" / "global" / "sh"
sys.path.insert(0, str(ROOT / "scripts"))
import panel_policy as pp  # noqa: E402

LENS_NAMES = ["security", "mobile", "osm", "business"]


def _lens_files() -> list[Path]:
    return sorted(LENSES.glob("*.yaml"))


def test_lens_set_matches_resolver_order():
    """A lens the resolver can name must exist as a file, and vice versa."""
    assert {f.stem for f in _lens_files()} == set(pp.LENS_ORDER) == set(LENS_NAMES)


@pytest.mark.parametrize("f", _lens_files(), ids=lambda f: f.stem)
def test_lens_pack_shape(f: Path):
    d = yaml.safe_load(f.read_text(encoding="utf-8"))
    assert set(d) >= {"name", "description", "applies_when", "experts", "checklist"}, set(d)
    assert d["name"] == f.stem
    assert 2 <= len(d["experts"]) <= 3, "a lens is 2-3 experts appended to spec-panel"
    for e in d["experts"]:
        assert (INDIVIDUALS / f"{e}.md").is_file(), f"unknown expert id {e}"
    assert len(d["checklist"]) >= 3 and all(isinstance(c, str) and c.strip() for c in d["checklist"])


@pytest.mark.parametrize("name", LENS_NAMES)
def test_lens_panel_yaml_is_gone_and_command_is_an_alias(name: str):
    assert not (PANELS / f"{name}-panel.yaml").exists(), "one source of truth: the lens YAML"
    alias = (COMMANDS / f"{name}-panel.md").read_text(encoding="utf-8")
    assert f"--lenses {name}" in alias, "alias must force its own lens"
    assert "PANEL_PROTOCOL" in alias, "wiring check (test_panel_propagation) must still see it"
    assert f"panels/{name}-panel.yaml" not in alias, "alias must not point at the deleted YAML"


def test_ai_panel_is_retired():
    assert not (PANELS / "ai-panel.yaml").exists()
    assert not (COMMANDS / "ai-panel.md").exists()
    assert (ROOT / ".claude" / "skills-retired" / "sh-ai-panel").is_dir()
