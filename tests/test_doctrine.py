"""Doctrine invariants for Shepherd v2 (US-SH2-01).

AC-1: no `sc:` namespace reference survives outside the append-only journal.
AC-2: the FIPD table lives in Governance, not here.
AC-3: every /sh:<name> DOCTRINE.md names resolves to a command file.
The four old doctrine files are gone; DOCTRINE.md has the four sections.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SH_COMMANDS = Path.home() / ".claude" / "commands" / "sh"
JOURNALS = {"DECISIONS.md"}  # append-only; historical text is allowed to quote dead names


def _md_files():
    yield from (p for p in ROOT.glob("*.md") if p.name not in JOURNALS)
    yield from (ROOT / ".claude" / "skills").rglob("*.md")


def test_no_sc_namespace_references():
    hits = [f"{p.relative_to(ROOT)}:{i}" for p in _md_files()
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if "sc:" in line]
    assert hits == [], f"sc: references remain: {hits}"


def test_fipd_table_not_defined_here():
    hits = [p.name for p in ROOT.glob("*.md") if "| **Fix** |" in p.read_text(encoding="utf-8")]
    assert hits == [], f"FIPD table still defined in {hits}; it belongs in 00_Governance/KNOWN_PATTERNS.md"


def test_old_doctrine_files_deleted():
    present = [n for n in ("DOR.md", "DOD.md", "KNOWN_PATTERNS.md", "GOVERNANCE-GUIDE.md", "CLAUDE-LOOP.md")
               if (ROOT / n).exists()]
    assert present == [], f"still present: {present}"


def test_doctrine_has_four_sections():
    text = (ROOT / "DOCTRINE.md").read_text(encoding="utf-8")
    for heading in ("## Sources", "## DOR", "## DOD", "## FIPD"):
        assert heading in text, f"missing {heading}"


def test_every_sh_command_in_doctrine_resolves():
    text = (ROOT / "DOCTRINE.md").read_text(encoding="utf-8")
    names = sorted(set(re.findall(r"/sh:([a-z0-9-]+)", text)))
    assert names, "DOCTRINE.md names no /sh: command at all"
    missing = [n for n in names if not (SH_COMMANDS / f"{n}.md").exists()]
    assert missing == [], f"DOCTRINE.md names commands that do not exist: {missing}"
