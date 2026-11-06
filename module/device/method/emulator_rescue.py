# -*- coding: utf-8 -*-
"""MuMu 模拟器急救：adb 彻底失联时的最后一级兜底。

Usage:
    from module.device.method.emulator_rescue import emulator_rescue
    ok = emulator_rescue(self.serial, self.adb_binary)

背景
----
2026-11-04 19:47：MuMu 内的 adbd 僵死。PC 侧 adb 能连上 TCP（端口 ESTABLISHED），
但任何命令都不回；`adb devices` 里该端口一路 offline，另一个端口显示 device 但
`shell` 一样超时。OAS 原先的空帧重连只重建 PC 侧连接（disconnect/connect），
病根在模拟器里，5 次重试全失败后只能 RequestHumanTakeover 退出，挂机停摆。

做法
----
1. `MuMuManager.exe info -v all` 按 adb_port 找到 serial 对应的实例
2. `taskkill /F /PID <实例进程>` 杀掉僵死的 MuMuNxDevice
3. `MuMuManager.exe control --vmindex <n> launch` 重新拉起
4. 轮询 `adb -s <serial> shell getprop sys.boot_completed`，最长 150 秒
5. 返回是否恢复

注意
----
- 只在 Windows、且 serial 是本机 127.0.0.1:port 时生效，否则直接返回 False（保持原行为）
- 5 分钟内最多救一次，避免失败循环变成无限重启
- 这是"最后一级"：只在 retry 的 5 次全部失败后才调用（此时本来就要退出）
"""

import json
import os
import re
import subprocess
import time

from module.logger import logger

# 用环境变量指定 MuMuManager.exe，例如 OAS_MUMU_MANAGER=E:\Game\MuMuPlayer\nx_main\MuMuManager.exe
_MANAGER_ENV = 'OAS_MUMU_MANAGER'
# 两次急救的最小间隔（秒）
_COOLDOWN = 300
# 重启实例后等待 Android 起来的最长秒数
_BOOT_TIMEOUT = 150
# 上次急救时间戳
_last_attempt = 0.0
# port -> index 缓存。实例进程死掉后 info 里就没有 adb_port 了，只能靠这里记。
_port_index = {}


def _run(cmd, timeout=20):
    """跑一条命令，异常一律吞掉返回 None。"""
    try:
        kwargs = {}
        if os.name == 'nt':
            kwargs['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        return subprocess.run(
            cmd, capture_output=True, text=True,
            encoding='utf-8', errors='ignore',
            timeout=timeout, **kwargs
        )
    except Exception as e:
        logger.warning(f'[Rescue] run `{cmd[0]}` failed: {e}')
        return None


def _find_manager():
    """
    Returns:
        str: MuMuManager.exe 的绝对路径，找不到返回空串。
    """
    # 1) 环境变量优先
    path = os.environ.get(_MANAGER_ENV, '').strip().strip('"')
    if path and os.path.isfile(path):
        return path

    # 2) 从正在运行的 MuMu 主进程反查安装目录
    try:
        import psutil
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                name = proc.info.get('name') or ''
                if name.lower() in ('mumunxmain.exe', 'mumuplayer.exe'):
                    exe = proc.info.get('exe')
                    if exe:
                        candidate = os.path.join(os.path.dirname(exe), 'MuMuManager.exe')
                        if os.path.isfile(candidate):
                            return candidate
            except Exception:
                continue
    except ImportError:
        pass

    # 3) 常见安装位置
    for base in (
        r'E:\Game\MuMuPlayer',
        r'C:\Program Files\Netease\MuMuPlayer-12.0',
        r'C:\Program Files\Netease\MuMuPlayer',
        r'D:\Program Files\Netease\MuMuPlayer-12.0',
    ):
        for rel in ('nx_main\\MuMuManager.exe', 'shell\\MuMuManager.exe', 'MuMuManager.exe'):
            candidate = os.path.join(base, rel)
            if os.path.isfile(candidate):
                return candidate
    return ''


