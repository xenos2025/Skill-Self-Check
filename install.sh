#!/usr/bin/env bash
# Install skill-self-check + skill-ship-safety into Cursor personal skills
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
SKILLS=(skill-self-check skill-ship-safety)

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

  mkdir -p "$(dirname "$TARGET")"
  if [[ -e "$TARGET" && "$FORCE" -ne 1 ]]; then
    echo "Destination exists: $TARGET (pass --force to overwrite)" >&2
    exit 1
  fi
  rm -rf "$TARGET"
  cp -R "$SRC" "$TARGET"
  echo "Installed $SKILL -> $TARGET"
done

echo "Requires Python 3.10+ (stdlib only). Try:"
echo "  python \"\$HOME/.cursor/skills/skill-self-check/scripts/hard_gates.py\" path/to/your-skill --pretty"
echo "  python \"\$HOME/.cursor/skills/skill-ship-safety/scripts/ship_safety.py\" path/to/your-skill --pretty"
