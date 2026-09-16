#!/usr/bin/env python3
"""One-way sync to MemOS Cloud — store only, no recall.

Usage:
  python memos_cloud_sync.py "user message" "assistant response"
  python memos_cloud_sync.py --file /path/to/turns.json
  python memos_cloud_sync.py --last  # sync most recent session turns

Uses MEMOS_API_KEY and MEMOS_USER_ID from environment.
"""

import json
import os
import sys
import httpx

BASE_URL = os.environ.get("MEMOS_BASE_URL", "https://memos.memtensor.cn/api/openmem/v1")


def _get_creds() -> tuple[str, str]:
    key = os.environ.get("MEMOS_API_KEY", "")
    uid = os.environ.get("MEMOS_USER_ID", "")
    if not key or not uid:
        print("ERROR: MEMOS_API_KEY and MEMOS_USER_ID must be set", file=sys.stderr)
        sys.exit(1)
    return key, uid


def sync_turns(turns: list[dict], conversation_id: str = "") -> bool:
    """Upload turns to MemOS Cloud. Returns True on success."""
    api_key, user_id = _get_creds()
    conv_id = conversation_id or turns[0].get("content", "")[:200] if turns else "fallback"

    try:
        url = f"{BASE_URL}/add/message"
        payload = {
            "user_id": user_id,
            "conversation_id": conv_id,
            "messages": turns,
        }
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=15.0)
        resp.raise_for_status()
        print(f"OK: synced {len(turns)} turns to MemOS Cloud")
        return True
    except Exception as e:
        print(f"ERROR: sync failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--file" and len(sys.argv) >= 3:
        with open(sys.argv[2]) as f:
            turns = json.load(f)
        sync_turns(turns)
    elif sys.argv[1] == "--last":
        # Sync from stdin — pipe conversation JSON
        turns = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else []
        sync_turns(turns)
    else:
        # CLI: user_msg assistant_msg ...
        turns = []
        role = "user"
        for arg in sys.argv[1:]:
            turns.append({"role": role, "content": arg})
            role = "assistant" if role == "user" else "user"
        if turns:
            sync_turns(turns)
