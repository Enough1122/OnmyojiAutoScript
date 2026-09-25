# -*- coding: utf-8 -*-
"""工作空间异地备份:D:/Hermes 整仓 -> 私有仓库 hermes-workspace

用法:  python D:/Hermes/scripts/backup_life.py

流程:  git add -A -> 有变化才 commit -> push
真源即工作目录,无副本、无镜像 —— 版本控制直接作用于工作空间本身。

安全约定:
  * 只操作 D:/Hermes 自己的 git;外部/独立仓统一放在 repos/(已被 .gitignore
    整夹排除),不触碰
  * 仓库必须保持 private —— 历史里有完整体重与健康记录

每一步的返回码都必须检查。`git add -A` 会因为工作区里任何
"does not have a commit checked out" 的嵌套 worktree 而整批失败(退出码 128),
此前未检查返回值,导致 23:00 备份静默空跑:连续两晚 last_status=ok
但仓库最新提交仍停在 09-24 23:00。失败必须显式报错退出,不能伪装成成功。
"""
import subprocess
import sys
from pathlib import Path

SPACE = Path("D:/Hermes")
LABEL = "工作空间"


def git(args):
    return subprocess.run(["git"] + args, cwd=SPACE, capture_output=True, text=True)


def main():
    added = git(["add", "-A"])
    if added.returncode != 0:
        # 典型原因:临时 worktree 未 checkout commit,或 .gitignore 漏了新的临时目录
        detail = (added.stderr or added.stdout).strip().replace("\n", " | ")[:400]
        print(f"{LABEL}: git add -A 失败(退出码 {added.returncode}),未提交任何内容:{detail}")
        sys.exit(1)

    status = git(["status", "--porcelain"]).stdout.strip()
    if not status:
        print(f"{LABEL}: 无变化")
        return

    n = len(status.splitlines())
    committed = git(["commit", "-m", f"自动备份:{n} 处变更"])
    if committed.returncode != 0:
        detail = (committed.stderr or committed.stdout).strip().replace("\n", " | ")[:400]
        print(f"{LABEL}: git commit 失败(退出码 {committed.returncode}),暂存内容保留待处理:{detail}")
        sys.exit(1)

    pushed = git(["push"])
    if pushed.returncode == 0:
        print(f"{LABEL}: 已推送 {n} 处变更")
    else:
        print(f"{LABEL}: push 失败 {pushed.stderr[:200]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
