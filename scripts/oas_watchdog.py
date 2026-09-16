"""OAS看门狗(v1,供cron no_agent调用)
检查:1)22267端口在听? 2)当日oas日志15分钟内有动静?
任一失败→taskkill+拉start_oas.py,stdout报告(空=静默);exit!=0→告警
纯stdlib,双击可测"""
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta

OAS_DIR = r"D:/Hermes/yyssy/OAS"
TOOL_PY = OAS_DIR + "/toolkit/python.exe"
PORT = 22267
STALE_MIN = 15
ALERT_WINDOW_MIN = 30
STATE_FILE = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\admin\AppData\Local"),
                          "hermes", "cron", "oas_watchdog.state")


def log(msg):
    print(f"[watchdog] {msg}", flush=True)


def port_listening():
    s = socket.socket()
    s.settimeout(3)
    try:
        return s.connect_ex(("127.0.0.1", PORT)) == 0
    finally:
        s.close()


def latest_oas_log():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    for d in (today, yesterday):
        p = os.path.join(OAS_DIR, "log", f"{d}_oas.txt")
        if os.path.exists(p):
            return p
    return None


def log_fresh(path, minutes):
    try:
        return (time.time() - os.path.getmtime(path)) < minutes * 60
    except OSError:
        return False


def load_last_alert():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError):
        return None


def save_last_alert(ts):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(ts.strftime("%Y-%m-%d %H:%M:%S"))
    except OSError:
        pass


def recent_human_takeover(path, minutes):
    """近N分钟内、且未报过警的人工接管请求(去重)"""
    try:
        cutoff = datetime.now() - timedelta(minutes=minutes)
        last_alert = load_last_alert()
        tail = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-Content -Tail 300 -Path '{path}' | Select-String -Pattern 'human takeover|failed 3 or more|Game page unknown' | Select-Object -Last 5"],
            capture_output=True, text=True, timeout=30)
        lines = [l for l in tail.stdout.strip().splitlines() if l.strip()]
        fresh = []
        newest = None
        for l in lines:
            m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", l)
            if not m:
                continue
            ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
            if ts < cutoff:
                continue
            if last_alert and ts <= last_alert:
                continue
            fresh.append(l)
            newest = ts if newest is None or ts > newest else newest
        if fresh and newest:
            save_last_alert(newest)
        return "\n".join(fresh[-3:])
    except Exception as e:
        return f"(检查失败:{e})"


def kill_by_port():
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True,
                             text=True, timeout=15).stdout
        for line in out.splitlines():
            if f"0.0.0.0:{PORT}" in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid],
                               capture_output=True, timeout=15)
                log(f"已杀旧后端 PID={pid}")
                time.sleep(3)
                return True
    except Exception as e:
        log(f"杀进程失败:{e}")
    return False


def relaunch():
    try:
        subprocess.Popen(
            [TOOL_PY, os.path.join(OAS_DIR, "start_oas.py")],
            cwd=OAS_DIR,
            creationflags=0x00000008 | 0x00000200,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("已拉起 start_oas.py,等30s验端口")
        for _ in range(6):
            time.sleep(5)
            if port_listening():
                log("后端端口恢复 ✅")
                return True
        log("拉起后端口仍无监听 ❌")
        return False
    except Exception as e:
        log(f"拉起失败:{e}")
        return False


def main():
    if not port_listening():
        log(f"端口{PORT}无监听,后端已死→重启")
        kill_by_port()
        ok = relaunch()
        print("RESULT: " + ("recovered" if ok else "FAILED"))
        sys.exit(0 if ok else 1)
    path = latest_oas_log()
    if not path or not log_fresh(path, STALE_MIN):
        log(f"日志超{STALE_MIN}分钟不动({path})→重启后端")
        kill_by_port()
        ok = relaunch()
        print("RESULT: " + ("recovered" if ok else "FAILED"))
        sys.exit(0 if ok else 1)
    hit = recent_human_takeover(path, ALERT_WINDOW_MIN)
    if hit and "检查失败" not in hit:
        log(f"近{ALERT_WINDOW_MIN}分钟内有人接管/连跪请求,需人看:")
        print(hit[-1500:])
        print("RESULT: needs-human")
        sys.exit(2)
    # 一切正常→静默
    sys.exit(0)


if __name__ == "__main__":
    main()
