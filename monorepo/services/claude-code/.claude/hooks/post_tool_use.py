#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import json
import os
import sys
from datetime import datetime

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
    tool_response = payload.get("tool_response", {})
    
    # Log the tool result
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "hook": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_response": tool_response
    }
    
    with open(f"{log_dir}/hooks.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"Logged result from tool: {tool_name}")

if __name__ == "__main__":
    main()