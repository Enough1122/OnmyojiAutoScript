#!/usr/bin/env python3
"""Auto-sync recent conversation turns to MemOS Cloud.

Queries the Hermes state.db for new messages in the most recent
user-facing session and pushes them to MemOS Cloud via the
memos_cloud_sync.py script. Tracks progress via a state file.

Usage: python memos_auto_sync.py
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta

# Paths
STATE_DB = os.path.expanduser(
    "~/AppData/Local/hermes/state.db"
)
SYNC_SCRIPT = os.path.join(os.path.dirname(__file__), "memos_cloud_sync.py")
STATE_FILE = os.path.join(os.path.dirname(__file__), ".memos_sync_state.json")

# Exclude cron sessions (they're automated, not user conversation)
CRON_PREFIXES = ("cron_", "delegation_", "child_")

TZ = timezone(timedelta(hours=8), "CST")


def get_latest_user_session(cur) -> str | None:
    """Find the most recent non-cron, non-delegation session with user messages."""
    cur.execute("""
        SELECT id FROM sessions
        WHERE id NOT LIKE 'cron_%'
          AND id NOT LIKE 'delegation_%'
          AND id NOT LIKE 'child_%'
          AND ended_at IS NULL
        ORDER BY started_at DESC
        LIMIT 3
    """)
    return [r[0] for r in cur.fetchall()]


def get_unsynced_messages(cur, session_ids: list[str], last_id: int, limit: int = 20):
    """Get messages newer than last_id from given sessions."""
    placeholders = ",".join("?" for _ in session_ids)
    cur.execute(f"""
        SELECT id, role, content, timestamp
        FROM messages
        WHERE session_id IN ({placeholders})
          AND id > ?
          AND role IN ('user', 'assistant')
          AND content != ''
        ORDER BY id ASC
        LIMIT ?
    """, (*session_ids, last_id, limit))
    return cur.fetchall()


def push_to_memos(turns: list[tuple]) -> bool:
    """Push conversation turns to MemOS Cloud, returns True on success."""
    if not turns:
        return False

    # Build pairs of user/assistant messages
    args = []
    for msg_id, role, content, ts in turns:
        # Truncate very long messages to avoid token limits
        text = content[:2000] if len(content) > 2000 else content
        args.append(text)

    if not args:
        return False

    cmd = f'python "{SYNC_SCRIPT}"'
    for a in args:
        # Escape single quotes
        escaped = a.replace("'", "'\\''")
        cmd += f" '{escaped}'"

    # We'll use subprocess to call the sync script
    import subprocess
    result = subprocess.run(
        ["python", SYNC_SCRIPT] + args,
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print(f"OK: synced {len(turns)} messages ({len(args)} turns) to MemOS Cloud")
        return True
    else:
        print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
        return False


def load_state() -> int:
    """Load last synced message ID from state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                return data.get("last_synced_id", 0)
        except (json.JSONDecodeError, KeyError):
            return 0
    return 0


def save_state(last_id: int):
    """Save last synced message ID to state file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({
            "last_synced_id": last_id,
            "updated_at": datetime.now(TZ).isoformat()
        }, f)


def main():
    if not os.path.exists(STATE_DB):
        print(f"ERROR: state.db not found at {STATE_DB}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(STATE_DB)
    cur = conn.cursor()

    session_ids = get_latest_user_session(cur)
    if not session_ids:
        print("SKIP: no active user sessions found")
        conn.close()
        return

    last_id = load_state()
    turns = get_unsynced_messages(cur, session_ids, last_id)
    if not turns:
        print(f"SKIP: no new messages (last_id={last_id})")
        conn.close()
        return

    print(f"Found {len(turns)} new messages (last_id={last_id})")

    # Push all at once
    success = push_to_memos(turns)

    if success:
        new_last_id = max(t[0] for t in turns)
        save_state(new_last_id)
        print(f"State updated: last_synced_id -> {new_last_id}")
    else:
        print("WARN: push failed, state NOT updated (will retry next run)", file=sys.stderr)

    conn.close()


if __name__ == "__main__":
    main()