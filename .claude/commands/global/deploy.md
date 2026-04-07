Run the deploy script: execute `powershell.exe -File "D:\Temp\git\SVG-PAINT\run.ps1"` in bash. This pulls latest code, builds with Cairo, and starts the server on port 9001.

## Dry Run

When `--dry-run` is passed, **do not execute the deploy script**. Instead, output a synopsis:

| Action | Target | What Would Change |
|--------|--------|-------------------|
| run | `run.ps1` | Pull latest code from git |
| build | Cairo dependencies | Rebuild native dependencies |
| start | server on port 9001 | Start/restart the application server |

Include current git status (branch, uncommitted changes) and whether port 9001 is already in use.
End with confidence: **High** (clean state, no conflicts), **Medium** (uncommitted changes present), or **Low** (build issues likely).