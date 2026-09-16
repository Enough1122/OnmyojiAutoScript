#!/usr/bin/env python3
"""一键启动 OAS 探索+突破循环。

自动处理:
- 杀旧进程(端口 22267)
- 清空崩溃记录
- 配置 exploration + realm_raid (其他任务全关)
- 双写 oas.json + oas1.json
- 用 script.py oas 启动(稳定,不走 server.py)

用法:
    python start_oas.py [serial]

    # 自动检测 MuMu(默认)
    python start_oas.py

    # 指定端口
    python start_oas.py 127.0.0.1:16416
    python start_oas.py emulator-5554
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

OAS_DIR = Path('D:/Hermes/repos/OAS')
CONFIG_DIR = OAS_DIR / 'config'
TOOLKIT_PYTHON = OAS_DIR / 'toolkit' / 'python.exe'
ADB = OAS_DIR / 'toolkit' / 'Lib' / 'site-packages' / 'adbutils' / 'binaries' / 'adb.exe'
LOG_DIR = OAS_DIR / 'log'
TODAY = time.strftime('%Y-%m-%d')


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def kill_old_oas():
    """杀端口 22267 上的旧 OAS 进程"""
    r = run(['netstat', '-ano'])
    pids = set()
    for line in r.stdout.split('\n'):
        m = re.match(r'.*0\.0\.0\.0:22267.*LISTENING\s+(\d+)', line)
        if m:
            pids.add(m.group(1))
    for pid in pids:
        log(f"killing old OAS PID {pid}")
        run(['powershell', '-Command', f'Stop-Process -Id {pid} -Force'])
    if not pids:
        log("no old OAS process")
    time.sleep(2)


def clear_crash_record():
    """清空 crash_reason.txt,否则稳定性分析 cron 会读到旧的"""
    crash_file = OAS_DIR / 'crash_reason.txt'
    crash_file.write_text('', encoding='utf-8')
    log("cleared crash_reason.txt")


def detect_emulators():
    """用 adb 列出当前所有 emulator,返回 [(name, serial), ...]"""
    r = run([str(ADB), 'devices'])
    devices = []
    for line in r.stdout.split('\n')[1:]:
        if 'device' in line and 'unauthorized' not in line:
            serial = line.split()[0]
            # 去掉尾巴的 'device'
            if serial.endswith('device'):
                serial = serial[:-6].strip()
            if serial:
                devices.append(serial)
    return devices


def get_emulator_info(serial):
    """从 adb 取 android version + sdk_ver,用于选定 emulator 类型"""
    r = run([str(ADB), '-s', serial, 'shell', 'getprop', 'ro.build.version.release'],
            timeout=10)
    android_ver = r.stdout.strip() or 'unknown'
    r2 = run([str(ADB), '-s', serial, 'shell', 'getprop', 'ro.build.version.sdk'],
             timeout=10)
    sdk_ver = r2.stdout.strip() or 'unknown'
    return android_ver, sdk_ver


def write_config(serial):
    """写入 oas.json + oas1.json,启用探索 + RealmRaid,关其他任务"""
    oas_json = CONFIG_DIR / 'oas.json'
    d = json.loads(oas_json.read_text(encoding='utf-8'))

    # device serial
    d['script']['device']['serial'] = serial

    # 探索
    d['exploration']['scheduler']['enable'] = True
    d['exploration']['scheduler']['priority'] = 2
    d['exploration']['scheduler']['next_run'] = '2020-01-01 00:00:00'
    d['exploration']['minions_cnt'] = 3000
    d['exploration']['limit_time'] = '04:59:00'
    d['exploration']['scrolls']['scrolls_enable'] = True
    d['exploration']['scrolls']['scrolls_threshold'] = 25
    d['exploration']['general_battle_config']['lock_team_enable'] = True
    d['exploration']['switch_soul_config']['enable'] = False

    # 突破(个人结界 RyouToppa)关
    if 'ryou_toppa' in d:
        d['ryou_toppa']['scheduler']['enable'] = False
        d['ryou_toppa']['scheduler']['next_run'] = '2099-01-01 00:00:00'

    # RealmRaid 必须开(探索攒突破券会触发)
    if 'realm_raid' in d:
        d['realm_raid']['scheduler']['enable'] = True
        d['realm_raid']['scheduler']['priority'] = 4
        d['realm_raid']['scheduler']['next_run'] = '2020-01-01 00:00:00'
        d['realm_raid']['general_battle_config']['lock_team_enable'] = True
        d['realm_raid']['switch_soul_config']['enable'] = False

    # 关其他
    for task in ['memory_scrolls', 'orochi', 'area_boss', 'hyakkiyakou',
                 'kekka_utilize', 'kekka_activation', 'daily_trifles', 'gold_youkai',
                 'eternity_sea', 'evo_zone', 'goryou_realm']:
        if task in d:
            d[task]['scheduler']['enable'] = False

    # memory_scrolls auto_contribute 关
    if 'memory_scrolls' in d and 'memory_scrolls_config' in d['memory_scrolls']:
        d['memory_scrolls']['memory_scrolls_config']['auto_contribute_memoryscrolls'] = False

    # 双写
    oas_json.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')
    (CONFIG_DIR / 'oas1.json').write_text(
        json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')
    log(f"config written for serial={serial}")


def start_oas():
    """启动 OAS,TERM=dumb + NO_COLOR=1 绕过 colorama 死锁"""
    env_clean = {
        'PATH': 'D:/Hermes/repos/OAS/toolkit;D:/Hermes/repos/OAS/toolkit/Scripts;'
                'D:/Hermes/repos/OAS/toolkit/Git/mingw64/bin;/c/Windows/System32',
        'PYTHONUTF8': '1',
        'TERM': 'dumb',
        'NO_COLOR': '1',
    }
    log("starting OAS via script.py oas ...")
    p = subprocess.Popen(
        [str(TOOLKIT_PYTHON), '-u', str(OAS_DIR / 'script.py'), 'oas'],
        env=env_clean,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(OAS_DIR),
    )
    log(f"started PID {p.pid}")
    return p


def verify_running():
    """30 秒后看日志确认 OAS 在跑"""
    log_file = LOG_DIR / f'{TODAY}_oas1.txt'
    log(f"verifying via {log_file.name}")
    for i in range(6):
        time.sleep(5)
        if log_file.exists():
            tail = log_file.read_text(encoding='utf-8', errors='replace').split('\n')[-30:]
            if 'Game not running' in '\n'.join(tail):
                log("⚠️ Game not running - check emulator")
                return False
            if 'Pending tasks' in '\n'.join(tail):
                log("✓ OAS scheduler loaded")
                return True
    log("⚠️ no progress in 30s, check log manually")
    return False


def main():
    serial = sys.argv[1] if len(sys.argv) > 1 else None

    log("=== OAS 一键启动 ===")
    kill_old_oas()
    clear_crash_record()

    if not serial:
        devices = detect_emulators()
        if not devices:
            log("❌ no adb device found - is the emulator running?")
            return 1
        if len(devices) == 1:
            serial = devices[0]
            log(f"only one emulator: {serial}")
        else:
            log(f"multiple emulators found:")
            for i, d in enumerate(devices):
                av, sdk = get_emulator_info(d)
                log(f"  [{i}] {d}  android {av}  sdk {sdk}")
            try:
                idx = int(input("choose index: "))
                serial = devices[idx]
            except (ValueError, IndexError):
                log("invalid choice")
                return 1

    log(f"using serial: {serial}")
    write_config(serial)
    proc = start_oas()
    verify_running()
    return 0


if __name__ == '__main__':
    sys.exit(main())
