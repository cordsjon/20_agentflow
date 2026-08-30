---
name: sh-osm-panel
description: "Multi-expert OSM/geodata architecture review — tag semantics, harvest pipelines, admin boundaries, corridors and routing — for European mapping projects"
---

# /sh:osm-panel — OSM Europe Architecture Review Panel

## Usage

```
/sh:osm-panel [specification_content|@file] [--mode discussion|critique|socratic] [--focus tagging|pipeline|boundaries|querying|routing] [--experts "name1,name2"] [--iterations N] [--verbose]
```

## Verbosity

- **Silent (default)**: No expert deliberations. Output only: score table, FIPD-classified findings list, and auto-fix diff. Saves ~60-80% output tokens.
- **Verbose (`--verbose`)**: Full expert deliberations, cross-expert dialogue, reasoning traces, and detailed per-expert analysis before scores and findings.

Silent mode still performs full internal analysis — quality is preserved, only the output is compressed.

## Behavioral Flow

0. **Load Protocol**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/PANEL_PROTOCOL.md` and apply it IN FULL — every section it defines, including any added after this line was written. This is load-bearing — findings that are not grounded per the protocol, or that do not survive its refute stage, MUST NOT be reported.
1. **Load Panel Config**: Read `/Users/jcords-macmini/projects/20_agentflow/experts/panels/osm-panel.yaml` for panel definition, focus areas, auto-select rules, pre-scoring checks, and scoring config (absolute path — relative paths fail when CWD is outside agentflow)
2. **Load Experts**: Read expert files from `/Users/jcords-macmini/projects/20_agentflow/experts/individuals/` for each selected expert
3. **Auto-Select Experts**: Scan the specification content against panel YAML `auto-select` keywords — add matching experts up to `max-experts: 7` cap
4. **Pre-Scoring Checks (deterministic — do NOT delegate to LLM personas):** run ALL checks the panel YAML defines whose `when` condition matches — table-reconciliation, **tag-evidence** (every named OSM tag needs wiki status + measured count), **boundary-crs** (every geometry claim needs CRS/unit + per-country admin_level), and operator-surface-completeness. Findings from these checks are reported BEFORE expert deliberation, at the severity the YAML assigns. These steps are mechanical, executed by the panel runner, not by an expert voice.
5. **Analyze**: Parse specification content, identify components, gaps, and quality issues
6. **Assemble Panel**: Select experts based on `--focus` area or use `default-experts` from panel YAML. `--experts` override replaces defaults entirely
7. **Conduct Review**: Run analysis in the selected mode using each expert's distinct methodology. Experts may (read-only) consult the project corpus (sqlite), taginfo, and the OSM wiki to ground findings — a tag-semantics claim without a wiki or corpus citation dies in the refute stage.
8. **Score**: Rate specification across the 6 dimensions defined in the panel YAML (0-10 each), compute overall score. Dimensions marked N/A by their own definition are excluded from the average, noted in output.
9. **Gate Check**: Overall score must be >= 7.0 to pass. Below threshold = specification needs rework

## Panel Experts

Defined in `/Users/jcords-macmini/projects/20_agentflow/experts/individuals/`; personas are syntheses of each person's public work and stated positions, not the people themselves:

- **Jochen Topf** (lead, tagging) — taginfo/osmium author, "OpenStreetMap Data" co-author. Tag semantics, wiki-status drift, vocabulary gates.
- **Frederik Ramm** (lead, pipeline) — Geofabrik co-founder. Extracts, harvest pipelines, ODbL pragmatics.
- **Sarah Hoffmann** (lead, boundaries) — Nominatim maintainer. Admin boundaries, per-country admin_level, geocoding.
- **Roland Olbricht** (lead, querying) — Overpass API author. Query design, rate limits, API etiquette.
- **Dennis Luxen** (routing, auto-selected) — OSRM author. Corridors, ferry legs, routing profiles.

## Analysis Modes

### Discussion Mode (`--mode discussion`)
Collaborative improvement through expert dialogue. Experts build upon each other's insights sequentially. Cross-expert validation and consensus building around critical improvements.

### Critique Mode (`--mode critique`)
Systematic review with severity-classified issues (CRITICAL / MAJOR / MINOR). Each finding includes: expert attribution, specific recommendation, priority ranking, and quality impact estimate.

### Socratic Mode (`--mode socratic`)
Learning-focused questioning to deepen understanding. Experts pose foundational questions about purpose, data provenance, assumptions, and alternatives. No direct answers — forces the author to think critically.

## Focus Areas

- **tagging**: Tag semantics, wiki-status drift, vocabulary gates, taginfo evidence. Lead: Jochen Topf
- **pipeline**: Extract selection, harvest/derive/reclassify ordering, corpus freshness, ODbL. Lead: Frederik Ramm
- **boundaries**: admin_level semantics per country, CRS choices, polygon vs point, geocoding. Lead: Sarah Hoffmann
- **querying**: Overpass query design, rate limits, taginfo vs corpus counts. Lead: Roland Olbricht
- **routing**: Route corridors, ferry legs, profile semantics, network topology. Lead: Dennis Luxen

## Scoring Gate

6 dimensions, each scored 0-10 (definitions in the panel YAML):

| Dimension            | Description |
|----------------------|-------------|
| Clarity              | Language precision and understandability |
| Tag-grounding        | Every named OSM tag evidenced: wiki status + measured corpus/taginfo count. N/A when no tags named. |
| Pipeline-integrity   | harvest → derive → classify → join → bundle ordering respected; backfill named for every added derived column; extract provenance + ODbL addressed. |
| Boundary-correctness | Explicit CRS, per-country admin_level verification, spatial-partition edge effects named and mitigated or measured. |
| Consistency          | Internal coherence and contradiction detection |
| Operator-surface     | Every introduced capability reachable by human operator (named CLI command + menu entry where applicable) and by agents (a2a entry as AC when applicable). N/A when no operator-facing surface. |

**Pass threshold: overall score >= 7.0**

## Grounding Sources (fetched 2026-08-30 — re-verify if older than ~6 months)

Fetched live 2026-08-30 (8/8 sources). Facts below are quotable; anything marked *verify-at-review* must be re-fetched before a reviewer cites it.

1. **Map Features** (wiki/Map_features): ~28 primary keys form the top-level taxonomy (Amenity, Boundary, Highway, Landuse, Leisure, Natural, Route, Shop, Tourism, …). Free-tagging doctrine: the documented core is not an exhaustive schema.
2. **admin_level** (wiki/Tag:boundary=administrative): **country-specific, never universal.** DE: 2=country, 4=Bundesland, 5=Regierungsbezirk, 6=Landkreis/Kreis/kreisfreie Stadt, 8=Stadt/Gemeinde — corroborated in-project by `city.py`'s measured 97.3% `admin_level=8`↔`addr:city` agreement. AT (Bundesland→Bezirk→Gemeinde), BE (Region→Province→Arrondissement→Municipality), DK (Regioner→Kommune) unit *orders* fetched; their exact level numbers plus all rows for **NL, CH, SE, LU resisted extraction (summarizer truncation, 2 independent attempts) — verify-at-review directly from the wiki table; recalled admin levels are banned as evidence.**
3. **Overpass API** (wiki/Overpass_API): public-instance ceiling ~10,000 queries / 1 GB per day; **divide by 100 for automated use** (~100 queries / 10 MB per day). Unique User-Agent required; no parallel scripts; 30 s pause on 429/406; commercial load must self-host; the wiki itself calls the public server "nowadays overloaded". In-project measured trap: `/api/status` can report free slots while the next query returns `rate_limited` — probe with a real tiny query.
4. **Geofabrik Europe** (download.geofabrik.de/europe.html): `denmark-latest.osm.pbf` 470 MB and `sweden-latest.osm.pbf` 777 MB — both **single country-level extracts, no sub-region splits offered.**
5. **route=ferry** (wiki/Tag:route=ferry): map simple crossings as a **single way** terminal-to-terminal (`route=ferry` + `name`); route *relations* exist but "most routing clients and renderers do not currently support ferry relations" — tags go on ways regardless. `duration=HH:MM:SS` highly recommended; terminals are `amenity=ferry_terminal`; tourist rides are `attraction=boat_ride`, never `route=ferry`.
6. **ODbL attribution** (osmfoundation.org Attribution_Guidelines): credit "© OpenStreetMap contributors" linking to openstreetmap.org/copyright, presented to anyone exposed to the map (corner or collapsible splash with persistent info access); **derived databases embed the ODbL notice inside the database/README**; static images under 100 features or 10,000 m² are exempt.
7. **taginfo** (taginfo.openstreetmap.org): planet-wide key/value usage counts, refreshed daily, documented API — the canonical source for "how often is this tag actually used"; regional instances exist.
8. **Free tagging + lifecycle** (wiki/Any_tags_you_like, wiki/Lifecycle_prefix): "documented" is a wiki/community status, not a validity gate — undocumented tags are valid data whose *meaning* is unevidenced. Lifecycle prefixes (`disused:`, `abandoned:`, `demolished:`/`razed:`, `construction:`, `proposed:`, `was:`) rename the key — a harvester matching `shop=*` must not match `disused:shop=*`, and a vocabulary that ignores prefixes silently resurrects dead POIs.

## Output

Specification review document containing:
- Multi-expert analysis with distinct perspectives
- Per-dimension scores and overall quality score
- Pass/fail gate result
- Critical issues with severity and priority
- Consensus points and disagreements
- Priority-ranked improvement recommendations

**AUTO-FIX, NOT SYNTHESIS-ONLY** — this panel produces the analysis AND then applies fixes for **every** finding (high, medium, and low) automatically, per `00_Governance/CLAUDE.md §8 Panel Auto-Fix Policy`. It never asks which findings to apply and never presents a menu: it fixes everything, then reports what changed. A below-gate score means fix the findings and re-run, not stop and ask.

## Auto-Fix Policy
Fix ALL findings automatically — high, medium, and low severity. Do not ask which findings to fix. Do not present a menu or an a/b/c choice. Fix everything, then report what was changed. This overrides any softer "synthesis only" framing. Per `00_Governance/CLAUDE.md §8`.

## Output Contract (machine-readable verdict)

The quality gate (`quality_gate.run_stage3_panel`) consumes this panel via
`claude -p` and reads the **score from stdout, not the exit code**. Therefore
the **final line** of your output MUST be exactly one of:

```
PANEL-VERDICT: <overall_score>
PANEL-VERDICT: FAIL: <machine_reason>
```

- `<overall_score>` is the numeric overall score (0–10, one decimal — e.g. `8.3`).
  The gate applies the pass threshold (default 7.0); do NOT pre-apply it — just
  report the score you computed.
- Use the `FAIL: <machine_reason>` form only when no score could be produced
  (structural failure) — snake_case naming the first blocker (e.g.
  `no_content`, `panel_config_missing`, `experts_unavailable`).
- Emit the line literally, on its own line, as the last meaningful output.
