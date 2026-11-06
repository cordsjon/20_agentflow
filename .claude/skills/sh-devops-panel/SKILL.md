---
name: sh-devops-panel
description: "Multi-expert DevOps and infrastructure review with scoring gate — CI/CD, infra, monitoring, cost. Use when reviewing pipeline definitions, infrastructure config, monitoring setup, or deployment artifacts before they ship."
---

# /sh:devops-panel — DevOps & Infrastructure Review Panel

## Usage

```
/sh:devops-panel [document_path_or_content] [--mode discussion|critique|socratic] [--focus cicd|infrastructure|monitoring|cost] [--experts "name1,name2"] [--iterations N]
```

## Verbosity

See the **Verbosity** section of `/Users/jcords-macmini/.claude/skills/_panel-shared/PANEL_CORE.md`
— read it; this panel uses it unchanged. Do not copy it here; a verbatim copy drifts
from the source, which is what PANEL_CORE's sync note exists to prevent.

## Behavioral Flow

0. **Load Protocol**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply it IN FULL — every section it defines, including any added after this line was written. This is load-bearing — findings that are not grounded per the protocol, or that do not survive the refute stage, MUST NOT be reported.
1. **Load Panel Config**: Read `experts/panels/devops-panel.yaml` for panel definition, focus areas, and auto-select rules
2. **Load Experts**: Read expert files from `experts/individuals/` for each selected expert
3. **Auto-Select Experts**: Scan content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 6` cap
4. **Analyze**: Parse infrastructure config, pipeline definitions, and deployment artifacts
5. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts`. `--experts` override replaces defaults entirely
6. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology
7. **Score**: Rate across 4 dimensions (0-10 each), compute overall score
8. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold → run the **Below-Gate Loop** in `/Users/jcords-macmini/.claude/skills/_panel-shared/PANEL_CORE.md` (report round 1, fix all findings, re-score, repeat)

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension       | Description                                              |
|-----------------|----------------------------------------------------------|
| Reliability     | Uptime design, failover, rollback capability, blast radius |
| Automation      | Pipeline coverage, manual steps eliminated, reproducibility |
| Observability   | Logging, metrics, alerting, dashboards, incident response  |
| Cost Efficiency | Resource sizing, waste elimination, scaling economics      |

**Pass threshold: overall score >= 7.0**

## Expert Panel

| Expert                    | Domain                                    |
|---------------------------|-------------------------------------------|
| DevOps Engineer           | CI/CD pipelines, deployment strategies    |
| SRE                       | Reliability, SLOs, incident management    |
| Cloud Architect           | Infrastructure design, scaling, networking|
| Security Engineer         | Supply chain security, secrets, hardening |
| Cost Optimisation Specialist | Resource right-sizing, reserved capacity |

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative infrastructure review where experts build upon each other's operational insights. Default mode.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues. Each finding includes: blast radius, specific recommendation, and operational risk.

### Socratic Mode (`--mode socratic`)
Question-driven exploration of infrastructure assumptions, failure modes, and scaling strategy.

## Focus Areas

- **cicd**: Pipeline design, build times, deployment frequency, rollback. Lead: DevOps Engineer
- **infrastructure**: Compute, networking, storage, scaling patterns. Lead: Cloud Architect
- **monitoring**: Observability stack, alerting, dashboards, SLOs. Lead: SRE
- **cost**: Resource utilization, waste, reserved vs. on-demand. Lead: Cost Optimisation Specialist

## Output

DevOps review document containing:
- Multi-expert analysis with distinct operational perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical reliability or security issues with blast radius assessment
- Priority-ranked recommendations with implementation effort

**AUTO-FIX, NOT SYNTHESIS-ONLY** — per `00_Governance/CLAUDE.md §8`, this panel fixes every finding and re-scores. See the **Auto-Fix Policy** and **Below-Gate Loop** sections of `/Users/jcords-macmini/.claude/skills/_panel-shared/PANEL_CORE.md` — read them; this panel uses them unchanged.
