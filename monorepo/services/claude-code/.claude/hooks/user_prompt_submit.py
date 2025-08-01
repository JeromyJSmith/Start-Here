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
    
    # Extract prompt info
    prompt = payload.get("prompt", "")
    session_id = payload.get("session_id", "unknown")
    
    # Log the prompt
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "hook": "UserPromptSubmit",
        "session_id": session_id,
        "prompt": prompt
    }
    
    with open(f"{log_dir}/hooks.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Optional: Add context or modify prompt
    # You could inject additional context here
    
    print(f"Logged prompt from session {session_id}")

if __name__ == "__main__":
    main()