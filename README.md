# agentflow

**AI-governed Scrumban loop for autonomous dev agents.**

A governance framework that gives AI coding agents (Claude Code, Cursor, Codex, Devin, etc.) a structured execution loop with quality gates, dependency tracking, and autonomous task processing — while keeping humans in control.

---

## What is this?

Most AI coding agents run in one of two modes: fully manual (you prompt every step) or fully autonomous (YOLO). **agentflow** provides the middle ground — a Scrumban pipeline where:

- **Agents execute autonomously** within a bounded loop (pick task, implement, test, commit)
- **Quality gates halt execution** when issues exceed thresholds (no silent failures)
- **Humans control the queue** (what gets built, in what order, with what priority)
- **Skills plug into loop stages** (code review, TDD, security audit — each wired to a specific step)

```
INBOX → BACKLOG (Ideation → Refining → Ready) → TODO-Today → DONE-Today
                                                      ↑
                                               Autopilot Loop
                                          (14 steps, quality-gated)
```

## Core Components

| File | Purpose |
|------|---------|
| [CLAUDE-LOOP.md](CLAUDE-LOOP.md) | The execution loop — 3 nested loops, 14 inner steps, semaphore control |
| [GOVERNANCE-GUIDE.md](GOVERNANCE-GUIDE.md) | Full framework reference — pipeline, quality gates, skill portfolios |
| [DOD.md](DOD.md) | Definition of Done — quality gate before deployment |
| [DOR.md](DOR.md) | Definition of Ready — entry criteria before implementation |
| [ORCHESTRATOR.md](ORCHESTRATOR.md) | Task routing, agent assignment, stall detection |
| [AGENT_CAPABILITIES.md](AGENT_CAPABILITIES.md) | Agent capability matrix for task routing |
| [KNOWN_PATTERNS.md](KNOWN_PATTERNS.md) | Anti-pattern catalog — consult before writing code |
| [SKILLS.md](SKILLS.md) | Complete skill catalog — dependencies, chains, examples, portfolios |

## The Loop (simplified)

```
1. Check semaphore (run/pause)
2. Load context from previous iteration
3. Read first unchecked task from queue
4. Route: assign agent, check deps, preload context
5. Verify task meets Definition of Ready
6. Execute (TDD-first for user stories)
7. Verify acceptance criteria with evidence
8. Self-review changed files
9. Cleanup sub-loop (fix all Low findings)
10. Commit (atomic, conventional)
11. PR + branch cleanup (if feature branch)
12. Move to done, cascade unblocked deps
13. Save context for next session
14. Next task or stop
```

**Key invariant:** Medium+ severity findings pause the loop — the agent stops and asks for human review. No silent quality degradation.

## Quality Gate Stack

```
┌─────────────────────┐
│  GREENLIGHT          │  Project test suite — 100% green
├─────────────────────┤
│  DEEP AUDIT          │  Security/perf/arch scan (M+ tasks)
├─────────────────────┤
│  DEFINITION OF DONE  │  Code quality + architecture + committed + deployable
└─────────────────────┘
```

## Skill Integration

Skills (reusable prompt modules) plug into specific loop stages:

| Loop Stage | Skills |
|------------|--------|
| Execute | `/test-driven-development` |
| Verify | `/verification-before-completion` |
| Review | `/requesting-code-review`, `/receiving-code-review` |
| Cleanup | `/clean-code`, `/production-code-audit` |
| Commit | `/commit-smart` |
| Branch | `/finishing-a-development-branch` |
| Context | `/session-handoff` |
| Retro | `/kaizen` |
| Refine | `/requirements-clarity` |

Plus 4 support process portfolios (GTM, SEO, Intel, Content) and an on-demand toolbox — see [GOVERNANCE-GUIDE.md](GOVERNANCE-GUIDE.md) §12.

## Getting Started

1. **Copy these files** into your project's `governance/` directory
2. **Reference from your CLAUDE.md** (or equivalent agent instructions):
   ```markdown
   ## Governance
   This project follows the agentflow loop.
   See governance/CLAUDE-LOOP.md for execution model.
   ```
3. **Create your pipeline files:**
   - `INBOX.md` — raw input dump
   - `BACKLOG.md` — with `## Ideation`, `## Refining`, `## Ready` sections
   - `TODO-Today.md` — with `## Queue` section
   - `DONE-Today.md` — completion log
   - `.autopilot` — semaphore file (write `run` or `pause`)

