#!/bin/bash
# sync-skills-global.sh — RETIRED 2026-06-26 (US-SKILLHOME-01)
#
# This cp-based sync is obsolete. ~/.claude/commands/sh is now a SYMLINK to
# this repo's .claude/commands/global/sh — skills authored here are live in
# every project instantly, with no copy step and no drift.
#
# The old script's premise ("Claude Code doesn't follow symlinks in commands/")
# was disproven: both file- and directory-symlinks load live without restart.
#
# If you are looking for the old behavior, you don't need it. To add a NEW
# command, just create it under .claude/commands/global/sh/<name>.md and it is
# immediately available as /sh:<name>.
#
# Rollback (if the symlink ever needs undoing):
#   rm ~/.claude/commands/sh
#   cp -R ~/.claude/_skills-migration-backup-2026-06-26/commands-sh ~/.claude/commands/sh

set -euo pipefail

cat <<'EOF'
sync-skills-global.sh is RETIRED (US-SKILLHOME-01, 2026-06-26).

~/.claude/commands/sh is now a symlink to this repo's .claude/commands/global/sh.
Skills here are live everywhere with no sync step — nothing to run.

To add a new command: create .claude/commands/global/sh/<name>.md → it is
immediately /sh:<name>. No copy needed.
EOF
exit 0
