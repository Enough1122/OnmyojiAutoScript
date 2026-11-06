"""
OAS一键启动脚本
仅需用户先启动MuMu模拟器，运行此脚本自动启动OAS并开始挂机
"""
import subprocess
import time
import asyncio
import websockets
import requests
import sys
import os
import signal

OAS_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PORT = 22267
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
PYTHON = os.path.join(OAS_DIR, "toolkit", "python.exe")
LOG_DIR = os.path.join(OAS_DIR, "log")


def log(msg):
    print(f"[OAS] {msg}")


def ws_url(config):
    return f"ws://127.0.0.1:{SERVER_PORT}/ws/{config}"


def find_pid_by_port(port):
    """Find PID listening on given port"""
    try:
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f"0.0.0.0:{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    return parts[-1]
    except:
        pass
    return None


def kill_process(pid):
    """Kill process by PID"""
    try:
        result = subprocess.run(
            ["wmic", "process", "where", f"processid='{pid}'", "delete"],
            capture_output=True, text=True
        )
        if "success" in result.stdout.lower():
            log(f"Killed old process PID={pid}")
            return True
    except:
        pass
    return False


def check_server_alive():
    """Check if server is responding"""
    try:
        r = requests.get(f"{SERVER_URL}/test", timeout=2)
        return r.status_code == 200
    except:
        return False


def wait_for_server(timeout=30):
    """Wait for server to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        if check_server_alive():
            log(f"Server ready after {time.time()-start:.1f}s")
            return True
        time.sleep(1)
    return False


async def start_script_via_ws(config):
    """Start OAS script via WebSocket"""
    async with websockets.connect(ws_url(config)) as ws:
        initial = await ws.recv()
        log(f"WS connected, initial state: {initial}")
        await ws.send("start")
        log("Sent 'start' command")
        await asyncio.sleep(3)
        await ws.send("get_state")
        state = await ws.recv()
        log(f"Script state: {state}")
        return state


def force_adb_screenshot(config):
    """Force screenshot method to ADB_nc to avoid window_background issue"""
    try:
        r = requests.put(
            f"{SERVER_URL}/{config}/Script/device/screenshot_method/value",
            params={"types": "string", "value": "ADB_nc"},
            timeout=5
        )
        if r.text == "true":
            log("Forced screenshot method to ADB_nc ✓")
            return True
    except Exception as e:
        log(f"Failed to set screenshot method: {e}")
    return False


def main(config):
    log(f"=== OAS Auto-Start (config={config}) ===")

    # 1. Kill old server if running
    pid = find_pid_by_port(SERVER_PORT)
    if pid:
        log(f"Port {SERVER_PORT} occupied by PID={pid}, killing...")
        kill_process(pid)
        time.sleep(2)

    # 2. Start server
    log("Starting OAS server...")
    server_proc = subprocess.Popen(
        [PYTHON, "server.py"],
        cwd=OAS_DIR,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    log(f"Server started (PID={server_proc.pid})")

    # 3. Wait for server ready
    if not wait_for_server():
        log("ERROR: Server failed to start!")
        return 1

    # 4. Force ADB screenshot method
    force_adb_screenshot(config)
    time.sleep(1)

    # 5. Start script via WebSocket
    asyncio.run(start_script_via_ws(config))

    # 6. Quick verification
    time.sleep(5)
    log("Let's check the log...")
    try:
        today = time.strftime("%Y-%m-%d")
        log_path = os.path.join(LOG_DIR, f"{today}_{config}.txt")
        result = subprocess.run(
            ["tail", "-5", log_path], capture_output=True, text=True
        )
        if result.stdout:
            for line in result.stdout.strip().splitlines():
                print(f"  {line}")
    except:
        pass

    log("=== OAS started successfully! ===")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OAS 一键启动：起 server 并拉起指定配置实例")
    parser.add_argument("-c", "--config", default="oas_daily",
                        help="配置名（config/ 下的 json 名，不带后缀），默认 oas_daily")
    cli_args = parser.parse_args()
    sys.exit(main(cli_args.config))
