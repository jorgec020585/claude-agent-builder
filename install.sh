#!/bin/bash
# Claude Agent Builder — Quick Install Script
# Usage: ./install.sh [--project]

set -e

SKILL_DIR="agent-builder"

if [ "$1" = "--project" ]; then
    TARGET=".claude/skills"
    echo "📁 Installing to project-level: $TARGET/$SKILL_DIR"
else
    TARGET="$HOME/.claude/skills"
    echo "📁 Installing to user-level: $TARGET/$SKILL_DIR"
fi

mkdir -p "$TARGET"

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -d "$SCRIPT_DIR/$SKILL_DIR" ]; then
    cp -r "$SCRIPT_DIR/$SKILL_DIR" "$TARGET/"
    echo "✅ Installed successfully!"
    echo ""
    echo "Open Claude Code and try:"
    echo '  > Build me an agent that [describe your use case]'
else
    echo "❌ Error: $SKILL_DIR directory not found. Run this from the repo root."
    exit 1
fi
