#!/usr/bin/env bash
# OAS watchdog — 检查 OAS 进程是否活着，崩了重启
# 被 cronjob no_agent=True 调用

OAS_DIR="D:/Hermes/yyssy/OAS"
LOG_FILE="$OAS_DIR/log/2026-06-28_oas.txt"

# 1. 检查进程
alive=$(ps aux | grep "script.py oas" | grep -v grep | wc -l)

if [ "$alive" -ge 1 ]; then
    # 2. 检查日志是否在 3 分钟内更新
    if [ -f "$LOG_FILE" ]; then
        now=$(date +%s)
        mtime=$(stat -c "%Y" "$LOG_FILE" 2>/dev/null || echo 0)
        if [ "$((now - mtime))" -lt 180 ]; then
            exit 0  # 一切正常
        fi
    fi
fi

# OAS 挂了，重启
echo "[$(date '+%H:%M:%S')] OAS down, restarting..."

# 杀旧进程
for pid in $(ps aux | grep -E "script\.py\ oas|server\.py" | grep -v grep | awk '{print $1}'); do
    kill -9 "$pid" 2>/dev/null
done
sleep 2

# 启动
cd "$OAS_DIR" && \
env -i PATH="$OAS_DIR/toolkit;$OAS_DIR/toolkit/Scripts;$OAS_DIR/toolkit/Git/mingw64/bin;/c/Windows/System32" \
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 \
"$OAS_DIR/toolkit/python.exe" script.py oas &

echo "OAS restarted"
