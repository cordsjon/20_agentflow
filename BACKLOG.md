# BACKLOG — Cross-Project

> **Central priority authority.** Items here span projects or are project-agnostic.
> Project-scoped items stay in their own BACKLOG.md.
>
> Items flow: **Ideation -> Refining -> Ready -> project TODO-Today.md (execution)**

---

## Ideation

- **Governance Repo: Tether-as-PO-Agent** — Evolve governance from passive files to an active agent. The governance repo becomes a "PO agent" that sends prioritized work to project-scoped agents (Claude, Gemini, ChatGPT) via Tether. Priority changes propagate in real-time. Retro insights flow back via Tether messages. Requires: Tether thread per project, governance CLI that reads BACKLOG priority order and posts to Tether.

- **WinForms UI for Tether** _(project: Tether)_ — Desktop dashboard to see what's sent, what came back, log errors. Visual monitor for the postoffice: message list with status (pending/completed/failed), sender/recipient filters, error log viewer, real-time refresh. Wraps existing HTTP API (localhost:7890) as data source.

- **LLM Scrum Masters** (ideation 2026-03-01) `[process]` — Employ external LLMs (Gemini, ChatGPT) as independent scrum masters / retro facilitators. They receive retro data via Tether, run their own analysis, and post improvement suggestions back. Provides an outside perspective that Claude (as primary executor) may be blind to. Requires: Tether cross-agent messaging, structured retro data format, prompt templates for each LLM.

- **Project Reporting Component** (ideation 2026-03-01) `[governance]` — Governance Hub needs visibility into project activity. Report per project: what changed in what period (commits, stories completed, files touched), what is expected to change (queued items, critical path forecast, upcoming risks). Aggregated cross-project view for the PO. Output destinations: markdown summary in `reports/`, Excel dashboard (existing sync mechanism), Google Sheets (existing Tether bridge). Could feed into planning rounds (§5) as input data.

- **Daily Auto-Commit for Governance** (ideation 2026-03-01) `[infrastructure]` — Scheduled task (Windows Task Scheduler or Startup script) that runs once daily: stages all changed governance files (BACKLOG.md, decision_log.md, MEMORY.md, knowledge/, retros/), commits with message `"daily: governance snapshot YYYY-MM-DD"`, and triggers sync-repos.ps1. Prevents loss of planning work between sessions. Guard: only commits if there are actual changes (no empty commits). Does NOT push to remote — local safety net only. Could extend to all governed project repos with the same pattern.

- **Governance Dashboard — WinForms Widget** (ideation 2026-03-01) `[governance]` `[winforms]` — Purpose-built desktop widget for the PO to monitor and interact with the governance loop. NOT a build pipeline remote control — this is a planning and priority cockpit. See detailed concept below.
  - **Data source:** Reads governance markdown files directly (BACKLOG.md, TODO-Today.md per project, ROADMAP.md, decision_log.md, retros/counter.json, knowledge/_index.md) + git log for activity
  - **Panels:**
    - **Backlog Health** — Ideation/Refining/Ready item counts per project, staleness badges (green/amber/red), date annotations visualized as age bars
    - **Critical Path** — Visual dependency chain, current position indicator, blocked/done status per item, optical barrier between locked and free zones
    - **Risk Heatmap** — L/M/H grid colored by likelihood x impact, items mapped to risk cells, closed risks greyed out
    - **Queue Monitor** — Per-project TODO-Today progress bars (checked/total), current autopilot status (run/pause/stop), last `.claude-action` message as ticker
    - **Planning Triggers** — Live indicator lights: queue near-empty? 5+ Ready idle? path changed? retro due? Each light links to "Start planning round" action
    - **Decision Inbox** — Unresolved INFO/WARN flags from all projects, one-click "Decide" button that logs to decision_log.md
    - **Retro Counter** — Per-project story count toward next retro, progress ring visualization
    - **Domain Knowledge** — Domain spoke list with item counts, staleness, last-updated dates, interlink map
  - **Actions (not read-only):**
    - Re-number Ready items (drag-and-drop priority)
    - Add/remove critical path items
    - Log decisions (clears flags)
    - Trigger planning round / retro
    - Initiate sync (runs sync-repos.ps1)
  - **Tech:** WinForms (.NET), reads .md files via regex parsing, writes back via file I/O, no server needed (local-first). Could optionally poll Tether HTTP API for cross-agent status
  - **Figma:** Wireframe needed — see below

