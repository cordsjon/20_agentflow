#!/bin/bash
# sync-skills-global.sh — Copy agentflow skills into ~/.claude/commands/ for global access
# Run this after adding/removing skills in the agentflow repo.
#
# Structure mapping:
#   skills/sh-brainstorm/SKILL.md   → ~/.claude/commands/sh/brainstorm.md
#   skills/agentflow-loop/SKILL.md  → ~/.claude/commands/agentflow/loop.md
#
# Uses cp (not symlinks) because Claude Code doesn't follow symlinks in commands/.

set -euo pipefail

SKILLS_DIR="$HOME/projects/20_agentflow/.claude/skills"
COMMANDS_DIR="$HOME/.claude/commands"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "ERROR: Skills directory not found: $SKILLS_DIR"
  exit 1
fi

# Track counts
added=0
updated=0
removed=0
skipped=0

sync_namespace() {
  local prefix="$1"    # e.g. "sh" or "agentflow"
  local ns_dir="$COMMANDS_DIR/$prefix"
  mkdir -p "$ns_dir"

  # Remove commands that no longer have a source skill
  for target in "$ns_dir"/*.md; do
    [ -f "$target" ] || continue
    local cmd_name=$(basename "$target" .md)
    local source_dir="$SKILLS_DIR/${prefix}-${cmd_name}"
    if [ ! -d "$source_dir" ] || [ ! -f "$source_dir/SKILL.md" ]; then
      echo "  REMOVE ${prefix}:${cmd_name} (source deleted)"
      rm "$target"
      ((removed++))
    fi
  done

  # Copy new/updated skills
  for skill_dir in "$SKILLS_DIR"/${prefix}-*/; do
    [ -d "$skill_dir" ] || continue
    local skill_md="$skill_dir/SKILL.md"
    [ -f "$skill_md" ] || continue

    # sh-brainstorm → brainstorm
    local name=$(basename "$skill_dir" | sed "s/^${prefix}-//")
    local target="$ns_dir/${name}.md"

    # Skip if target exists, is not a symlink, and content matches
    if [ -f "$target" ] && [ ! -L "$target" ] && diff -q "$skill_md" "$target" >/dev/null 2>&1; then
      ((skipped++))
      continue
    fi

    # Remove stale symlink if present (migration from old script)
    [ -L "$target" ] && rm "$target"

    cp "$skill_md" "$target"
    if [ -f "$target" ]; then
      # Check if this was a new file or an update
      if diff -q "$skill_md" "$target" >/dev/null 2>&1; then
        echo "  COPY ${prefix}:${name}"
        ((added++))
      fi
    fi
  done
}

sync_namespace "sh"
sync_namespace "agentflow"

echo ""
echo "Sync complete: $added copied, $removed removed, $skipped unchanged"
echo "Skills available globally as /sh:<name> and /agentflow:<name>"
echo "Restart Claude Code for changes to take effect."