def _mumu_info(manager):
    """
    Returns:
        dict: {index: instance_info}, 失败返回空 dict。
    """
    res = _run([manager, 'info', '-v', 'all'], timeout=20)
    if res is None or res.returncode != 0:
        return {}
    try:
        data = json.loads(res.stdout.strip().lstrip('\ufeff'))
    except (json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _instances_from_vms(manager):
    """从 vms/ 目录名解析实例序号（如 MuMuPlayer-15.0-1 -> '1'）。"""
    root = os.path.dirname(os.path.dirname(manager))
    vms = os.path.join(root, 'vms')
    indexes = []
    if os.path.isdir(vms):
        for name in os.listdir(vms):
            m = re.search(r'-(\d+)$', name)
            if m:
                indexes.append(m.group(1))
    return indexes


def _resolve_instance(serial, info, manager):
    """
    找到 serial 对应的实例序号。

    MuMu 实例进程一旦死掉，`info` 里就没有 adb_port 字段了（只有 index /
    is_android_started），所以不能只按端口匹配。

    Returns:
        (index, instance_or_None): 找不到返回 (None, None)
    """
    port = serial.split(':')[-1]

    # 1) 运行中的实例，按 adb_port 匹配
    for key, item in info.items():
        if isinstance(item, dict) and str(item.get('adb_port')) == port:
            index = str(item.get('index', key))
            _port_index[port] = index
            return index, item

    # 2) 用之前记下的映射
    index = _port_index.get(port)
    if index is not None and index in info:
        return index, info.get(index)

    # 3) 单实例兜底：vms/ 下只有一个实例就当它是
    indexes = _instances_from_vms(manager)
    if len(indexes) == 1:
        logger.info(f'[Rescue] single instance {indexes[0]} in vms, assume it is the target')
        _port_index[port] = indexes[0]
        return indexes[0], info.get(indexes[0])

    return None, None


def _adb_ready(adb_binary, serial, timeout=6):
    """设备能回 shell 才算真恢复（`adb devices` 显示 device 也可能是假的）。"""
    if adb_binary:
        _run([adb_binary, 'connect', serial], timeout=8)
    res = _run([adb_binary, '-s', serial, 'shell', 'getprop', 'sys.boot_completed'], timeout=timeout)
    if res is None or res.returncode != 0:
        return False
    return res.stdout.strip() == '1'


def emulator_rescue(serial, adb_binary, dry_run=False):
    """
    adb 彻底失联时重启对应 MuMu 实例。

    Args:
        serial (str): 例如 127.0.0.1:16416
        adb_binary (str): adb 可执行文件路径
        dry_run (bool): 只打印将要做什么，不动进程

    Returns:
        bool: True 表示 adb 已恢复（或本来就正常）
    """
    global _last_attempt

    if os.name != 'nt':
        return False
    if not serial or not serial.startswith('127.0.0.1:'):
        # 真机 / 远程设备不救
        return False
    if _adb_ready(adb_binary, serial, timeout=4):
        # 设备其实好的，不需要救
        return True

    now = time.time()
    if now - _last_attempt < _COOLDOWN:
        logger.warning(f'[Rescue] skipped, last attempt was {int(now - _last_attempt)}s ago')
        return False
    _last_attempt = now

    manager = _find_manager()
    if not manager:
        logger.warning('[Rescue] MuMuManager.exe not found, skip emulator rescue')
        return False

    info = _mumu_info(manager)
    index, instance = _resolve_instance(serial, info, manager)
    if index is None:
        logger.warning(f'[Rescue] cannot locate MuMu instance for {serial}, skip')
        return False

    pid = instance.get('pid') if instance else None
    logger.hr('Emulator rescue', level=1)
    logger.warning(f'[Rescue] MuMu instance {index} (pid={pid}) adb is dead, restarting')
    logger.info(f'[Rescue] manager: {manager}')

    if dry_run:
        logger.info(f'[Rescue] dry-run: would taskkill pid={pid} and launch vm {index}')
        return False

    if pid:
        res = _run(['taskkill', '/F', '/PID', str(pid)], timeout=20)
        if res is None:
            logger.warning('[Rescue] taskkill failed')
            return False
        logger.info(f'[Rescue] taskkill pid={pid} -> rc={res.returncode}')
        if res.returncode != 0:
            logger.warning(f'[Rescue] taskkill output: {res.stdout.strip()} {res.stderr.strip()}')

    time.sleep(3)
    res = _run([manager, 'control', '--vmindex', index, 'launch'], timeout=60)
    if res is None:
        logger.warning('[Rescue] launch failed')
        return False
    logger.info(f'[Rescue] launch vm {index} -> rc={res.returncode}')

    deadline = time.time() + _BOOT_TIMEOUT
    while time.time() < deadline:
        time.sleep(5)
        if _adb_ready(adb_binary, serial):
            logger.info('[Rescue] adb recovered')
            return True

    logger.warning(f'[Rescue] adb still unavailable after {_BOOT_TIMEOUT}s')
    return False
