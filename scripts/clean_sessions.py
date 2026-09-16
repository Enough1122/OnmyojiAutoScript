"""清理超过3天的所有会话（含活跃中状态），每日凌晨3点由cron调用"""
import sqlite3
import os
import time
from pathlib import Path

db_path = Path.home() / "AppData" / "Local" / "hermes" / "state.db"

if not db_path.exists():
    print(f"DB not found: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
conn.execute("PRAGMA journal_mode=WAL")
cursor = conn.cursor()

cutoff = (time.time() - 3 * 86400)  # 3天前的秒级时间戳

# 1. 统计
cursor.execute("SELECT COUNT(*) FROM sessions WHERE started_at < ?", (cutoff,))
total_old = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sessions WHERE started_at < ? AND ended_at IS NULL", (cutoff,))
active_old = cursor.fetchone()[0]

# 2. 删除（messages外键级联）
cursor.execute("DELETE FROM sessions WHERE started_at < ?", (cutoff,))
deleted = cursor.rowcount
conn.commit()

# 3. 清理FTS残留（孤儿messages_rows）
cursor.execute("DELETE FROM messages WHERE session_id NOT IN (SELECT id FROM sessions)")
conn.commit()

conn.close()

print(f"✅ 清理完成: 删除{deleted}条会话（其中{active_old}条活跃中）")
print(f"   剩余会话: {total_old - deleted}条")
