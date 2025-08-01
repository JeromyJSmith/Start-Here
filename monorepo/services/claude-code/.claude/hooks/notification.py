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
    
    # Extract notification info
    message = payload.get("message", "")
    
    # Log the notification
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "hook": "Notification",
        "message": message
    }
    
    with open(f"{log_dir}/hooks.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"Notification: {message}")

if __name__ == "__main__":
    main()