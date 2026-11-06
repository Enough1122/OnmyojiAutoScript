"""
以「脱离终端」方式启动 OAS:server + 指定配置实例。

存在的理由(2026-10-04 修复):
start_oas.py 用 subprocess.Popen(..., creationflags=CREATE_NEW_PROCESS_GROUP) 启动
server.py,子进程继承 launcher 的 stdout。而 launcher 一旦退出(正常跑完 main() 就退出),
这个 console handle 就失效了 —— 之后 server / script 每写一行日志都会抛
`OSError: [Errno 22] Invalid argument`,连 logger 的错误处理器自己在打印 traceback 时
也会因为写 stdout 失败而二次崩溃,最终整个 script 进程静默死掉。

表现和「游戏卡住」完全不同:日志里先出现业务错误(例如 GameTooManyClickError),
紧接着 Errno 22,日志文件 mtime 停在崩溃那一刻,而 WS /oas_daily 却还在报告
"running" —— 那是内存里的陈旧状态,不是真实进程。

修法:把 stdout/stderr 重定向到一个**独立打开的文件句柄**,这个句柄的生命周期
由文件本身决定,不再受 launcher 进程退出影响。

2026-11-06 追加:从 DSH 的 pwsh 工具里拉起时,server 与脚本实例会在调用结束后
约一分钟「一起静默消失」(日志无 traceback、事件查看器无记录)—— 是工具调用所在的
Windows Job Object 被关闭时连带回收了子进程。因此 server 改用
CREATE_BREAKAWAY_FROM_JOB 启动以跳出该 Job;若系统拒绝 breakaway
(Job 未开 BREAKAWAY_OK),自动退回普通 detached 模式并打印提示。
从资源管理器双击 bat 启动不受此影响。
"""
import os
import subprocess
import sys
import time

OAS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(OAS_DIR, "toolkit", "python.exe")
LOG_DIR = os.path.join(OAS_DIR, "log")
SERVER_PORT = 22267


def log(msg):
    print(f"[OAS] {msg}", flush=True)


def find_pid_by_port(port):
    try:
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        pids = set()
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    pids.add(parts[-1])
        return pids
    except Exception:
        return set()


def kill_old_server():
    """杀掉旧 server **以及它 fork 出来的脚本实例**。

    只按端口找 server 是不够的:脚本实例是 server 的 multiprocessing 子进程,
    server 被强杀后子进程会变成孤儿继续跑自己的调度器(2026-10-31 实测端口上
    有两个脚本实例同时抢模拟器,日志里每个动作都打印两遍)。
    """
    pids = set(find_pid_by_port(SERVER_PORT))
    pids.discard(str(os.getpid()))  # 本启动器用的也是 toolkit python，别把自己杀了
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             "Where-Object { $_.ExecutablePath -eq '%s' } | "
             "ForEach-Object { $_.ProcessId }" % PYTHON.replace("'", "''")],
            capture_output=True, text=True, timeout=30,
        ).stdout
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit():
                pids.add(line)
    except Exception as e:
        log(f"enumerate OAS python failed: {e}")
    pids.discard(str(os.getpid()))
    if not pids:
        return
    for pid in pids:
        log(f"killing OAS process PID {pid}")
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
            capture_output=True, text=True,
        )
    time.sleep(3)


def main(config):
    log(f"=== OAS detached start (config={config}) ===")
    kill_old_server()

    # 独立句柄:子进程写日志不再依赖本进程/控制台的生命周期
    out_path = os.path.join(LOG_DIR, "oas_console.log")
    os.makedirs(LOG_DIR, exist_ok=True)
    out = open(out_path, "a", encoding="utf-8", errors="replace")

    log(f"console log -> {out_path}")

    def spawn_server(flags):
        return subprocess.Popen(
            [PYTHON, "server.py"],
            cwd=OAS_DIR,
            stdout=out,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=flags,
        )

    detach_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    breakaway_flag = getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000)
    try:
        server_proc = spawn_server(detach_flags | breakaway_flag)
        log("spawned server with CREATE_BREAKAWAY_FROM_JOB")
    except OSError as exc:
        log(f"breakaway from job refused ({exc}); falling back to plain detached")
        log("hint: 若从 DSH/CI 等带 Job Object 的宿主拉起，请改用计划任务或双击 bat 启动")
        server_proc = spawn_server(detach_flags)
    log(f"server started (PID={server_proc.pid})")

    # 等待端口就绪
    start = time.time()
    ready = False
    while time.time() - start < 40:
        try:
            import socket
            s = socket.socket()
            s.settimeout(2)
            if s.connect_ex(("127.0.0.1", SERVER_PORT)) == 0:
                ready = True
                break
            s.close()
        except Exception:
            pass
        time.sleep(1)
    if not ready:
        log("ERROR: server failed to open port 22267")
        return 1
    log("port 22267 ready")

    # 强制 ADB_nc 截图
    try:
        import requests
        r = requests.put(
            f"http://127.0.0.1:{SERVER_PORT}/{config}/Script/device/screenshot_method/value",
            params={"types": "string", "value": "ADB_nc"},
            timeout=5,
        )
        log(f"screenshot_method=ADB_nc -> {r.text}")
    except Exception as e:
        log(f"failed to set screenshot method: {e}")

    time.sleep(1)

    # 通过 WebSocket 拉起配置实例
    try:
        import asyncio
        import websockets

        async def run():
            url = f"ws://127.0.0.1:{SERVER_PORT}/ws/{config}"
            async with websockets.connect(url) as ws:
                initial = await ws.recv()
                log(f"ws connected, initial: {initial}")
                await ws.send("start")
                await asyncio.sleep(3)
                await ws.send("get_state")
                state = await ws.recv()
                log(f"script state: {state}")

        asyncio.run(run())
    except Exception as e:
        log(f"ERROR: websocket start failed: {e}")
        return 1

    log("=== OAS running detached ===")
    log(f"watch: {os.path.join(LOG_DIR, time.strftime('%Y-%m-%d') + '_oas.txt')}")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="启动 OAS(server 与脚本均脱离终端,日志写入文件)")
    parser.add_argument("-c", "--config", default="oas_daily", help="配置名,默认 oas_daily")
    args = parser.parse_args()
    sys.exit(main(args.config))