4. **Adapt to your agent:** The loop is agent-agnostic. Replace skill names with your agent's equivalents, or use them as-is with Claude Code.

## Design Principles

- **Queue-first:** Never implement during triage. Write the queue item first, then execute.
- **Semaphore-controlled:** Agent checks run/pause before every task, not just at session start.
- **Evidence-based completion:** No task is "done" without verification evidence (test output, screenshots).
- **Learnings are part of the fix:** Every bug fix updates the anti-pattern catalog. The fix is incomplete without documentation.
- **Continuous improvement:** Every 10 completed stories triggers a retrospective.

---

## Origin Story

agentflow started as a simple TODO list and a CLAUDE.md file in a solo developer's side project — an SVG asset generation platform built with FastAPI and Claude Code.

### The Humble Beginning

**Phase 0 — The "just ship it" era.**
No process. Prompt Claude, get code, paste it, hope it works. Context lost between sessions. Same bugs reintroduced. Same anti-patterns rediscovered. The agent was powerful but amnesiac.

**Phase 1 — The checklist.**
A `TODO-Today.md` file. A simple `DONE-Today.md` to track what shipped. A `CLAUDE.md` with rules like "don't use bare except" and "always run tests before commit." Better, but still reactive — rules were added after each painful bug, not before.

**Phase 2 — The loop.**
The realization that autonomous agents need _structure_, not just instructions. The inner loop emerged: pick task → implement → test → commit → next. Then the semaphore (`.autopilot` file) — a kill switch for when the agent goes off track. Then the cleanup sub-loop — quality gates that halt execution on medium+ severity findings.

**Phase 3 — The pipeline.**
Work items need to mature before implementation. INBOX for raw dumps. BACKLOG with Ideation → Refining → Ready stages. Definition of Ready (DOR) as an entry gate. Definition of Done (DOD) as an exit gate. Graduation commands to move items through the pipeline with quality checks at each transition.

**Phase 4 — The skills.**
Repeatable prompt modules that plug into specific loop stages. Test-driven development at step 6. Verification at step 7. Code review at step 8. Each skill encapsulates expertise that would otherwise be lost between sessions. 60+ skills organized into dev loop, support processes, and an on-demand toolbox.

**Phase 5 — The governance layer.**
One project became many. The loop needed to be consistent across all of them. A central Governance repo with synced copies. An orchestrator for multi-agent routing. Known patterns that travel between projects. Retrospectives every 10 stories that feed improvements back into the system.

### What We Learned

1. **Agents don't need freedom — they need guardrails.** The more structure you give an autonomous agent, the better it performs. Not because it's dumb, but because structure prevents drift.

2. **Memory is the hardest problem.** Context windows compress, sessions end, conversations get lost. Every mechanism in agentflow exists because forgetting was more expensive than remembering.

3. **Quality gates must be automatic.** If a human has to remember to run tests, tests won't get run. If the loop runs tests automatically and halts on failure, quality is guaranteed.

4. **Process scales, heroics don't.** A single developer with agentflow can sustain output that would normally require a small team — but only because the process catches what the human would miss.

---

## Expansion: Multi-Agent Communication

agentflow was designed for a single agent (Claude Code), but the architecture supports multi-agent orchestration through a message bus layer.

### The Problem

Modern AI teams don't use just one model. Claude excels at implementation. Gemini has a million-token context window for research. ChatGPT writes compelling copy. Grok has real-time information. Each agent has strengths, but none can do everything.

### The Architecture

```
                    ┌─────────────────────┐
                    │    Orchestrator      │  Routes tasks to best agent
                    │  (ORCHESTRATOR.md)   │  based on capability scoring
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Message Bus       │  Agent-to-agent communication
                    │  (any transport)     │  SQLite, HTTP, pub/sub, etc.
                    └──┬──────┬──────┬────┘
                       │      │      │
                  ┌────▼─┐ ┌─▼────┐ ┌▼─────┐
                  │Claude│ │Gemini│ │ChatGPT│
                  │ACTIVE│ │ STUB │ │ STUB  │
                  └──────┘ └──────┘ └───────┘
```

### How It Works

1. **Capability scoring:** Each agent has a manifest ([AGENT_CAPABILITIES.md](AGENT_CAPABILITIES.md)) listing strengths, context access, and constraints. The orchestrator scores each agent against the task keywords.

