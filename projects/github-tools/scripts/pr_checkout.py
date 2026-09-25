#!/usr/bin/env python
"""Build an exact base/head checkout for one PR into a scratch dir (no upstream mutation).

usage: pr_checkout.py <pr> <base_sha> <head_sha> [dest]
"""
import subprocess
import sys
from pathlib import Path

pr, base_sha, head_sha = sys.argv[1], sys.argv[2], sys.argv[3]
dest = Path(sys.argv[4] if len(sys.argv) > 4 else f'D:/Hermes/cache-review-pr{pr}-exact')
upstream = 'https://github.com/NousResearch/hermes-agent.git'


def force_rmtree(path: Path) -> None:
    """Remove a tree even when git left read-only pack files behind.

    ``shutil.rmtree`` raises PermissionError (WinError 5) on Windows for
    ``-r--r--r--`` objects, so every entry's mode is restored first. A plain
    rmtree failure here is an environment artifact, never a PR signal.
    """
    if not path.exists():
        return
    import os
    import shutil
    import stat
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            target = Path(root) / name
            try:
                target.chmod(stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        for name in dirs:
            target = Path(root) / name
            try:
                target.chmod(stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            except OSError:
                pass
    shutil.rmtree(path, ignore_errors=True)
    if path.exists():
        shutil.rmtree(path)


force_rmtree(dest)
dest.mkdir(parents=True)


def run(*args, timeout: int = 900, **kw):
    p = subprocess.run(['git', *args], cwd=str(dest), text=True, capture_output=True,
                       timeout=timeout, **kw)
    if p.returncode:
        sys.exit(f'FAILED git {" ".join(args)}\n{p.stdout}\n{p.stderr}')
    return p.stdout.strip()


run('init', '-q')
run('remote', 'add', 'upstream', upstream)
# A shallow fetch of either ref is tens of MB; give it room and never let a
# stalled transfer look like a PR problem.
run('fetch', '-q', '--depth=1', '--no-tags', 'upstream', base_sha, timeout=1200)
run('fetch', '-q', '--depth=1', '--no-tags', 'upstream', head_sha, timeout=1200)
run('checkout', '-q', '-B', 'pr-head', head_sha)
run('update-ref', 'refs/remotes/origin/pr-base', base_sha)
print('HEAD', run('rev-parse', 'HEAD'))
print('BASE', run('rev-parse', 'origin/pr-base'))
print('diff stat:')
print(run('diff', '--stat', 'origin/pr-base..HEAD'))
