"""6点停OAS+停看门狗(一次性cron调用)。WS停脚本→pause看门狗,stdout报告。"""
import subprocess
import sys

OAS_DIR = r"D:/Hermes/yyssy/OAS"
TOOL_PY = OAS_DIR + "/toolkit/python.exe"
WS_STOP = r"C:\Users\admin\AppData\Local\Temp\oas_stop.py"


def log(msg):
    print(f"[6am-stop] {msg}", flush=True)


def main():
    try:
        r = subprocess.run([TOOL_PY, WS_STOP], capture_output=True,
                           text=True, timeout=60)
        log("WS stop: " + (r.stdout.strip() or r.stderr.strip() or "sent"))
    except Exception as e:
        log(f"WS stop失败:{e}")
    try:
        r = subprocess.run(["hermes", "cron", "pause", "b7ab8ad6e41c"],
                           capture_output=True, text=True, timeout=30)
        log("看门狗已pause")
    except Exception as e:
        log(f"pause看门狗失败:{e}")
    print("RESULT: stopped-for-6am")


if __name__ == "__main__":
    main()
