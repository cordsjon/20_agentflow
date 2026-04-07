# /pipeline — Idea Pipeline Manager

Pipeline runner for automated idea processing through analysis panels.
Manages ideas through business-panel → spec-panel → design stages.

## Usage

```
/pipeline start "Idea title" --project SVG-PAINT
/pipeline scan                          # intake-scan all INBOXes
/pipeline process <idea-slug>           # run next stage
/pipeline process-all                   # process all ready ideas
/pipeline status                        # show all ideas
/pipeline decisions                     # show pending decisions
/pipeline resolve <idea> <stage> <1-5>  # record decision
/pipeline consult <idea> <stage> [min]  # defer to consultant lane
/pipeline graduate <idea>               # move to BACKLOG Ready
```

## Instructions

You are the pipeline manager. Parse the user's subcommand and execute accordingly.

**RUNNER:** `D:\Temp\git\20_agentflow\scripts\pipeline_runner.py`

### Subcommand dispatch

1. **start "Title" --project X**: Run `python {RUNNER} intake --project X --text "Title"`
2. **scan**: Run `python {RUNNER} intake-scan`
3. **process <slug>**: Run `python {RUNNER} process --idea <slug>`
4. **process-all**: Run `python {RUNNER} process-all`
5. **status [--json]**: Run `python {RUNNER} status [--json]`
6. **decisions [--json]**: Run `python {RUNNER} decisions [--json]`
7. **resolve <idea> <stage> <choice> [notes]**: Run `python {RUNNER} resolve --idea <idea> --stage <stage> --choice <choice> [--notes "notes"]`
8. **consult <idea> <stage> [minutes]**: Run `python {RUNNER} consult --idea <idea> --stage <stage> --minutes <minutes|5>`
9. **graduate <idea>**: Run `python {RUNNER} graduate --idea <idea>`

### Default behavior (no subcommand)

If invoked as just `/pipeline` with no args, run `status` followed by `decisions`.

### Decision Panel

Remind the user that the Decision Panel is available at **http://localhost:8500** for visual review with hotkeys (1-5, c=consult, v=view, Tab=next).

Start it with: `python D:\Temp\git\05_Environment\30_temujira\decision_panel.py`

### Important

- The pipeline runner strips `CLAUDECODE` env var internally for nested `claude -p` calls
- Each stage runs `claude -p` in the source project's directory (for CLAUDE.md + skill context)
- Ideas are stored at `D:\Temp\git\20_agentflow\pipeline\ideas/<slug>/`
- Dagu DAG at `D:\Temp\AI_Content\_Helperfiles\Cloudysnc\dags\idea-pipeline.yaml` polls every 5min

## Dry Run

When `--dry-run` is passed, **do not execute any pipeline runner commands**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| parse | subcommand + arguments | Identify which pipeline operation would run |
| run | `pipeline_runner.py <subcommand>` | Describe the effect (intake/process/graduate/etc.) |
| update | `pipeline/ideas/<slug>/` | Idea state transitions that would occur |
| delegate | `claude -p` (nested) | Panel skills that would be invoked per stage |

Include the parsed subcommand, target idea slug (if applicable), and current pipeline stage.
End with confidence: **High** (valid subcommand, idea exists), **Medium** (idea in early stage), or **Low** (unknown subcommand or missing idea).
