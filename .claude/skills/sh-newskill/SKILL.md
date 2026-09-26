---
name: sh-newskill
description: Make a new agentflow command (live via the ~/.claude/commands/sh symlink) or skill (promoted with scripts/skills_manifest.py) available in every project.
---

# Sync Agentflow Skills Globally

Make a new agentflow skill or command available globally.

## Steps

1. **Command** (`/sh:<name>`): create `.claude/commands/global/sh/<name>.md` in `~/projects/20_agentflow`. Nothing to run — `~/.claude/commands/sh` is a symlink to that dir, so it is live at once.
2. **Skill** (`.claude/skills/sh-<name>/SKILL.md`): add an entry to `skills-manifest.json` (`"status": "repo-local"`), then run `python3 ~/projects/20_agentflow/scripts/skills_manifest.py promote sh-<name>` and `... check`. Report both outputs to the user.
3. Remind the user to start a new Claude Code session for newly added skills to appear
