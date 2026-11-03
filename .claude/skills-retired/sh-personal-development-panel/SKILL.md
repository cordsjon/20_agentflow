---
name: sh-personal-development-panel
description: "Multi-expert personal-development review with scoring gate — learnability, adoption, human-centeredness, and capability impact for talent/learning/AI-augmentation designs"
---

# /sh:personal-development-panel — Expert Personal-Development Review Panel

## Usage

```
/sh:personal-development-panel [specification_content|@file] [--mode discussion|critique|socratic] [--focus learnability|adoption|human-centeredness|capability] [--experts "name1,name2"] [--iterations N] [--verbose]
```

## Shared Core

0. **Load shared core**: Read `~/.claude/skills/_panel-shared/PANEL_CORE.md` and follow its Verbosity, Expert Loading, Auto-Fix Policy, and Output Contract sections verbatim.

## Behavioral Flow

0. **Load Protocol**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply it IN FULL — every section it defines, including any added after this line was written (non-code branch: every finding quotes the source section it rests on). Findings that misquote or cannot cite the source MUST NOT be reported.
1. **Load Panel Config**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/panels/personal-development-panel.yaml` for panel definition, focus areas, auto-select rules, and scoring config (absolute path — relative paths fail when CWD is outside agentflow)
2. **Load Experts**: Read expert files from `/Users/jcords-macmini/projects/20_agentflow/experts/individuals/` for each selected expert — these files contain the expert's domain, methodology, and critique focus
3. **Auto-Select Experts**: Scan the specification content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 8` cap
4. **Pre-Scoring Checks (deterministic — do NOT delegate to LLM personas):**
    - **Table reconciliation:** If the spec contains 2+ tables with numeric values (competence counts, capability-spine size, role-slice membership, "≥ N" thresholds), extract every numeric claim and verify cross-section arithmetic *before* personas opine. Enumerate the items the count refers to in the other sections; assert the math reconciles. Flag any mismatch as a CRITICAL finding up front. Rationale: LLMs reliably hallucinate arithmetic consistency over freeform tables — personas reading personas will not catch it. This step is mechanical, executed by the panel runner, not by an expert voice.
5. **Analyze**: Parse specification content, identify components, gaps, and quality issues
6. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts` from panel YAML. `--experts` override replaces defaults entirely
7. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology
8. **Score**: Rate the design across 4 dimensions (0-10 each), compute overall score
9. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = design needs rework

## Default Panel

The default roster (7 experts) reviews every design unless `--focus` or `--experts` narrows it:

| Expert | Lens | Method |
|---|---|---|
| Dave Ulrich | HR / talent architecture | competency models, HR-from-the-outside-in, receiver-defined value |
| Malcolm Knowles | adult learning (andragogy) | six andragogical principles |
| Jeff Hiatt | change management (individual) | Prosci ADKAR |
| Erik Brynjolfsson | AI enablement / future of work | task-based augment-vs-automate, the Turing Trap |
| Amy Edmondson | psychological safety / teaming | psychological safety, intelligent failure |
| Ravin Jesuthasan | skills-based organization | work deconstruction (jobs→tasks→skills→capabilities) |
| Josh Bersin | enterprise L&D + AI | capability academies, commercialization, maturity models |

Auto-select adds **Stuart Russell** (AI safety / control) when autonomy/agentic/alignment keywords appear, up to the `max-experts: 8` cap.

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative improvement through expert dialogue. Experts build upon each other's insights sequentially. Cross-expert validation and consensus building around critical improvements.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues (CRITICAL / MAJOR / MINOR). Each finding includes: expert attribution, specific recommendation, priority ranking, and quality impact estimate.

### Socratic Mode (`--mode socratic`)
Learning-focused questioning to deepen understanding. Experts pose foundational questions about purpose, learners, assumptions, and alternatives. No direct answers — forces the author to think critically.

## Focus Areas

- **learnability**: Adult-learning fit — why-now framing, learner agency, problem-centered design. Lead: Malcolm Knowles. Experts: Knowles, Ulrich
- **adoption**: Will real people adopt and sustain the behavior — ADKAR rungs and psychological safety. Lead: Jeff Hiatt. Experts: Hiatt, Edmondson
- **human-centeredness**: Trust, safety, augmentation-over-replacement. Lead: Amy Edmondson. Experts: Edmondson, Brynjolfsson
- **capability**: Capability spine integrity, work deconstruction, individual→org→value line of sight. Lead: Ravin Jesuthasan. Experts: Jesuthasan, Ulrich, Brynjolfsson, Bersin

## Scoring Gate

4 dimensions, each scored 0-10:

| Dimension          | Description                                                                 | Owner(s)              |
|--------------------|-----------------------------------------------------------------------------|-----------------------|
| Learnability       | Adult-learning soundness — why-now framing, learner agency, builds on experience | Knowles               |
| Adoption-Readiness | Individual adoption through ADKAR rungs + psychological safety; barrier point named, reinforcement sustains behavior | Hiatt, Edmondson      |
| Human-Centeredness | Human stays central — trust over surveillance, augmentation over replacement (Turing Trap avoided) | Edmondson, Brynjolfsson |
| Capability-Impact  | Capability spine integrity + line of sight from individual competence to organizational capability to receiver-defined value | Ulrich, Jesuthasan    |

**Pass threshold: overall score >= 7.0**

Output includes per-dimension scores, overall score, critical issues, expert consensus points, and an improvement roadmap (immediate / short-term / long-term).

## Output

Personal-development review document containing:
- Multi-expert analysis with distinct perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical issues with severity and priority
- Consensus points and disagreements
- Priority-ranked improvement recommendations

Auto-fix behavior and the machine-readable PANEL-VERDICT output contract come from the shared core (step 0).
