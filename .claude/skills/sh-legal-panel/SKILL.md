---
name: sh-legal-panel
description: "Multi-expert legal and compliance review with scoring gate — contracts, GDPR, licensing, IP"
---

# /sh:legal-panel — Legal & Compliance Review Panel

## Usage

```
/sh:legal-panel [document_path_or_content] [--mode discussion|critique|socratic] [--focus contracts|privacy|licensing|ip] [--experts "name1,name2"]
```

## Behavioral Flow

1. **Load Panel Config**: Read `experts/panels/legal-panel.yaml` for panel definition, focus areas, and auto-select rules
2. **Load Experts**: Read expert files from `experts/individuals/` for each selected expert
3. **Auto-Select Experts**: Scan content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 6` cap
4. **Analyze**: Parse legal content, identify compliance domains and risk areas
5. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts`. `--experts` override replaces defaults entirely
6. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology
7. **Score**: Rate across 4 dimensions (0-10 each), compute overall score
8. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = needs rework

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension       | Description                                              |
|-----------------|----------------------------------------------------------|
| Compliance      | Regulatory coverage (GDPR/DSGVO, ePrivacy, sector-specific) |
| Risk Exposure   | Identified liabilities, indemnification gaps, enforcement risk |
| Clarity         | Contract language precision, unambiguous terms, defined obligations |
| Completeness    | Coverage of all required clauses, edge cases, termination paths |

**Pass threshold: overall score >= 7.0**

## Expert Panel

| Expert                | Domain                                    |
|-----------------------|-------------------------------------------|
| Corporate Lawyer      | Contract structure, liability, governance |
| Data Privacy Specialist | GDPR/DSGVO, data processing agreements  |
| Compliance Officer    | Regulatory frameworks, audit readiness    |
| IP Expert             | Intellectual property, licensing models   |
| Regulatory Analyst    | Sector-specific rules, cross-border issues|

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative review where experts build upon each other's legal analysis. Default mode.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues (CRITICAL / MAJOR / MINOR). Each finding includes: legal basis, specific recommendation, and risk impact.

### Socratic Mode (`--mode socratic`)
Question-driven exploration of legal assumptions and obligations.

## Focus Areas

- **contracts**: Contract terms, liability, SLA, termination. Lead: Corporate Lawyer
- **privacy**: GDPR, data processing, consent, retention. Lead: Data Privacy Specialist
- **licensing**: Software licenses, open source, IP assignment. Lead: IP Expert
- **ip**: Intellectual property protection, trade secrets, patents. Lead: IP Expert

## Output

Legal review document containing:
- Multi-expert analysis with distinct legal perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical compliance gaps with severity and legal basis
- Priority-ranked recommendations with remediation steps

**SYNTHESIS ONLY** — this panel produces analysis and recommendations. It does not draft contracts or make legal decisions without explicit instruction.
