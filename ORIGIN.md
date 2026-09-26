# The Origin of Shepherd

## Genesis

Shepherd didn't start as a product. It started as frustration.

---

### Phase 0 — The YOLO Era

A solo developer. A side project — a local-first content generation platform for Etsy sellers, built with FastAPI and Claude Code. The workflow was simple: prompt Claude, get code, paste it, hope it works.

It worked. Until it didn't.

Context vanished between sessions. The same bugs reappeared. The same anti-patterns — bare `except Exception`, unguarded `setattr()` loops, CWD-relative paths — kept creeping back in. The agent was powerful but amnesiac. Every session started from zero.

**The lesson:** AI agents without memory are Sisyphus with a keyboard.

### Phase 1 — The Checklist

The first attempt at structure: a `TODO-Today.md` file and a `CLAUDE.md` with rules like "don't use bare except" and "always run tests before commit."

Better. But reactive — every rule was a scar from a previous bug. The rules grew, but they were just text. Nothing enforced them. The agent would read the rules, acknowledge them, and then violate them three prompts later because they'd scrolled out of context.

**The lesson:** Instructions decay. Enforcement is the only thing that persists.

### Phase 2 — The Loop

The realization that autonomous agents need _structure_, not just instructions.

The inner loop emerged: pick task → implement → test → commit → next. Then the semaphore — a `.autopilot` file, a kill switch for when the agent goes off track. Write `pause`, the agent stops. Write `run`, it continues.

Then the cleanup sub-loop — quality gates that halt execution on medium+ severity findings. The agent could fix small issues on its own, but anything serious required a human to look at it before proceeding.

For the first time, the agent could run unattended for hours without producing garbage.

**The lesson:** Autonomy without guardrails is just faster chaos.

### Phase 3 — The Pipeline

Work items needed to mature before implementation. Raw ideas dumped into `INBOX.md` were too vague to execute. Features needed requirements. Requirements needed specs. Specs needed review.

The Scrumban pipeline emerged:

```
INBOX → BACKLOG (Ideation → Refining → Ready) → TODO-Today → DONE-Today
```

Definition of Ready (DOR) as an entry gate. Definition of Done (DOD) as an exit gate. Graduation commands to move items through the pipeline with quality checks at each transition.

Items that weren't ready couldn't enter the queue. Items that weren't done couldn't be committed. The pipeline enforced what willpower couldn't.

**The lesson:** Process beats heroics. Every time.

### Phase 4 — The Skills

Repeatable prompt modules emerged for specific loop stages. Test-driven development at step 6. Verification at step 7. Code review at step 8. Each skill encapsulated expertise that would otherwise be lost between sessions.

But skills came from everywhere — some homegrown, some from open-source projects:

- **Superpowers** brought disciplined execution skills: brainstorming with hard gates, TDD cycles, verification-before-completion, systematic debugging
- **SuperClaude** brought analysis and expert panels: spec-panel with 10 simulated engineering experts, business-panel with 9 strategy thinkers, deep web research, code analysis with structured finding taxonomies
- **Ralph Loop** (named after Ralph Wiggum's "I'm in danger" meme) brought persistence: a stop hook that prevented Claude from exiting, forcing it to keep iterating on the same task until genuinely complete

Three systems. Three installs. Three namespaces. Three mental models.

**The lesson:** The best tools are useless if you can't find them.

### Phase 5 — The Name

The question became obvious: why three mental models? Ralph provides persistence, Superpowers provides execution discipline, SuperClaude provides analysis depth, AgentFlow provides governance — layers, not competitors. They were **not merged into one code base**: Superpowers and SuperClaude remain separate, live skill trees installed alongside this repo, and Ralph's stop hook is a plugin. What this repo did was give the governance layer one namespace (`/sh:`, 47 commands as of 2026-09) and one doctrine (`DOCTRINE.md`), and drop its own duplicates of what the other trees already did. The result needed a name that captured guiding a flock of tasks through a pipeline, protecting them from wolves (bugs), and getting them to completion.

**Shepherd.**

---

## What We Learned

1. **Agents don't need freedom — they need guardrails.** The more structure you give an autonomous agent, the better it performs. Not because it's dumb, but because structure prevents drift.

2. **Memory is the hardest problem.** Context windows compress, sessions end, conversations get lost. Every mechanism in Shepherd exists because forgetting was more expensive than remembering.

3. **Quality gates must be automatic.** If a human has to remember to run tests, tests won't get run. If the loop runs tests automatically and halts on failure, quality is guaranteed.

4. **Process scales, heroics don't.** A single developer with Shepherd can sustain output that would normally require a small team — but only because the process catches what the human would miss.

5. **The best system is the one you actually use.** Three excellent tools that require three mental models lose to one good tool that requires one. Unification isn't about features — it's about cognitive load.

6. **Skills are the unit of reuse.** Not functions, not libraries — prompt modules that encapsulate expertise for a specific task. A TDD skill is worth more than a TDD library because it brings the discipline, not just the tools.

7. **Expert panels are surprisingly effective.** Simulating 10 engineering experts reviewing a spec catches things that a single-voice review misses. Not because the simulation is perfect, but because each "expert" applies a different lens. Karl Wiegers asks "is this testable?" while Michael Nygard asks "what happens when this fails?" — different questions, different blindspots covered.

---

## The Name

**Shepherd** — because the job isn't to do the work. The job is to guide the work through a structured process, protect it from quality wolves, and deliver it safely to completion.

The sheep are tasks. The pasture is the pipeline. The shepherd is the governance framework that keeps everything moving in the right direction.

`/sh:` — short, memorable, and unlikely to conflict with anything.

---

## Timeline

| Date | Event |
|------|-------|
| 2024 | Phase 0-1: Solo project, first CLAUDE.md, first TODO-Today |
| 2025 Q1 | Phase 2: Inner loop, semaphore, cleanup sub-loop |
| 2025 Q2 | Phase 3: Full Scrumban pipeline, DOR/DOD gates |
| 2025 Q3 | Phase 4: Skill integration, Superpowers + SuperClaude adoption |
| 2025 Q4 | AgentFlow extracted as standalone repo |
| 2026 Q1 | Phase 5: One namespace and one doctrine — Shepherd v2.0 |

---

## Credits

Shepherd stands on the shoulders of:

- **[Superpowers](https://github.com/anthropics/claude-plugins-official)** — Disciplined execution skills for Claude Code
- **[SuperClaude](https://github.com/SuperClaude-Org/SuperClaude_Framework)** — Analysis skills and expert panel system
- **[Ralph Loop](https://github.com/anthropics/claude-plugins-official)** — The Ralph Wiggum persistence technique
- **The SVG-PAINT project** — The original side project where all of this was born, battle-tested across 500+ user stories and 19 quality audit passes
