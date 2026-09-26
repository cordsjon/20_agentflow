---
name: sh-content-panel
description: "Multi-expert content quality review with scoring gate — articles, docs, written content"
---

# /sh:content-panel — Content Quality Review Panel

## Usage

```
/sh:content-panel [document_path_or_content] [--mode discussion|critique|socratic] [--focus structure|clarity|seo|audience] [--experts "name1,name2"]
```

## Behavioral Flow

1. **Load Panel Config**: Read `experts/panels/content-panel.yaml` for panel definition, focus areas, and auto-select rules
2. **Load Experts**: Read expert files from `experts/individuals/` for each selected expert
3. **Auto-Select Experts**: Scan content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 6` cap
4. **Analyze**: Parse written content, identify structure, tone, and audience fit
5. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts`. `--experts` override replaces defaults entirely
6. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology
7. **Score**: Rate across 4 dimensions (0-10 each), compute overall score
8. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = needs rework

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension       | Description                                              |
|-----------------|----------------------------------------------------------|
| Structure       | Logical flow, section progression, narrative arc          |
| Clarity         | Sentence precision, jargon management, readability level  |
| Depth           | Evidence quality, specificity, insight density            |
| Audience Fit    | Tone match, assumed knowledge level, actionability        |

**Pass threshold: overall score >= 7.0**

## Expert Panel

| Expert             | Domain                                    |
|--------------------|-------------------------------------------|
| Editor             | Structural editing, narrative flow, cuts   |
| Content Strategist | Editorial planning, content-market fit    |
| SEO Specialist     | Search intent, keyword density, metadata  |
| Technical Writer   | Accuracy, terminology, procedural clarity |
| Audience Expert    | Reader persona, engagement, readability   |

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative editorial review where experts build upon each other's feedback. Default mode.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues. Each finding includes: specific location, recommendation, and quality impact.

### Socratic Mode (`--mode socratic`)
Question-driven exploration of authorial intent, audience assumptions, and structural choices.

## Focus Areas

- **structure**: Document organization, flow, section balance. Lead: Editor
- **clarity**: Language precision, readability, jargon. Lead: Technical Writer
- **seo**: Search optimization, metadata, keyword strategy. Lead: SEO Specialist
- **audience**: Reader persona match, engagement, actionability. Lead: Audience Expert

## Output

Content review document containing:
- Multi-expert analysis with distinct editorial perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical quality issues with specific locations and fixes
- Priority-ranked recommendations for improvement

**SYNTHESIS ONLY** — this panel produces analysis and recommendations. It does not rewrite content without explicit instruction.
