#!/usr/bin/env bash
# deploy.sh — Push this project's docs to getaccess.cloud
set -euo pipefail

DEPLOY_REPO="$HOME/projects/deploy"
PROJECT_NAME="Shepherd / Agentflow"
SOURCE_FILE="$(cd "$(dirname "$0")/.." && pwd)/docs/index.html"
SLUG="shepherd"
DESC="Unified AI agent governance framework — 3 nested loops, 44 skills, expert panels, and Tether message bus. Structure scales autonomy."

[[ -f "$SOURCE_FILE" ]] || { echo "ERROR: $SOURCE_FILE not found"; exit 1; }

"$DEPLOY_REPO/deploy.sh" add "$PROJECT_NAME" \
  --source "$SOURCE_FILE" \
  --slug "$SLUG" \
  --desc "$DESC"

"$DEPLOY_REPO/deploy.sh" push-vps

echo "Done: http://getaccess.cloud/projects/$SLUG/"