- **AG-BOS: Brand Context Layer + Per-Skill Learnings + Skill Overlap Detection** (ideation 2026-03-15) `[agentflow]` `[skills]` — Extend agentflow with three features inspired by "Agentic OS" pattern (video analysis 2026-03-15). All three integrate into the existing governance loop — no separate system needed.
  - **1. Brand context as first-class folder** — `brand-context/` directory per governed project containing: `voice.md` (tone, vocabulary, do/don't), `icp.md` (ideal customer profile), `positioning.md` (market angle, differentiators), `samples/` (gold-standard outputs), `assets.md` (links, handles, visual refs). Foundation skills interview the user once and generate structured files. All execution skills read from this folder. For SVG-PAINT: Etsy buyer persona, listing voice, competitor positioning.
  - **2. Per-skill learnings** — Each skill gets a `learnings:` section (or companion `learnings.md`) that captures user feedback specific to that skill's output. On skill execution, learnings are read before the skill runs. On session wrap-up, feedback is logged per skill. Complements the global KNOWN_PATTERNS / retro loop with skill-scoped memory. Lifecycle: feedback → learnings entry → skill.md update (if pattern is stable across 3+ entries).
  - **3. Skill overlap detection** — Before creating a new skill, scan all installed skills' front matter (triggers, strengths, tools used). Flag overlaps > 60% keyword match. Suggest merge, dependency, or scope narrowing. Prevents skill sprawl and routing ambiguity in ORCHESTRATOR.md.
  - **Dependencies:** None (pure additive to existing agentflow structure)
  - **Risk:** R-LOW — markdown files only, no runtime code. Main risk is over-engineering the brand context interview.
  - **Next:** Draft user stories for each sub-feature, spec-panel review

- **AG-VPS: Agentflow VPS Integration Layer** (ideation 2026-03-16) `[agentflow]` `[infrastructure]` — Deploy three missing infrastructure components on VPS (`100.91.68.95`) to enable reliable Agent-to-Agent communication and pipeline observability for Agentflow-governed projects.
  - **1. Message Queue (Redis)** — Deploy Redis on VPS as pub/sub backbone for Agent-to-Agent messaging. Replaces current Tether/Google Sheets bridge (2min polling, ngrok dependency) with sub-second delivery. Agents publish task completions, quality gate results, and approval requests to named channels. n8n subscribes for orchestration triggers. Container: `redis:alpine`, port `6379` (Tailscale-only). Persistence: AOF for message durability.
  - **2. Tether Server on VPS** — Deploy Tether SQLite post office (`/tmp/Tether/` source) as Docker container on VPS. Eliminates ngrok tunnel dependency for Gemini-Bridge. Stable endpoint at `tether.getaccess.cloud` (Tailscale-only). Connects to Redis for real-time notifications alongside existing polling. Migration: update `AGENT_CAPABILITIES.md` transport entries from `ngrok` to VPS endpoint.
  - **3. Agentflow Pipeline API** — Lightweight FastAPI service exposing pipeline status as REST endpoints. Reads governance markdown files (BACKLOG.md, TODO-Today.md per project) and exposes: `GET /pipeline/status` (INBOX/BACKLOG/READY/DONE counts), `GET /pipeline/active` (current task + agent), `GET /pipeline/health` (staleness, blocked items, gate failures). Feeds into: Homer dashboard widget, n8n polling workflows, Nanobot status queries via Slack. Container: Python 3.12 + FastAPI + uvicorn, port `8500` (Tailscale-only).
  - **Synergy with existing VPS services:**
    - **n8n** → subscribes to Redis channels, triggers workflows on task completions
    - **Nanobot** → queries Pipeline API for status, sends Slack alerts on gate failures
    - **Dify** → registered as agent in `AGENT_CAPABILITIES.md`, receives tasks via Tether
    - **Uptime Kuma** → monitors all three new services
    - **Ollama** → LLM backend for Dify agent and Nanobot responses
  - **Dependencies:** Docker Compose extension of existing VPS stack, Tailscale for access control
  - **Risk:** R-LOW — all additive, no changes to existing services. Redis is stateless (restart-safe). Tether migration needs rollback plan (keep ngrok as fallback).
  - **Design decisions:**
    - **Tailscale-only** for all three services — no public exposure needed, only Agents and admin tools access these endpoints. Simplifies security (no auth layer needed beyond Tailscale ACLs).
    - **Redis pub/sub over message queue** — Agents publish events, n8n/Nanobot subscribe. Lighter than RabbitMQ and sufficient for expected load (dozens of events/day, not thousands). No consumer groups or dead-letter queues needed at this scale.
    - **Naming convention:** `AG-VPS` prefix groups all three sub-features as one deliverable — they are interdependent (Pipeline API benefits from Redis for real-time push, Tether benefits from Redis for notification alongside polling).
  - **Next:** Architecture spike for Redis pub/sub schema, Tether Dockerfile, Pipeline API endpoint spec

- **AG-DIFY: Dify Integration Layer — Nanobot Workflow Backend & Prototyping Platform** (ideation 2026-03-16) `[agentflow]` `[infrastructure]` `[nanobot]` — Connect Dify (`dify.getaccess.cloud`, 11-container stack on VPS) to Nanobot and Agentflow as a visual workflow backend. Currently three isolated systems: Dify (visual LLM-app builder with RAG/Weaviate), Nanobot (multi-channel assistant via WhatsApp/Slack/Email), Agentflow (Claude Code governance with skills/pipeline/orchestrator). Goal: Dify becomes the visual workflow engine that Nanobot calls via API, and a rapid prototyping platform for new agent ideas before they graduate to Agentflow skills.
  - **1. Nanobot → Dify API Bridge** — Add HTTP adapter in Nanobot that routes qualifying messages to Dify's `/v1/chat-messages` API and returns the response to the user's channel. Nanobot remains the channel gateway (WhatsApp/Slack/Email), Dify handles complex workflow logic. Routing: keyword-based or intent-classified — e.g. messages containing "Rezept", "suche", "fasse zusammen" trigger Dify; general chat stays in Nanobot's native LLM path. Config: Dify API key + app IDs stored in Nanobot's `config.json`. Fallback: if Dify is unreachable (timeout >5s), Nanobot responds with native LLM + "erweiterte Suche nicht verfügbar" notice.
  - **2. Dify Knowledge Base — RAG Pipeline** — Create at least one Knowledge Base in Dify using Weaviate vector store. Candidate document sets: (a) Keto food database docs + recipe PDFs, (b) VPS runbooks + maintenance guides, (c) project documentation (BACKLOG.md, CLAUDE.md files across repos). Nanobot users can ask natural-language questions and get grounded, cited answers. Evaluationskriterium: "Ist die Antwort besser als reines LLM ohne RAG?" — wenn nein nach 2 Wochen, Knowledge Base abschalten.
  - **3. Dify Workflow Templates** — Build 3 starter workflows in Dify's visual editor:
    - **Keto-Rezeptsuche:** User fragt nach Rezept → Dify queries Keto PostgreSQL (`100.91.68.95:5433`) → filtert nach Nährwerten → formatiert Ergebnis
    - **PDF-Zusammenfassung:** User sendet PDF-Link → Dify lädt herunter, chunked, fasst zusammen → Antwort zurück
    - **VPS-Status-Check:** "Wie geht's dem Server?" → Dify ruft Uptime Kuma API auf → formatiert Health-Dashboard als Text
  - **4. Dify als Prototyping-Plattform** — Organisatorisches Pattern: neue Agent-Ideen werden zuerst als Dify-Workflow prototypisiert (visuell, kein Code, 10x schneller). Wenn ein Workflow sich bewährt (>10 Nutzungen/Woche über 2 Wochen), wird er als Agentflow-Skill portiert. Dify = Experiment, Agentflow = Production. Dokumentation: `dify-workflows.md` im Agentflow-Repo mit Status pro Workflow (prototype/graduated/retired).
  - **5. Dify ↔ Agentflow Agent Registration** — Registriere Dify als Agent in `AGENT_CAPABILITIES.md` mit Transport `http`, Endpoint `dify.getaccess.cloud`, Capabilities `[rag, workflow-execution, document-qa]`. Agentflow-Orchestrator kann dann Tasks an Dify routen wenn RAG oder visuelle Workflows gefragt sind. Dify meldet Ergebnisse via Tether oder direkte HTTP-Response zurück.
  - **6. Resource Governance — Keep-or-Kill Gate** — Dify's 11-Container-Stack verbraucht ~1.5-2 GB RAM. Nach 30 Tagen: messe aktive Nutzung (API-Calls/Tag via Dify-Logs). Schwellwert: <5 API-Calls/Tag im Durchschnitt → Entscheidung: Dify abschalten und RAM für n8n/Nanobot/Ollama freigeben. >5 Calls/Tag → weiter betreiben. Dokumentiere Entscheidung in `decision_log.md`.
  - **Synergien mit AG-VPS (wenn implementiert):**
    - Redis pub/sub → Dify publisht Workflow-Completion-Events → n8n/Nanobot subscriben
    - Pipeline API → zeigt Dify-Task-Status neben Agentflow-Tasks
    - Tether auf VPS → stabiler Transport zwischen Dify und anderen Agents (kein ngrok)
  - **Dependencies:** Nanobot config.json Erweiterung, Dify Admin-Setup (LLM-Provider konfigurieren, erste App anlegen)
  - **Risk:** R-LOW — Dify läuft bereits. Nanobot-Adapter ist ein HTTP-Call. Hauptrisiko: Dify wird konfiguriert aber nicht genutzt (→ Keep-or-Kill Gate fängt das ab).
  - **Strategische Hinweise:**
    - **Keep-or-Kill Gate ist das wichtigste Sub-Feature:** Dify's 11-Container-Stack (~1.5-2 GB RAM) ist teuer für einen VPS. Ohne messbaren Nutzen nach 30 Tagen wird es zur Resource-Last. Der Gate verhindert "Install and forget"-Syndrom.
    - **Synergy mit AG-VPS:** Falls AG-VPS (Redis, Tether auf VPS, Pipeline API) zuerst gebaut wird, wird AG-DIFY deutlich mächtiger — Dify kann Events über Redis publishen statt nur auf API-Polls zu warten. Empfehlung: AG-VPS vor AG-DIFY priorisieren.
  - **Next:** Dify Admin-Login, ersten LLM-Provider (Anthropic oder Ollama) konfigurieren, erste Knowledge Base anlegen, Nanobot HTTP-Adapter designen

- **CogniShield — Personal AI Usage Proxy & Cognitive Atrophy Tracker** (ideation 2026-03-08) `[new-product]` — Local proxy that intercepts all personal AI usage (ChatGPT, Claude, Gemini etc.), categorizes delegated tasks (definitions, code, writing, reasoning, research), and prescribes mitigating offline exercises to counteract cognitive atrophy. Not anti-AI — pro-human. Context: MIT EEG study shows 83% recall failure minutes after ChatGPT use, 47% brain connectivity collapse, Wharton confirms "cognitive surrender" across 10K trials. Tech: mitmproxy + SQLite + exercise engine, CLI-first, privacy-first (no cloud). Features: delegation frequency tracking, counter-exercise prescriptions ("10 definitions delegated → look up 10 in a dictionary"), weekly cognitive health dashboard, optional spaced repetition. Separate project. `BV: R=M U=H S=H`
  - Next: market validation, proxy architecture spike, exercise taxonomy design

## Refining

## Ready

- **Code-Level Quality Gate Augmentation** → DONE (2026-03-09) `[governance]` `[quality]` · **S** _(project: Governance)_ — Adopt two high-leverage quality patterns from [ryanthedev/code-foundations](https://github.com/ryanthedev/code-foundations) (MIT, v4.0) to add code-level enforcement where DOR/DOD currently operate only at process level. Business panel (5/5 consensus) + spec-panel (pass 1: 2.9/10 → pass 2: 7.6/10) shaped scope.
  - **Source:** *Code Complete* assessment framework (Fix/Investigate/Plan/Decide taxonomy + uncertainty declaration)
  - **Excluded (business panel unanimous):** 614-check rubric, slash commands, model auto-selection, feature branch enforcement, debugging workflow
  - **Risk:** R-LOW — pure documentation change, no runtime dependency. KNOWN_PATTERNS.md is LLM-read only (no programmatic parser).
  - **Rollback:** If FIPD adoption causes friction after 2 sprints, revert to severity-only and log findings in retro.
  - **User Stories:**
    - **US-QG-01:** As a governance consumer, I want every finding classified by action type (Fix/Investigate/Plan/Decide) so that I know what to do next without re-analyzing the issue.
      - **AC-1:** Given KNOWN_PATTERNS.md, when I read any row, then it has an "Action" column with exactly one value from {Fix, Investigate, Plan, Decide}.
      - **AC-2:** Given a new finding from `/sc:analyze` or quality audit, when the finding is reported, then it is prefixed with its FIPD action type (FIPD *replaces* severity as the primary classifier; severity may remain as metadata but is not the leading label).
      - **AC-3:** Given DOD.md, when I read the quality audit enforcement step, then it references the FIPD taxonomy and links to the definitions.
      - **AC-4:** Given the 10 existing KNOWN_PATTERNS rows, when the migration is complete, then all 10 rows have been backfilled with the correct action classification.
      - **FIPD definitions:**
        - **Fix:** Root cause known, solution clear — implement immediately
        - **Investigate:** Symptom observed, root cause unknown — gather data before acting
        - **Plan:** Issue understood, solution *direction* is known but requires design work — add to backlog
        - **Decide:** Trade-off identified, multiple valid directions exist requiring human judgment — escalate to decision-maker
    - **US-QG-02:** As a reviewer, I want every analysis finding to declare what remains unknown or unverified so that I don't act on false confidence.
      - **AC-1:** Given KNOWN_PATTERNS.md, when I read the patterns list, then there is a meta-pattern row stating: "All review/analysis findings must declare what remains unknown or unverified."
      - **AC-2:** Given a finding output, when the action type is Investigate or Decide, then an `Unknown:` clause is mandatory.
      - **AC-3:** Given a finding output, when the action type is Fix or Plan, then an `Unknown:` clause is recommended but optional.
      - **AC-4:** Given an agent that reads the updated KNOWN_PATTERNS, when it classifies a new hypothetical finding, then it produces output matching the FIPD + uncertainty format. Pass criterion: output contains (a) one FIPD prefix, (b) `Unknown:` clause when action is Investigate or Decide, (c) valid sentence structure. No golden answer match required.
  - **Deliverables:** (1) KNOWN_PATTERNS.md schema change + backfill, (2) uncertainty meta-pattern row, (3) DOD.md finding format reference
  - **Test strategy:** Agent acceptance test — read updated KNOWN_PATTERNS, classify a novel finding, verify FIPD + uncertainty output format
  - **Dependencies:** None
  - **Before/After examples:**
    - KNOWN_PATTERNS row — Before: `| 2 | Catching bare Exception | Catch specific exceptions | SVG-PAINT |` → After: `| 2 | Catching bare Exception | Catch specific exceptions | SVG-PAINT | Fix |`
    - Finding output (Fix) — Before: `⚠️ MEDIUM: Unguarded setattr loop in config_service.py:45` → After: `Fix: Unguarded setattr loop in config_service.py:45 · Unknown: whether current PERSISTED_FIELDS whitelist covers all callers`
    - Finding output (Investigate) — `Investigate: Intermittent 500 on /api/collections endpoint · Unknown: whether caused by connection pool exhaustion or upstream timeout`
  - **Spec-panel:** pass 1: 2.9/10 → pass 2: **7.6/10** (gate passed)

- **PO Capabilities: 8 functions** (refining 2026-03-01) · **L** _(project: Governance)_
  - Spec: [requirements/REQ_PO_CAPABILITIES.md](requirements/REQ_PO_CAPABILITIES.md)
  - 8 capabilities: Prioritization, Critical Path, Dependencies, Backlog Review, Planning Rounds, Risk Calendar, Retros, Release Bundling
  - 15 User Stories (US-P-01/02, US-CP-01/02, US-D-01/02, US-BR-01/02, US-SPR-01/02/03, US-R-01/02, US-RT-01/02, US-RB-01/02)
  - 5 open questions: **all resolved** (see spec §Open Questions — Resolved)
  - Spec-panel pass 1: **6.4/10** → 16 improvements applied (precedence rule, Done def, RACI, flag severity, parsing grammar, validation, integrated example, cross-project deps, 150-line rule, planning interactive gates, retro quality bar)
  - **Missing before Ready:** `/sc:spec-panel` re-score >= 7.0, user sign-off on BACKLOG.md format changes
