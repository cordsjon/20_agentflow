<!-- AI-maintained, append-only -->

## R1 — Show HN: Moadim.io – A scheduler for agents — reject

**Artifact:** Show HN: Moadim.io – A scheduler for agents — https://news.ycombinator.com/item?id=49571537
**Question:** does it enhance 20_agentflow?
**What it does:** [inference] Moadim is an MIT Rust daemon that runs Claude/Codex agents on schedules in tmux, exposed via REST and MCP. It overlaps 20_agentflow's purpose, adds a new always-on Rust/tmux runtime outside the Python/FastAPI stack, and its loop-termination and token-cost controls are unclear.
**Evidence:** stored snapshot SHA-256 ab8d0360abd9271f9b40f61bcdcfdb4bcd17db21664f601ce86e832c11ac817d; runtime capability [unmeasured].
**Verdict:** reject
**Justification:** [inference] Agent loop scheduling with isolated per-tick workbenches, hung-run watchdog and session reaping is not fully covered: current runs use cron/manual triggers, and main-7 (ASES CLI) has autopilot scheduling only for its skill registry. However, 20_agentflow is the resolved project for agent orchestration, so scheduled agent runs belong inside it rather than in a parallel Rust daemon. Moadim adds a new language and runtime (cargo, tmux, launchd service) to maintain alongside the Python/FastAPI/SQLite stack. Per the source and HN comments, how a loop decides it is done and how token spend is bounded are not documented, which is a cost risk for unattended runs. The adopt gate rated it park. The useful patterns (fresh workbench per tick, watchdog timeout, session reaping, routine-as-MCP-tool, iCal feed of schedules) can be borrowed as design references for 20_agentflow without adopting the daemon.
**Cost if adopted:** n/a
**Revisit-if:** —
**Ref:** gap:8 rev:f375c01f03b34008adcd49bb934dbb00
source: gap 8
drafted-by: gap loop (claude-opus-5-5, from untrusted evidence)
