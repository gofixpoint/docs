#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

# Create output directory
OUTDIR="$CLAUDE_PROJECT_DIR/scratch/mcp-results"
mkdir -p "$OUTDIR"

# Write response to file
OUTFILE="$OUTDIR/$(date +%Y%m%dT%H%M%S)-${TOOL_NAME//[^a-zA-Z0-9_-]/_}.json"
echo "$INPUT" | jq '.tool_response' > "$OUTFILE"

# Return the file path as the replacement output
jq -n --arg path "$OUTFILE" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    updatedMCPToolOutput: ("MCP tool response saved to: " + $path)
  }
}'