2. **Routing confidence:** Score > 0.7 = auto-route. Score 0.3-0.7 = suggest with human confirmation. Score < 0.3 = unroutable.

3. **Message bus transport:** Any communication layer works — HTTP API, SQLite-based messaging, Google Sheets bridge, or manual paste. The framework is transport-agnostic.

4. **Single-agent mode:** When only one agent is active (the common case), the orchestrator still adds value through stall detection, dependency cascading, and context preloading. No message bus needed.

### Building Your Own Multi-Agent Setup

To add a new agent:

1. Add an entry to `AGENT_CAPABILITIES.md` with status `stub`
2. Set up transport (message bus, HTTP, or manual relay)
3. Run the activation checklist:
   - Verify transport (can the agent receive messages?)
   - Complete first contact (round-trip message)
   - Send bootstrap context (project overview, conventions)
   - Route one low-risk test task
   - Set routing weight based on observed capability
4. Update status from `stub` to `active`

The orchestrator handles routing automatically once the agent is registered and weighted.

---

## Companion Tools

agentflow is a set of markdown files and conventions. But two companion tools were built alongside it to make the loop tangible — a GUI remote control and a web-based pipeline dashboard. Both are open-source and can be adapted to any agentflow project.

### Remote Control — Loop GUI Dashboard

A native desktop GUI (WinForms/PowerShell) that exposes all 30+ loop functions without touching the terminal. Designed for the operator who wants to see what the agent is doing and intervene when needed.

**Dual-mode UI:**

```
COMPACT MODE (~420×120 px, always-on-top)
+================================================================+
|  [>] [||] [U] [AB] | Status | [BLD] [RST] [GL] [D] [X]       |
+----------------------------------------------------------------+
|  > [4] US-019 Recipe validation              project v2.1      |
+----------------------------------------------------------------+
|  Action: Medium finding in auth.py — review required           |
+================================================================+

DASHBOARD MODE (~900×700 px)
+============================================================+
|  RC-1.0  [Project v]  INBOX(3) BACKLOG(7) QUEUE(4)          |
+------------------------------------------------------------+
|  PIPELINE (Kanban)                                           |
|  +--------+ +--------+ +--------+ +--------+                |
|  |Inbox(3)| |Ideate 2| |Refine 3| |Ready(2)|                |
+------------------------------------------------------------+
|  QUEUE (TODO-Today)                [Greenlight] [Run]        |
|  > Current: US-019 Recipe valid.    [2/7 done]               |
+------------------------------------------------------------+
|  AUTOPILOT      | SERVER       | SESSION                     |
|  [>Resume] [||] | :9001 UP     | Memory: 2h ago              |
|  [Unattend 2h]  | v2.1.0       | Retro: [===7/10==]          |
+============================================================+
```

**Key capabilities:**
- **Autopilot control** — Resume / Pause / Unattended timer (2h/4h/6h/8h)
- **Queue view** — Live TODO-Today parsing, current task display, progress bar
- **Server health** — TCP port check, build log streaming, git status (M/U counts)
- **Multi-project switching** — Dropdown lists all governed projects, auto-detects active one
- **Action bridge** — GUI writes commands to `.claude-action`, agent reads and executes. One-at-a-time queueing with stale detection (5 min timeout)
- **Hotkeys** — `Win+Shift+T` toggle visibility, `Win+Shift+R` resume, `Win+Shift+P` pause, `Win+Shift+G` greenlight

**Architecture — Single-Writer Rule:**

The critical constraint: the agent is the only writer to pipeline markdown files (BACKLOG, TODO-Today, DONE-Today). The GUI communicates through a `.claude-action` file — a command channel that the agent polls and executes. This eliminates concurrent write hazards entirely.

```
┌──────────┐     .claude-action      ┌──────────┐
│   GUI    │ ──── writes command ───→ │  Agent   │
│ (Remote  │                          │ (Claude  │
│  Control)│ ←── reads  result ────── │  Code)   │
└──────────┘     .claude-action-log   └──────────┘
                                           │
                                    writes to .md files
                                    (BACKLOG, TODO-Today, etc.)
```

**Tech stack:** PowerShell 5.1, WinForms (.NET Framework 4.7.2), no external dependencies. Runs on any Windows 10+ machine.

