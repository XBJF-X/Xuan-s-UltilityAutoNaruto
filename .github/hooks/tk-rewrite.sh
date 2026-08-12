#!/usr/bin/env bash
# TK (Token Killer) — GitHub Copilot PreToolUse hook
set -euo pipefail
command -v jq &>/dev/null || exit 1
command -v tk &>/dev/null || exit 1
[ "${TK_DISABLED:-}" = "1" ] && exit 1
INPUT=$(cat)
IS_CLI=0
echo "$INPUT" | jq -e '.toolName' &>/dev/null && IS_CLI=1
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [ -z "$CMD" ] && [ "$IS_CLI" = "1" ]; then
  TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs // empty' 2>/dev/null)
  [ -n "$TOOL_ARGS" ] && CMD=$(echo "$TOOL_ARGS" | jq -r '.command // empty' 2>/dev/null)
fi
[ -z "$CMD" ] && exit 1
REWRITTEN=$(tk rewrite "$CMD" 2>/dev/null) || exit 1
[ -z "$REWRITTEN" ] && exit 1
if [ "$IS_CLI" = "1" ]; then
  jq -n --arg r "Use `$REWRITTEN` for token savings (TK)" '{"permissionDecision":"deny","permissionDecisionReason":$r}'
else
  jq -n --arg cmd "$REWRITTEN" '{"hookSpecificOutput":{"updatedInput":{"command":$cmd}}}'
fi
exit 0
