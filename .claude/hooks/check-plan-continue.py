#!/usr/bin/env python3
"""
PermissionRequest hook for ExitPlanMode: inspects the plan and decides
whether to approve (allow Claude to proceed with implementation) or deny
(send feedback to revise the plan).

Receives JSON on stdin with tool_input.plan containing the plan text.
Outputs a PermissionRequest decision JSON to stdout.
"""

import json
import os
import sys
from datetime import datetime

LOG_PATH = "/tmp/dylan/cc-hooks.log"


def should_continue_with_plan(plan_content: str) -> tuple[bool, str]:
    """
    Inspect the plan contents and decide whether to continue.

    Args:
        plan_content: The text output from the planning phase.

    Returns:
        A tuple of (should_continue, reason).

    TODO: Implement your decision logic here. Examples:
        - Check if the plan contains risky operations (e.g., database migrations)
        - Verify the plan stays within scope of the original request
        - Reject plans that touch too many files
        - Require plans to include a test strategy
        - Check for specific keywords or patterns
    """
    ################################################################################
    # PLACEHOLDER: Replace this with your actual decision logic
    ################################################################################

    # Example: block plans that mention deleting production data
    # if "drop table" in plan_content.lower():
    #     return False, "Plan includes destructive database operations — refusing to continue."

    # Example: block plans that modify more than N files
    # mentioned_files = re.findall(r'`([^`]+\.\w+)`', plan_content)
    # if len(mentioned_files) > 20:
    #     return False, f"Plan touches {len(mentioned_files)} files — too broad."

    # Default: allow the plan to proceed
    return True, "Plan looks acceptable."
    ################################################################################


def log(message: str):
    """Append a timestamped message to the log file."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        log("Failed to parse hook input (JSON decode error or EOF)")
        # If we can't parse input, don't block — approve by default
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": {"behavior": "allow"},
                }
            },
            sys.stdout,
        )
        sys.exit(0)

    # Extract the plan from tool_input.plan
    tool_input = hook_input.get("tool_input", {})
    plan_content = tool_input.get("plan", "")

    log(f"ExitPlanMode hook triggered")
    log(f"Plan length: {len(plan_content)} chars")
    log(f"Plan preview: {plan_content[:500]!r}")

    should_continue, reason = should_continue_with_plan(plan_content)
    log(f"Decision: should_continue={should_continue}, reason={reason!r}")

    if should_continue:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"},
            }
        }
    else:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "deny",
                    "message": f"Plan rejected: {reason}",
                },
            }
        }

    log(f"Outputting result: {json.dumps(result)}")
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()

