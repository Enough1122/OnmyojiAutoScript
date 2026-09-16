# -*- coding: utf-8 -*-
"""生活数据异地备份:健康 / 日记 / 记录 -> 私有 GitHub 仓库

用法:  python D:/Hermes/scripts/backup_life.py

流程: 镜像复制(先清后拷) -> git add -A -> 有变化才 commit -> push

安全约定:
  * 永远只读 D:/Hermes/ 下的真源,只写 D:/Hermes/projects/life-backup/
  * 本脚本不会删除真源里的任何文件
  * 仓库必须保持 private —— 历史里有完整体重与健康记录
"""
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path("D:/Hermes")
REPO = Path("D:/Hermes/projects/life-backup")
MAP = [("健康", "health"), ("diary", "diary"), ("记录", "records")]


def run(args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def main():
    if not REPO.exists():
        sys.exit(f"仓库目录不存在: {REPO}")
    if not (REPO / ".git").exists():
        sys.exit(f"不是 git 仓库: {REPO}")

    for src_name, dst_name in MAP:
        src, dst = SRC / src_name, REPO / dst_name
        if not src.exists():
            print(f"跳过(真源不存在): {src}")
            continue
        if dst.exists():
            shutil.rmtree(dst)          # 先清后拷 -> 删除操作也能同步
        shutil.copytree(src, dst)
        print(f"镜像: {src_name}/ -> {dst_name}/  ({len(list(dst.rglob('*')))} 项)")

    run(["git", "add", "-A"])
    status = run(["git", "status", "--porcelain"]).stdout.strip()
    if not status:
        print("无变化,无需提交")
        return
    n = len(status.splitlines())
    run(["git", "commit", "-m", f"自动备份:{n} 处变更"])
    pushed = run(["git", "push"])
    if pushed.returncode == 0:
        print(f"已推送 {n} 处变更")
    else:
        print(f"push 失败:{pushed.stderr[:300]}")


if __name__ == "__main__":
    main()
