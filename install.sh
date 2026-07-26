#!/usr/bin/env bash
# Install the four stable workflow, audit, safety, and scorecard skills
# (default) or a project.
# Usage:
#   ./install.sh
#   ./install.sh --project .
#   ./install.sh --dest "$HOME/.cursor/skills/skill-self-check"   # single skill, legacy
#   ./install.sh --skills skill-self-check                        # pick skills

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST=""
PROJECT=""
FORCE=0
SKILLS=(
  skill-self-check
  skill-ship-safety
  agent-work-readiness
  skill-growth-scorecard
)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest) DEST="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --skills) IFS=',' read -r -a SKILLS <<< "$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help)
      sed -n '2,8p' "$0"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -n "$DEST" ]]; then
  # Legacy single-destination mode: install the first requested skill only.
  SKILLS=("${SKILLS[0]}")
fi

if [[ -z "$DEST" && -n "$PROJECT" ]]; then
  BASE="$(cd "$PROJECT" && pwd)/.cursor/skills"
elif [[ -z "$DEST" ]]; then
  BASE="${HOME}/.cursor/skills"
fi

for SKILL in "${SKILLS[@]}"; do
  SRC="$ROOT/skills/$SKILL"
  if [[ ! -d "$SRC" ]]; then
    echo "Missing skills/$SKILL at $SRC" >&2
    exit 1
  fi

  if [[ -n "$DEST" ]]; then
    TARGET="$DEST"
  else
    TARGET="$BASE/$SKILL"
  fi

  TARGET_PARENT="$(dirname "$TARGET")"
  mkdir -p "$TARGET_PARENT"
  TARGET_PARENT_ABS="$(cd "$TARGET_PARENT" && pwd -P)"
  TARGET_ABS="$TARGET_PARENT_ABS/$(basename "$TARGET")"
  HOME_ABS="$(cd "$HOME" && pwd -P)"

  if [[ "$(basename "$TARGET_ABS")" != "$SKILL" ]]; then
    echo "Install target must end with the skill name '$SKILL': $TARGET_ABS" >&2
    exit 1
  fi
  if [[ "$TARGET_ABS" == "$HOME_ABS" || "$TARGET_ABS" == "$ROOT" ]]; then
    echo "Unsafe install target: $TARGET_ABS" >&2
    exit 1
  fi
  if [[ "$TARGET_PARENT_ABS" == "/" ]]; then
    echo "Refusing to install directly under the filesystem root: $TARGET_ABS" >&2
    exit 1
  fi
  TARGET="$TARGET_ABS"

  if [[ -e "$TARGET" && "$FORCE" -ne 1 ]]; then
    echo "Destination exists: $TARGET (pass --force to overwrite)" >&2
    exit 1
  fi
  rm -rf "$TARGET"
  cp -R "$SRC" "$TARGET"
  echo "Installed $SKILL -> $TARGET"
done

echo "Requires Python 3.10+ (stdlib only). Try:"
echo "  python \"\$HOME/.cursor/skills/skill-self-check/scripts/run_full_audit.py\" path/to/your-skill --out-dir path/outside/the/repo --pretty"
echo "  python \"\$HOME/.cursor/skills/skill-self-check/scripts/hard_gates.py\" path/to/your-skill --pretty"
echo "  python \"\$HOME/.cursor/skills/skill-ship-safety/scripts/ship_safety.py\" path/to/your-skill --pretty"
echo "  python \"\$HOME/.cursor/skills/agent-work-readiness/scripts/readiness_gates.py\" path/to/work-package --pretty"
echo "  python \"\$HOME/.cursor/skills/skill-growth-scorecard/scripts/profile_engine.py\" --readiness readiness.json --out-html scorecard.html"
