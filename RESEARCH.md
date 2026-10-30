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

## R2 — job-search-aiagent: Open-source TypeScript multi-agent engine that harvests ATS boards, scores jobs, and tailors CVs without hallucinating — reject

**Artifact:** job-search-aiagent: Open-source TypeScript multi-agent engine that harvests ATS boards, scores jobs, and tailors CVs without hallucinating — https://www.reddit.com/r/coolgithubprojects/comments/1wf3g2l/jobsearchaiagent_opensource_typescript_multiagent/
**Question:** does it enhance 20_agentflow?
**What it does:** [inference] Reject: source body is empty (only 'Reddit'), so no capability can be verified. Job-search ATS harvesting/CV tailoring has no evident need in 20_agentflow or any listed profile, and TS stack mismatches the Python/FastAPI core.
**Evidence:** stored snapshot SHA-256 eb0050f72303bcdbbdc071e2a3bf810c903be8d05cdf09f7c3106f2b6f9878bf; runtime capability [unmeasured].
**Verdict:** reject
**Justification:** [inference] No confirmed gap. Registry match label is 'augment' but matches are incidental term hits (search, open, engine, agent) on cli-19, collect_p0_references, decisions_probe_queue, main-3 and nkl-review, none of which concern job search. 20_agentflow orchestration needs are not evidenced by a domain-specific job-hunting pipeline. Existing agent/CLI capabilities (main-3 ingest engine, nkl-review record checks) already cover generic multi-agent ingest and review patterns; adopting a TypeScript engine adds a foreign runtime and maintenance cost with no verified benefit. Adopt gate also parked for insufficient evidence.
**Cost if adopted:** n/a
**Revisit-if:** —
**Ref:** gap:26 rev:6576b4bdfffa40329721f0fa39eb8e43
source: gap 26
drafted-by: gap loop (claude-opus-5-5, from untrusted evidence)

## R3 — Show HN: Viaduct – C4 models that coding agents can read and update — reject

**Artifact:** Show HN: Viaduct – C4 models that coding agents can read and update — https://news.ycombinator.com/item?id=49790729
**Question:** does it enhance 20_agentflow?
**What it does:** [inference] Viaduct is a closed-source C4 modeling tool with an MCP server. The browser version requires an account and hosted EU storage; local-first use needs the paid, unsigned desktop app. graphify and mp-codebase-design already cover agent-readable architecture context.
**Evidence:** stored snapshot SHA-256 66d7707969220c2e46ec4dac747f349f13ac32e8a7dbf50cb16a462a36aa56f2; runtime capability [unmeasured].
**Verdict:** reject
**Justification:** [inference] Agents in 20_agentflow could use a shared, versioned architecture model (C4 context/container/component levels, OpenAPI contracts per container) that they read and update over MCP. graphify already covers persistent codebase/architecture graph queries for agents, and mp-domain-modeling and mp-codebase-design cover model vocabulary and design. The only uncovered piece is a C4-structured editor with change sets. Viaduct does not fit: it is closed-source. The free tier is hosted SaaS that requires sign-up and stores models on its servers. The local-first path is a €10/month desktop app with unsigned builds and licence checks. No self-host or source licence is shown, and there is no fit with the Python/FastAPI/SQLModel/SQLite stack. The JSON and OpenAPI export is unverified. Licensing cost, vendor lock-in and supply-chain risk outweigh this narrow gap; extending graphify with C4-level views is the cheaper route.
**Cost if adopted:** n/a
**Revisit-if:** —
**Ref:** gap:47 rev:bc9ef30cb090453a92ea04da83d2ad54
source: gap 47
drafted-by: gap loop (claude-opus-5-5, from untrusted evidence)
