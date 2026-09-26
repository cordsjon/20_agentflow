---
name: sh-spec-panel
description: "Multi-expert specification review with scoring gate and quality assessment"
---

# /sh:spec-panel — Expert Specification Review Panel

## Usage

```
/sh:spec-panel [specification_content|@file] [--mode discussion|critique|socratic] [--focus requirements|architecture|testing|compliance] [--experts "name1,name2"] [--iterations N] [--verbose]
```

## Shared Core

0. **Load shared core**: Read `~/.claude/skills/_panel-shared/PANEL_CORE.md` and follow its Verbosity, Expert Loading, Auto-Fix Policy, and Output Contract sections verbatim.

## Behavioral Flow

0. **Load Protocol**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply it IN FULL — every section it defines, including any added after this line was written. This is load-bearing — findings that are not grounded per the protocol, or that do not survive its refute stage, MUST NOT be reported.
1. **Load Panel Config**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/panels/spec-panel.yaml` for panel definition, focus areas, auto-select rules, and scoring config (absolute path — relative paths fail when CWD is outside agentflow)
2. **Load Experts**: Read expert files from `/Users/jcords-macmini/projects/20_agentflow/experts/individuals/` for each selected expert — these files contain the expert's domain, methodology, and critique focus
3. **Auto-Select Experts**: Scan the specification content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 7` cap
4. **Pre-Scoring Checks (deterministic — do NOT delegate to LLM personas):**
    - **Table reconciliation:** If the spec contains 2+ tables with numeric values (counts, totals, "≥ N" thresholds), extract every numeric claim and verify cross-section arithmetic *before* personas opine. Enumerate the items the count refers to in the other sections; assert the math reconciles. Flag any mismatch as a CRITICAL finding up front. Rationale: LLMs reliably hallucinate arithmetic consistency over freeform tables — personas reading personas will not catch it. This step is mechanical, executed by the panel runner, not by an expert voice.
5. **Analyze**: Parse specification content, identify components, gaps, and quality issues
6. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts` from panel YAML. `--experts` override replaces defaults entirely
7. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology
8. **Score**: Rate specification across the 6 dimensions defined in the panel YAML (0-10 each), compute overall score
9. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = specification needs rework

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative improvement through expert dialogue. Experts build upon each other's insights sequentially. Cross-expert validation and consensus building around critical improvements.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues (CRITICAL / MAJOR / MINOR). Each finding includes: expert attribution, specific recommendation, priority ranking, and quality impact estimate.

### Socratic Mode (`--mode socratic`)
Learning-focused questioning to deepen understanding. Experts pose foundational questions about purpose, stakeholders, assumptions, and alternatives. No direct answers — forces the author to think critically.

## Focus Areas

- **requirements**: Requirement clarity, completeness, testability. Lead: Karl Wiegers. Experts: Wiegers, Adzic, Cockburn
- **architecture**: Interface design, boundaries, scalability, patterns. Lead: Martin Fowler. Experts: Fowler, Newman, Hohpe, Nygard
- **testing**: Test strategy, coverage, edge cases, acceptance criteria. Lead: Lisa Crispin. Experts: Crispin, Gregory, Adzic
- **compliance**: Regulatory coverage, security, operational requirements. Lead: Karl Wiegers. Experts: Wiegers, Nygard, Hightower

## Scoring Gate

6 dimensions, each scored 0-10:

| Dimension         | Description                                                              |
|-------------------|-------------------------------------------------------------------------|
| Clarity           | Language precision and understandability                                 |
| Completeness      | Coverage of essential specification elements                            |
| Testability       | Measurability and validation capability                                 |
| Consistency       | Internal coherence and contradiction detection                          |
| Operator-surface  | Every introduced capability reachable by both consumers — human operator (named CLI command + launchpad/menu entry, not just --help) and other agents (a2a registry entry as explicit AC when applicable). Scored from the operator-surface-completeness pre-scoring check; N/A when the spec has no operator-facing surface. |
| Public-readiness  | Would this survive a public GitHub repo without ridicule — OSS hygiene (README, LICENSE, install/usage, examples, tests/CI) + design credibility (no hardcoded paths, secrets, bare excepts, happy-path-only). Weighted by actual public intent. |

**Pass threshold: overall score >= 7.0**

Output includes per-dimension scores, overall score, critical issues, expert consensus points, and an improvement roadmap (immediate / short-term / long-term).

## Output

Specification review document containing:
- Multi-expert analysis with distinct perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical issues with severity and priority
- Consensus points and disagreements
- Priority-ranked improvement recommendations

Auto-fix behavior and the machine-readable PANEL-VERDICT output contract come from the shared core (step 0).
