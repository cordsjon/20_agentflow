## Findings — DEEPSEEK  

### [CRITICAL] Missing referenced governance artifacts  
- **What:** The spec repeatedly cites files that do not exist in the repository: `00_Governance/TENETS.md`, `00_Governance/scripts/sync-global-skills.sh`, `00_Governance/scripts/install_repo_hooks.py`, `CLAUDE.md`, and the target `DOCTRINE.md` that the v2 design is supposed to create.  
- **Where:** Throughout the document (e.g., “One source per rule. … Rules live in Governance (`TENETS.md`, `KNOWN_PATTERNS.md`, `CLAUDE.md`).” – first paragraph of *Design principles*; US‑SH2‑01 “replace … by one `DOCTRINE.md`”; US‑SH2‑03 AC‑1 referencing `install_repo_hooks.py`; US‑SH2‑04 AC‑2 referencing `sync-global-skills.sh`).  
- **Why it matters:** Without these files the implementation plan cannot be executed; any automation that expects them will fail, and the “single source of truth” principle cannot be satisfied.  
- **Suggested fix:** Add the missing files to the repo (or correct the spec to point at the actual existing paths). If the files are intended to live in the `00_Governance` sub‑repo, either include them as a submodule or adjust the spec to reference the correct location. Explicitly list the expected path and a brief stub for each missing artifact.  
- **Confidence:** high  

### [CRITICAL] Acceptance criteria that contradict current state  
- **What:** US‑SH2‑01 AC‑1 requires `grep -rn "sc:" *.md .claude/skills` to return zero hits, yet the audit findings (point 3) state that `DOD.md` still contains five `sc:` references and `DOR.md` contains three.  
- **Where:** US‑SH2‑01 AC‑1 (under *Scope — user stories*); Audit finding 3 ( “The DOD queue tail is dead … `DOD.md:43-49` chains `/sc:…` …”).  
- **Why it matters:** The acceptance test is impossible to satisfy unless the spec first removes those `sc:` references, which is not described elsewhere. This creates a dead‑end for the implementation team.  
- **Suggested fix:** Either (a) update the acceptance criterion to reflect the intended post‑v2 state (e.g., “no `sc:` references remain after migration”) and add a story that removes them, or (b) amend the audit findings to note that those references will be eliminated as part of the v2 work.  
- **Confidence:** high  

### [CRITICAL] Undefined commands referenced in acceptance criteria  
- **What:** US‑SH2‑03 AC‑1 mentions `/sh:verify` and `/sh:finish` as required gates, but a search of `~/.claude/commands` and `~/.claude/skills` shows no such commands.  
- **Where:** US‑SH2‑03 AC‑1 ( “`install_repo_hooks.py` v4 gates + `/sh:verify` + `/sh:finish`”).  
- **Why it matters:** The DOD replacement cannot be validated without concrete command implementations; CI tests will fail and operators will have no runnable gate.  
- **Suggested fix:** Define and implement the two missing commands (or rename the acceptance criteria to use existing commands). Include their file locations in the spec.  
- **Confidence:** high  

### [IMPORTANT] Ambiguous decision about namespace migration  
- **What:** The “Decisions for the operator” section lists a recommendation to keep the `sh:` namespace but flags “Unknown: whether any dagu DAG or Hermes chain calls `agentflow:*` by name.” No plan is provided to discover or mitigate this risk.  
- **Where:** Decision 1 under *Decisions for the operator (Decide)*.  
- **Why it matters:** If any external workflow still references `agentflow:*`, retiring that namespace will break those pipelines, causing production outages.  
- **Suggested fix:** Add a concrete investigation step (e.g., grep all DAG definitions, CI configs, and deployment scripts for `agentflow:` prefixes) before the namespace migration, and record the result as a gating condition.  
- **Confidence:** medium  

### [IMPORTANT] Incomplete specification of skill‑promotion workflow  
- **What:** US‑SH2‑04 AC‑1 and AC‑2 require `skills-lock.json` regeneration and that `sync-global-skills.sh` produce a matching list, yet the spec does not define the format of `skills-lock.json`, the exact steps for regeneration, or how to verify the list equality.  
- **Where:** US‑SH2‑04 (user story) and the earlier audit finding 4 referencing `sync-global-skills.sh`.  
- **Why it matters:** Without a precise contract, developers may produce divergent lock files, leading to inconsistent skill sets across environments.  
- **Suggested fix:** Add a brief schema for `skills-lock.json` (e.g., list of skill IDs with status enum), and a verification command such as `diff <(cat skills-lock.json) <(sync-global-skills.sh --dry-run)`. Include these in the acceptance criteria.  
- **Confidence:** medium  

### [IMPORTANT] Unclear provenance of panel‑usage observation log  
- **What:** US‑SH2‑05 asks to count invocations from “the skill‑invocation observations the hooks already capture,” but the spec does not identify where that log is stored, its format, or whether it includes non‑`/private/tmp` sessions.  
- **Where:** US‑SH2‑05 (user story) – the “Unknown” note in the story description.  
- **Why it matters:** The measurement cannot be performed reliably, making the story impossible to complete and risking inaccurate panel retirement decisions.  
- **Suggested fix:** Document the exact log location (e.g., `~/.claude/logs/skill-invocations.jsonl`), its schema, and any filtering needed. If the log does not exist, add a task to create it before the measurement story.  
- **Confidence:** medium  

### [NIT] Inconsistent terminology for “gate” vs “command”  
- **What:** The spec sometimes calls a gate a “CLI/hook” (Design principle) and elsewhere a “command” (e.g., “No command is named that does not resolve in `~/.claude/commands`”). The mixed terminology could confuse implementers.  
- **Where:** Throughout *Design principles* and US‑SH2‑03 AC‑1.  
- **Why it matters:** Ambiguity may lead to duplicated implementations (one as a CLI, another as a skill) or missed validation steps.  
- **Suggested fix:** Choose a single term (e.g., “gate”) and define it early in the spec, then use it consistently.  
- **Confidence:** low  

### [NIT] Missing link to the “FIPD” definition  
- **What:** The spec mentions “FIPD with the mandatory `Unknown:` clause” but does not provide a reference or definition for “FIPD”.  
- **Where:** Audit finding 9 and US‑SH2‑01 AC‑2.  
- **Why it matters:** Readers unfamiliar with the acronym may not understand the requirement, leading to incomplete implementation.  
- **Suggested fix:** Add a brief definition or a link to the section in `KNOWN_PATTERNS.md` where FIPD is defined.  
- **Confidence:** low  

## Self‑flagged uncertainty  

- The exact location of the “skill‑invocation observations” log (US‑SH2‑05) is unknown; I assume it exists somewhere in `~/.claude/` based on prior patterns, but the repo may not contain it.  
- Whether any external CI pipelines already reference `agentflow:*` namespaces is not searchable from the provided bundle; I flagged it as an unknown risk but cannot confirm its presence.  
- The spec’s “measure before consolidating” principle references a “third” threshold; I am not certain what numeric value “abstract‑on‑third” maps to, but it does not affect the concrete findings above.  