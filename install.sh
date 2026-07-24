#!/usr/bin/env bash
# Install skill-self-check into Cursor personal skills (default) or a project.
# Usage:
#   ./install.sh
#   ./install.sh --project .
#   ./install.sh --dest "$HOME/.cursor/skills/skill-self-check"

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/skills/skill-self-check"
DEST=""
PROJECT=""
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest) DEST="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help)
      sed -n '2,7p' "$0"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -d "$SRC" ]]; then
  echo "Missing skills/skill-self-check at $SRC" >&2
  exit 1
fi

if [[ -z "$DEST" && -n "$PROJECT" ]]; then
  DEST="$(cd "$PROJECT" && pwd)/.cursor/skills/skill-self-check"
elif [[ -z "$DEST" ]]; then
  DEST="${HOME}/.cursor/skills/skill-self-check"
fi

mkdir -p "$(dirname "$DEST")"
if [[ -e "$DEST" && "$FORCE" -ne 1 ]]; then
  echo "Destination exists: $DEST (pass --force to overwrite)" >&2
  exit 1
fi
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "Installed skill-self-check -> $DEST"
echo "Requires Python 3.10+ (stdlib only). Try:"
echo "  python \"$DEST/scripts/hard_gates.py\" path/to/your-skill --pretty"
