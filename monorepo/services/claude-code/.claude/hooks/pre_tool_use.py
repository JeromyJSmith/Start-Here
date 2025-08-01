#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import json
import os
import sys
from datetime import datetime

# Dangerous commands and patterns to block
DANGEROUS_COMMANDS = [
    "rm -rf",
    "rm -fr", 
    "chmod 777",
    "curl | sh",
    "wget | sh"
]

BLOCKED_FILES = [
    ".env",
    ".ssh",
    "id_rsa",
    "id_ed25519",
    ".aws/credentials",
    ".gitconfig"
]

def is_dangerous(tool_name, tool_input):
    """Check if the tool usage is potentially dangerous"""
    if tool_name == "Bash":
        command = tool_input.get("command", "").lower()
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in command:
                return True, f"Blocked dangerous command: {dangerous}"
    
    if tool_name in ["Read", "Write", "Edit"]:
        file_path = tool_input.get("file_path", "").lower()
        for blocked in BLOCKED_FILES:
            if blocked in file_path:
                return True, f"Blocked access to sensitive file: {blocked}"
    
    return False, ""

def main():
    # Read the JSON payload from stdin
    if sys.stdin.isatty():
        print("No JSON payload received", file=sys.stderr)
        sys.exit(1)
    
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract tool info
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    
    # Log the tool use
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "hook": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input
    }
    
    with open(f"{log_dir}/hooks.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Check for dangerous operations
    is_blocked, reason = is_dangerous(tool_name, tool_input)
    if is_blocked:
        print(f"BLOCKED: {reason}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Allowed tool use: {tool_name}")

if __name__ == "__main__":
    main()