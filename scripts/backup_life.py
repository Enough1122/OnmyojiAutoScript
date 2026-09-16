# -*- coding: utf-8 -*-
"""工作空间异地备份:D:/Hermes 整仓 -> 私有仓库 hermes-workspace

用法:  python D:/Hermes/scripts/backup_life.py

流程:  git add -A -> 有变化才 commit -> push
真源即工作目录,无副本、无镜像 —— 版本控制直接作用于工作空间本身。

安全约定:
  * 只操作 D:/Hermes 自己的 git;子目录里的独立仓(hermes-agent-fix /
    lark-coding-agent-bridge / ai-berkshire / OAS)已被 .gitignore 排除,不触碰
  * 仓库必须保持 private —— 历史里有完整体重与健康记录
"""
import subprocess
from pathlib import Path

SPACE = Path("D:/Hermes")
LABEL = "工作空间"


def git(args):
    return subprocess.run(["git"] + args, cwd=SPACE, capture_output=True, text=True)


def main():
    git(["add", "-A"])
    status = git(["status", "--porcelain"]).stdout.strip()
    if not status:
        print(f"{LABEL}: 无变化")
        return
    n = len(status.splitlines())
    git(["commit", "-m", f"自动备份:{n} 处变更"])
    pushed = git(["push"])
    if pushed.returncode == 0:
        print(f"{LABEL}: 已推送 {n} 处变更")
    else:
        print(f"{LABEL}: push 失败 {pushed.stderr[:200]}")


if __name__ == "__main__":
    main()
