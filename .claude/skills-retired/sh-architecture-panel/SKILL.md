---
name: sh-architecture-panel
description: "Multi-expert architecture review — boundaries, integration patterns, failure modes, evolvability"
---

# /sh:architecture-panel — Expert Architecture Review Panel

## Usage

```
/sh:architecture-panel [content|@file] [--mode discussion|critique|socratic|debate] [--focus boundaries|integration|reliability|evolution] [--experts "name1,name2"] [--iterations N] [--verbose]
```

## Shared Core

0. **Load shared core**: Read `~/.claude/skills/_panel-shared/PANEL_CORE.md` and follow its Verbosity, Expert Loading, Auto-Fix Policy, and Output Contract sections verbatim.

## Behavioral Flow

0. **Load Protocol**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply it IN FULL — every section it defines, including any added after this line was written. This is load-bearing — findings that are not grounded per the protocol, or that do not survive its refute stage, MUST NOT be reported.
1. **Load Panel Config**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/panels/architecture-panel.yaml` for panel definition, focus areas, auto-select rules, and scoring config (absolute path — relative paths fail when CWD is outside agentflow).
2. **Load Experts**: Read expert files from `/Users/jcords-macmini/projects/20_agentflow/experts/individuals/` for each selected expert.
3. **Auto-Select Experts**: Scan the content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 6` cap.
4. **Analyze**: Parse architecture content (spec / diff / module diagram), identify boundaries, contracts, integration seams, failure-handling gaps.
5. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts` from panel YAML. `--experts` override replaces defaults entirely.
6. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology.
7. **Score**: Rate the design across 4 dimensions (0-10 each), compute overall score.
8. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = design needs rework.

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative architecture refinement. Experts build on each other's observations sequentially — boundary critique flows into integration concerns flow into failure-mode review.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified findings (CRITICAL / MAJOR / MINOR). Each finding includes expert attribution, the architectural assumption it challenges, a concrete recommendation, and the cost of leaving it unfixed.

### Socratic Mode (`--mode socratic`)
Foundational questioning — "what's the seam?", "where does this fail?", "how does this change look in two years?". No direct answers; forces the author to defend the design.

### Debate Mode (`--mode debate`)
Two-camp adversarial format. Experts split into pro-design and skeptic positions, exchange three rounds, and the panel runner synthesizes the disagreement into explicit trade-off statements.

## Focus Areas

- **boundaries**: Module/service boundaries, contracts, coupling, cohesion, dependency direction. Lead: Sam Newman. Experts: Newman, Fowler, Hohpe.
- **integration**: Inter-service patterns, message exchange, eventual consistency, idempotency. Lead: Gregor Hohpe. Experts: Hohpe, Newman, Nygard.
- **reliability**: Failure modes, circuit breakers, bulkheads, timeouts, degradation paths. Lead: Michael Nygard. Experts: Nygard, Newman, Hohpe.
- **evolution**: Change cost, versioning strategy, refactor paths, abstraction maturity. Lead: Martin Fowler. Experts: Fowler, Newman.

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension                  | Description                                                                                              |
|----------------------------|----------------------------------------------------------------------------------------------------------|
| Boundary clarity           | Are module/service boundaries explicit, with one-way dependency arrows and unambiguous contracts at each seam |
| Integration correctness    | Are integration patterns appropriate; idempotency, ordering, and delivery guarantees handled explicitly |
| Failure-mode coverage      | Are failure modes named and addressed; timeouts, retries, circuit-breakers, fallbacks specified where needed |
| Evolvability               | Can the design absorb foreseeable change without rewrites; versioning and migration paths exist          |

**Pass threshold: overall score >= 7.0**

## Output

Architecture review document containing:
- Multi-expert analysis with distinct perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical issues with severity and architectural assumption challenged
- Consensus points and disagreements (with explicit trade-off statements in debate mode)
- Priority-ranked improvement recommendations

Auto-fix behavior and the machine-readable PANEL-VERDICT output contract come from the shared core (step 0).
