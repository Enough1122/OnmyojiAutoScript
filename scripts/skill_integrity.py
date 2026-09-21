# -*- coding: utf-8 -*-
"""出厂技能完整性核对 —— 安装副本 vs 出厂源目录直接对拷(只读)

用户会反复问"你会不会把出厂的技能改得面目全非了/还是原版吗",这个脚本给答案:
  Hermes 安装目录的出厂源: <hermes>/hermes-agent/skills/<category>/<skill>/SKILL.md
  本机安装副本:            <hermes>/skills/<category>/<skill>/SKILL.md

为什么不用 skills/.bundled_manifest:它是 name:md5 清单,但 2026-09-21 实测
58 条**全部**对不上(试过 raw / CRLF 归一 / strip / sha1 / sha256 五种算法都不命中),
方案未知,拿它做完整性判断会误报"全被改了"。直接对拷源目录才是可信基线。

用法: python D:/Hermes/scripts/skill_integrity.py [--diff 技能名]
输出: 一致/有差异/未安装 三组;--diff 时打印某个技能的逐行差异。
"""
import difflib
import hashlib
import os
import sys

HERMES = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes")
SRC = os.path.join(HERMES, "hermes-agent", "skills")
DST = os.path.join(HERMES, "skills")


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def scan():
    same, diff, missing = [], [], []
    for root, _dirs, files in os.walk(SRC):
        if "SKILL.md" not in files:
            continue
        rel = os.path.relpath(os.path.join(root, "SKILL.md"), SRC)
        d = os.path.join(DST, rel)
        if not os.path.exists(d):
            missing.append(rel)
        elif md5(os.path.join(root, "SKILL.md")) == md5(d):
            same.append(rel)
        else:
            diff.append(rel)
    return same, diff, missing


def show_diff(rel):
    a = open(os.path.join(SRC, rel), encoding="utf-8", errors="replace").read().splitlines()
    b = open(os.path.join(DST, rel), encoding="utf-8", errors="replace").read().splitlines()
    for line in difflib.unified_diff(a, b, "出厂源", "本机副本", lineterm="", n=1):
        print(line)


if __name__ == "__main__":
    same, diff, missing = scan()
    print(f"出厂技能核对({SRC} ↔ {DST})")
    print(f"  一致 {len(same)} | 有差异 {len(diff)} | 本机未安装 {len(missing)}")
    if diff:
        print("\n有差异的:")
        for rel in sorted(diff):
            s = os.path.getsize(os.path.join(SRC, rel))
            d = os.path.getsize(os.path.join(DST, rel))
            print(f"  {rel:68} {s:6d}B → {d:6d}B ({d - s:+d})")
    if missing:
        print("\n本机未安装(通常为 mac 专用或用户没装的连接器):")
        for rel in sorted(missing):
            print("  " + rel)
    if len(sys.argv) > 2 and sys.argv[1] == "--diff":
        target = sys.argv[2]
        hit = [r for r in diff if target in r]
        if not hit:
            print(f"\n没有含 '{target}' 的差异项")
        for rel in hit:
            print(f"\n=== {rel} ===")
            show_diff(rel)
