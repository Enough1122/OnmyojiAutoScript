#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_all.py — 一键同步所有 CSV 派生文件
1. sync_visualization.py  → weight_data.js (体重可视化)
2. regen_timeline.py      → 完整体重时间线.md
两个都读同一个 CSV，跑一次全同步。
"""
import subprocess, sys
from pathlib import Path

SCRIPTS = [
    "D:/Hermes/scripts/sync_visualization.py",
    "D:/Hermes/scripts/regen_timeline.py",
]

for s in SCRIPTS:
    p = Path(s)
    if not p.exists():
        print(f"⚠️  {p.name} 不存在,跳过")
        continue
    print(f"\n{'='*50}")
    print(f"▶ {p.name}")
    print('='*50)
    r = subprocess.run([sys.executable, str(p)], capture_output=False)
    if r.returncode != 0:
        print(f"❌ {p.name} 失败 (exit {r.returncode})")
