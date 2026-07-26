"""Panel-protocol propagation checks.

WHY THIS EXISTS
---------------
US-AF-05 (split from US-AF-03, 2026-07-26). Two facts, both verified by adversarial
review across two codex rounds:

1. Every `sh-*-panel/SKILL.md` names the protocol sections it applies
   ("apply its Grounding and Refute Stage sections"). That is a named-section
   ALLOWLIST: adding a stage to PANEL_PROTOCOL.md leaves it inert in all of them.
2. Of 17 panel skills, only 10 load the protocol at all. 7 load neither it nor
   PANEL_CORE.md, so they can report ungrounded, un-refuted findings.

These tests pin the population and the wiring so both facts are enforced rather
than periodically rediscovered by hand.

SCOPE: presence and wiring only. A green run proves each skill READS the shared
protocol -- it proves nothing about whether the model then FOLLOWS it. Behavioural
evidence is out of scope here and is not claimed (see US-AF-03).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# The LIVE skill tree. `~/.claude/skills` is what the harness loads; the copies
# under 20_agentflow/.claude/skills/ are a pre-2026-06-26 fork that predates the
# PANEL_CORE.md extraction (11 of 18 still inline Verbosity/Expert Loading).
# Tracked as US-AF-06 -- see test_agentflow_fork_is_not_silently_live below.
SKILLS_DIR = Path.home() / ".claude" / "skills"
AGENTFLOW_SKILLS = (
    Path.home() / "projects" / "20_agentflow" / ".claude" / "skills"
)
PANEL_CORE = SKILLS_DIR / "_panel-shared" / "PANEL_CORE.md"
PANEL_PROTOCOL = (
    Path.home() / "projects" / "20_agentflow" / "experts" / "PANEL_PROTOCOL.md"
)

# The 7 skills that loaded neither shared file when US-AF-05 was written
# (2026-07-26). Listed explicitly so fixing one is a deliberate, visible edit
# rather than a silently shrinking xfail.
KNOWN_UNWIRED = {
    "sh-4-reviewer-panel",
    "sh-content-panel",
    "sh-devops-panel",
    "sh-legal-panel",
    "sh-marketing-panel",
    "sh-visualization-panel",
}
# Removed 2026-07-26: sh-claude-code-panel, when its verbatim Verbosity copy was
# replaced by a reference to PANEL_CORE.md. 6 remain for US-AF-04.


def panel_skills() -> list[Path]:
    """Every sh-*panel* skill directory containing a SKILL.md."""
    return sorted(
        p / "SKILL.md"
        for p in SKILLS_DIR.glob("sh-*panel*")
        if (p / "SKILL.md").is_file()
    )


def wired_skills() -> list[Path]:
    """Panel skills that reference the shared protocol or core."""
    return [
        f
        for f in panel_skills()
        if "PANEL_PROTOCOL" in f.read_text() or "PANEL_CORE" in f.read_text()
    ]


def test_shared_files_exist():
    assert PANEL_PROTOCOL.is_file(), f"missing {PANEL_PROTOCOL}"
    assert PANEL_CORE.is_file(), f"missing {PANEL_CORE}"


def test_panel_population_is_discovered():
    """Guard the denominator. A glob returning 0 would make every other test
    here vacuously green -- the 'live test asserting nothing' failure mode."""
    skills = panel_skills()
    assert len(skills) >= 15, f"expected >=15 panel skills, found {len(skills)}"


@pytest.mark.parametrize("skill", wired_skills(), ids=lambda p: p.parent.name)
def test_wired_skills_apply_protocol_wholesale(skill: Path):
    """No skill may enumerate an allowlist of protocol sections.

    'apply its Grounding and Refute Stage sections' silently ignores every
    stage added later. Wholesale application ('apply it in full') is the only
    form that survives a protocol change.
    """
    text = skill.read_text()
    allowlist = re.search(
        r"apply\s+its\s+Grounding[^.]*?and\s+Refute\s+Stage\s+sections",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    assert allowlist is None, (
        f"{skill.parent.name} enumerates protocol sections instead of applying the "
        f"protocol wholesale; a new stage would be inert here. Found: "
        f"{allowlist.group(0)[:80]!r}"
    )


@pytest.mark.parametrize(
    "skill", panel_skills(), ids=lambda p: p.parent.name
)
def test_every_panel_loads_shared_protocol(skill: Path):
    """Every panel skill must load the shared protocol.

    The 7 in KNOWN_UNWIRED are a pre-existing defect tracked by US-AF-04; they
    xfail rather than silently pass, so fixing one flips to XPASS and prompts
    removal from the list.
    """
    name = skill.parent.name
    text = skill.read_text()
    wired = "PANEL_PROTOCOL" in text or "PANEL_CORE" in text
    if name in KNOWN_UNWIRED:
        pytest.xfail(f"{name} loads no shared protocol (US-AF-04)")
    assert wired, f"{name} references neither PANEL_PROTOCOL nor PANEL_CORE"


def test_known_unwired_list_is_accurate():
    """The xfail list must match reality, or it hides regressions.

    A skill that stops loading the protocol must fail loudly rather than be
    absorbed into a stale allowance list.
    """
    actual_unwired = {
        f.parent.name
        for f in panel_skills()
        if "PANEL_PROTOCOL" not in f.read_text()
        and "PANEL_CORE" not in f.read_text()
    }
    assert actual_unwired == KNOWN_UNWIRED, (
        f"KNOWN_UNWIRED is stale.\n"
        f"  newly unwired: {sorted(actual_unwired - KNOWN_UNWIRED)}\n"
        f"  now wired (remove from list): {sorted(KNOWN_UNWIRED - actual_unwired)}"
    )


def test_agentflow_fork_is_not_silently_live():
    """Pin the denominator problem this suite nearly shipped with.

    Every test here globs ~/.claude/skills. A parallel tree exists at
    20_agentflow/.claude/skills/ (18 panel dirs) which still carries the
    allowlist form. It is a stale pre-2026-06-26 fork -- most of its files
    predate the PANEL_CORE.md extraction -- so it is NOT the live tree and is
    deliberately out of scope for US-AF-05.

    This test fails if that assumption stops holding: if the fork ever gains the
    PANEL_CORE wiring, it is being maintained again and must be brought into
    this suite's population rather than left to overwrite the live tree on the
    next sync. (US-AF-06.)
    """
    if not AGENTFLOW_SKILLS.is_dir():
        pytest.skip("agentflow skill fork not present")
    forked = sorted(AGENTFLOW_SKILLS.glob("sh-*panel*/SKILL.md"))
    if not forked:
        pytest.skip("agentflow skill fork has no panel skills")
    maintained = [f.parent.name for f in forked if "Load shared core" in f.read_text()]
    assert len(maintained) < len(forked), (
        "the agentflow skill fork now loads PANEL_CORE in every panel -- it is "
        "being maintained. Fold it into SKILLS_DIR's population or resolve the "
        "fork (US-AF-06); leaving it out risks a sync overwriting the live fix."
    )


def test_no_verbatim_copies_of_shared_blocks():
    """A VERBATIM copy of a shared block is drift waiting to happen.

    PANEL_CORE.md's header explicitly permits panel-specific deviations inline
    ("Panel-specific deviations live inline in the individual SKILL.md files and
    override the corresponding block here"). So a REWORDED Verbosity block is
    legitimate -- sh-business-panel emits consolidated findings because it has no
    scoring gate. Only a byte-identical copy is the defect: it reads as shared
    text while being a private fork that silently diverges.

    Detection is therefore an exact-sentence match against PANEL_CORE's own
    wording, not a topic keyword.
    """
    core_text = PANEL_CORE.read_text()
    # A distinctive full sentence from PANEL_CORE's Verbosity block. Copies keep
    # it byte-for-byte; genuine rewordings do not.
    canary = (
        "**Silent (default)**: No expert deliberations. Output only: score table, "
        "FIPD-classified findings list, and auto-fix diff."
    )
    assert canary in core_text, (
        "test fixture stale: the canary sentence is no longer in PANEL_CORE.md; "
        "pick a new verbatim sentence from its Verbosity block"
    )
    offenders = [
        f.parent.name for f in panel_skills() if canary in f.read_text()
    ]
    assert not offenders, (
        f"these skills carry a VERBATIM copy of PANEL_CORE's Verbosity block "
        f"instead of loading it: {offenders}"
    )
