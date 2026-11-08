---
name: sh-marketing-panel
description: "Multi-expert marketing strategy review with scoring gate — copy, positioning, go-to-market. Use when reviewing positioning, a launch plan, growth strategy, or marketing copy before a campaign goes out."
---

# /sh:marketing-panel — Marketing Strategy Review Panel

## Usage

```
/sh:marketing-panel [document_path_or_content] [--mode discussion|critique|socratic] [--focus positioning|content|growth|launch] [--experts "name1,name2"] [--iterations N]
```

## Verbosity

See the **Verbosity** section of `/Users/jcords-macmini/.claude/skills/_panel-shared/PANEL_CORE.md`
— read it; this panel uses it unchanged. Do not copy it here; a verbatim copy drifts
from the source, which is what PANEL_CORE's sync note exists to prevent.

## Behavioral Flow

0. **Load Protocol**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply it IN FULL — every section it defines, including any added after this line was written. This is load-bearing — findings that are not grounded per the protocol, or that do not survive the refute stage, MUST NOT be reported.
1. **Load Panel Config**: Read `experts/panels/marketing-panel.yaml` for panel definition, focus areas, and auto-select rules
2. **Load Experts**: Read expert files from `experts/individuals/` for each selected expert
3. **Auto-Select Experts**: Scan content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 6` cap
4. **Analyze**: Parse marketing content, identify strategic themes and channels
5. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts`. `--experts` override replaces defaults entirely
6. **Conduct Review**: Run analysis in the selected mode using each expert's distinct framework
7. **Score**: Rate across 4 dimensions (0-10 each), compute overall score
8. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold → run the **Below-Gate Loop** in `/Users/jcords-macmini/.claude/skills/_panel-shared/PANEL_CORE.md` (report round 1, fix all findings, re-score, repeat)

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension       | Description                                              |
|-----------------|----------------------------------------------------------|
| Positioning     | Clarity of value proposition, differentiation, audience fit |
| Message Quality | Copy effectiveness, tone consistency, call-to-action strength |
| Channel Fit     | Right message for right channel, format appropriateness    |
| Measurability   | KPIs defined, attribution model, success criteria clear    |

**Pass threshold: overall score >= 7.0**

## Expert Panel

| Expert             | Domain                                    |
|--------------------|-------------------------------------------|
| CMO                | Strategy, brand architecture, budgeting   |
| Content Strategist | Editorial planning, content-market fit    |
| Growth Hacker      | Acquisition loops, viral mechanics, A/B   |
| Brand Specialist   | Visual identity, tone of voice, consistency|
| Analytics Expert   | Attribution, conversion, funnel analysis  |

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative analysis where experts build upon each other's marketing insights. Default mode.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues. Each finding includes: expert attribution, specific recommendation, and expected impact.

### Socratic Mode (`--mode socratic`)
Question-driven exploration of marketing assumptions, audience understanding, and positioning choices.

## Focus Areas

- **positioning**: Value proposition, competitive differentiation, audience segmentation. Lead: CMO
- **content**: Copy quality, editorial strategy, content-market fit. Lead: Content Strategist
- **growth**: Acquisition channels, retention loops, viral mechanics. Lead: Growth Hacker
- **launch**: Go-to-market planning, launch sequencing, PR strategy. Lead: CMO

## Output

Marketing review document containing:
- Multi-expert analysis with distinct marketing perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical positioning or messaging gaps with severity
- Priority-ranked recommendations with expected impact

**AUTO-FIX, NOT SYNTHESIS-ONLY** — per `00_Governance/CLAUDE.md §8`, this panel fixes every finding and re-scores. See the **Auto-Fix Policy** and **Below-Gate Loop** sections of `/Users/jcords-macmini/.claude/skills/_panel-shared/PANEL_CORE.md` — read them; this panel uses them unchanged.