**Phases:**
1. Core Shell (compact mode, autopilot, queue, health) — **implemented**
2. Pipeline Visibility (Kanban view, INBOX triage, staleness scanner)
3. Outer Loop Controls (BACKLOG graduation, planning rounds, greenlight streaming)
4. PO Intelligence (dependency trees, risk register, retro counter, BV scoring)

---

### Pipeline Dashboard — Web-Based Kanban

A lightweight web dashboard that visualizes the entire agentflow pipeline as a 6-column Kanban board. Think "Jira for markdown files" — but local, instant, and zero-config.

```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline Dashboard          [Project Filter v]              │
├─────────┬─────────┬─────────┬─────────┬─────────┬──────────┤
│ INBOX   │IDEATION │REFINING │ READY   │ QUEUE   │  DONE    │
│         │         │         │         │         │          │
│ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │ ┌─────┐ │ ┌──────┐│
│ │ Raw │ │ │Idea │ │ │Spec │ │ │#1   │ │ │[x]  │ │ │14:32 ││
│ │ bug │ │ │     │ │ │in   │ │ │Ready│ │ │Done │ │ │Done  ││
│ │     │ │ │     │ │ │prog │ │ │     │ │ │     │ │ │      ││
│ │[/sc]│ │ │[/sc]│ │ │[/sc]│ │ │[/sc]│ │ │[/sc]│ │ │      ││
│ └─────┘ │ └─────┘ │ └─────┘ │ └─────┘ │ └─────┘ │ └──────┘│
│ ┌─────┐ │         │         │ ┌─────┐ │ ┌─────┐ │          │
│ │Link │ │         │         │ │#2   │ │ │[ ]  │ │          │
│ │     │ │         │         │ │Ready│ │ │Next │ │          │
│ └─────┘ │         │         │ └─────┘ │ └─────┘ │          │
├─────────┴─────────┴─────────┴─────────┴─────────┴──────────┤
│  Promote →                                                   │
└─────────────────────────────────────────────────────────────┘
```

**Key features:**
- **6-column Kanban** — maps directly to pipeline stages: Inbox → Ideation → Refining → Ready → Queue → Done
- **Auto-discovery** — scans a root directory for all projects containing pipeline markdown files
- **Project filter** — scope the board to a single project or view all at once
- **Epic accordion** — items grouped by epic prefix, collapse/expand state persisted in localStorage
- **Promote button** — one-click promotion to the next pipeline stage (writes directly to `.md` files)
- **Lane-aware command shortcuts** — each card shows the appropriate `/sc:` command for its stage, copies to clipboard on click
- **Card details** — expand any card to see the full item body (spec links, AC, context)

**Architecture:**
- Pure Python backend (no framework dependency beyond stdlib, or lightweight Flask)
- Vanilla HTML/CSS/JS frontend — no build system, no React/Vue
- No database — reads/writes directly to `.md` files via regex + file I/O
- No authentication — designed for single-user local environments

**How it integrates with agentflow:**

| Pipeline File | Dashboard Column | Interaction |
|---------------|-----------------|-------------|
| `INBOX.md` | Inbox | View + promote to BACKLOG |
| `BACKLOG.md #Ideation` | Ideation | View + promote to Refining |
| `BACKLOG.md #Refining` | Refining | View + promote to Ready |
| `BACKLOG.md #Ready` | Ready | View + promote to Queue via `/workflow` |
| `TODO-Today.md` | Queue | View current execution state |
| `DONE-Today.md` | Done | View completed items with timestamps |

**Start:**
```bash
python dashboard.py [--port 8500] [--root /path/to/projects]
# Open http://localhost:8500
```

---

### Choosing Between Them

| Feature | Remote Control | Pipeline Dashboard |
|---------|---------------|-------------------|
| **Platform** | Windows (WinForms) | Any (web browser) |
| **Best for** | Real-time operator control | Pipeline visibility + planning |
| **Autopilot control** | Yes (resume/pause/unattended) | No |
| **Server health** | Yes (TCP check, build log) | No |
| **Kanban view** | Phase 2+ | Yes (6 columns) |
| **Multi-project** | Yes (dropdown) | Yes (auto-discover) |
| **Promote items** | Via action bridge (agent writes) | Direct file write |
| **Always-on-top** | Yes (compact mode) | No |
| **Zero dependencies** | PowerShell 5.1 + .NET | Python + browser |

Use **both** together: Remote Control for moment-to-moment autopilot management, Pipeline Dashboard for planning rounds and backlog grooming.

---

## License

MIT — see [LICENSE](LICENSE).
