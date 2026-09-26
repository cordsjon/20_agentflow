---
name: sh-visualization-panel
description: "Multi-expert data visualization review with scoring gate — charts, dashboards, infographics"
---

# /sh:visualization-panel — Data Visualization Review Panel

## Usage

```
/sh:visualization-panel [document_path_or_content] [--mode discussion|critique|socratic] [--focus accuracy|design|accessibility|narrative] [--experts "name1,name2"]
```

## Behavioral Flow

1. **Load Panel Config**: Read `experts/panels/visualization-panel.yaml` for panel definition, focus areas, and auto-select rules
2. **Load Experts**: Read expert files from `experts/individuals/` for each selected expert
3. **Auto-Select Experts**: Scan content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 6` cap
4. **Analyze**: Parse visualization output, data encoding, and design choices
5. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts`. `--experts` override replaces defaults entirely
6. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology
7. **Score**: Rate across 4 dimensions (0-10 each), compute overall score
8. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = needs rework

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension       | Description                                              |
|-----------------|----------------------------------------------------------|
| Accuracy        | Data integrity, proportional encoding, no misleading scales |
| Design Quality  | Visual hierarchy, color usage, typography, whitespace      |
| Accessibility   | Color-blind safe, screen reader support, contrast ratios   |
| Narrative        | Story clarity, insight surfacing, annotation quality       |

**Pass threshold: overall score >= 7.0**

## Expert Panel

| Expert             | Domain                                    |
|--------------------|-------------------------------------------|
| Data Scientist     | Statistical accuracy, data encoding       |
| UX Designer        | Visual hierarchy, interaction design      |
| Statistician       | Proportional representation, scale integrity |
| Domain Expert      | Content accuracy, contextual relevance    |
| Accessibility Specialist | WCAG compliance, inclusive design   |

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative visualization review where experts build upon each other's analysis. Default mode.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues. Each finding includes: specific element, recommendation, and data integrity impact.

### Socratic Mode (`--mode socratic`)
Question-driven exploration of encoding choices, audience assumptions, and narrative decisions.

## Focus Areas

- **accuracy**: Data encoding fidelity, scale integrity, statistical correctness. Lead: Statistician
- **design**: Visual hierarchy, color palette, typography, layout balance. Lead: UX Designer
- **accessibility**: Color-blind safety, contrast, screen reader, WCAG. Lead: Accessibility Specialist
- **narrative**: Story structure, insight density, annotation quality. Lead: Data Scientist

## Output

Visualization review document containing:
- Multi-expert analysis with distinct data-viz perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical accuracy or misleading encoding issues with specific fixes
- Priority-ranked design and narrative improvements

**SYNTHESIS ONLY** — this panel produces analysis and recommendations. It does not modify visualizations without explicit instruction.
