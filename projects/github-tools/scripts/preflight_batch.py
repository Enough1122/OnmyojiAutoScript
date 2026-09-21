# -*- coding: utf-8 -*-
"""preflight_batch.py — 批次派单前的机械预检（只读，不发帖，不改仓）。

输入 : drafts/_batch{NN}_list.json（扁平 PR 号列表，升序）
输出 : drafts/_preflight_{tag}.json
  {N: {files:[...], apply_ok: bool, apply_err: str,
       mergeable_state: str, pairs: [{n, overlap_files:[...]}]}}

三件事（都是子代理以前各自重复做的）：
  1. git apply --check：把 diff 涉及文件从只读克隆拷到临时树再 check，
     筛出"hunk 基于旧版 main"（无法合入）的 PR。
  2. mergeable_state：gh api 一次读，供"机械 rebase"快审分流。
  3. 配对预警：共享 >=1 个文件的 PR 列为疑似堆叠/互斥实现对，
     提前告诉两边，避免重复深读。

用法:
    python preflight_batch.py batch14
    python preflight_batch.py batch14 --no-mergeable   # 跳过 GitHub API（限流时）
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

REPO = 'NousResearch/hermes-agent'
CLONE = r'D:\Hermes\repos\hermes-agent-fix'


def _base_ref():
    """取最新可用的 main 引用做 pre-image 源（工作树可能停在 PR 分支上，不可信）。"""
    for ref in ('upstream/main', 'origin/main', 'main'):
        r = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', ref],
                           cwd=CLONE, capture_output=True, text=True)
        if r.returncode == 0:
            sha = subprocess.run(['git', 'rev-parse', '--short', ref],
                                 cwd=CLONE, capture_output=True, text=True).stdout.strip()
            return ref, sha
    return 'main', '?'


BASE_REF, BASE_SHA = _base_ref()


def _blob(ref, path):
    """git show <ref>:<path> 的字节内容；失败返回 None。"""
    try:
        r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)],
                           cwd=CLONE, capture_output=True, timeout=120)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None
DIFF_DIR = r'D:\Hermes\projects\github-tools\drafts\_campaign'
DRAFTS = r'D:\Hermes\projects\github-tools\drafts'


def diff_files(n):
    """从 diff 头解析涉及文件 [(old, new)]；new 为 None 表示删除。"""
    files = []
    try:
        with open(os.path.join(DIFF_DIR, '%d.diff' % n), encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^diff --git a/(.*) b/(.*)$', line.rstrip('\n'))
                if m:
                    files.append((m.group(1), m.group(2)))
    except FileNotFoundError:
        pass
    return files


def apply_check(n, files):
    """临时树 + git apply --check。返回 (ok, err)。"""
    if not files:
        return False, 'no diff file'
    tmp = tempfile.mkdtemp(prefix='preflight%d_' % n)
    try:
        for old, new in files:
            src = new if new != '/dev/null' and not new.startswith('/dev/null') else None
            # 删除文件：目标是 old；新增：clone 里没有，只需目录结构
            target = new if new != '/dev/null' else None
            if old == '/dev/null':
                target = new
            else:
                target = new
            if target is None or target == '/dev/null':
                continue
            full = os.path.join(tmp, target)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            csrc = os.path.join(CLONE, old if old != '/dev/null' else new)
            data = _blob(BASE_REF, old if old != '/dev/null' else new)
            if data is not None:
                with open(full, 'wb') as fh:
                    fh.write(data)
            elif os.path.exists(csrc) and os.path.isfile(csrc):
                shutil.copyfile(csrc, full)
        r = subprocess.run(
            ['git', 'apply', '--check',
             os.path.join(DIFF_DIR, '%d.diff' % n)],
            cwd=tmp, capture_output=True, text=True, timeout=120)
        err = (r.stderr or r.stdout or '').strip().split('\n')
        err = '; '.join(e.strip() for e in err if e.strip())[:300]
        return r.returncode == 0, err
    except Exception as e:
        return False, 'ERR ' + str(e)[:100]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mergeable(n):
    """gh api 读 mergeable_state；失败返回 'unknown'。"""
    for a in range(3):
        try:
            r = subprocess.run(
                ['gh', 'api', 'repos/%s/pulls/%d' % (REPO, n),
                 '--jq', '.mergeable_state'],
                capture_output=True, text=True, timeout=60)
            v = (r.stdout or '').strip()
            return v if v else 'unknown'
        except Exception:
            time.sleep(2 + a * 2)
    return 'unknown'


def main():
    if len(sys.argv) < 2:
        print('usage: preflight_batch.py <tag> [--no-mergeable]')
        return 2
    tag = sys.argv[1]
    do_merg = '--no-mergeable' not in sys.argv
    nums = json.load(open(os.path.join(DRAFTS, '_%s_list.json' % tag), encoding='utf-8'))
    print('preflight %s: %d PRs (base=%s @%s)' % (tag, len(nums), BASE_REF, BASE_SHA), flush=True)

    filemap = {n: diff_files(n) for n in nums}
    try:
        deferred_ns = {x.get('n') for x in
                       json.load(open(os.path.join(DRAFTS, '_campaign_state.json'),
                                      encoding='utf-8')).get('deferred', [])}
    except Exception:
        deferred_ns = set()
    results = {}
    for n in nums:
        if not filemap[n]:
            reason = 'deferred(no-diff)' if n in deferred_ns else 'no-diff??'
            results[n] = {'files': [], 'apply_ok': None, 'apply_err': reason,
                          'mergeable_state': '', 'pairs': []}
            print('  #%d %s' % (n, reason), flush=True)
            continue
        ok, err = apply_check(n, filemap[n])
        results[n] = {'files': [b for _, b in filemap[n]],
                      'apply_ok': ok, 'apply_err': err,
                      'mergeable_state': '', 'pairs': []}
        if not ok:
            print('  #%d APPLY-FAIL: %s' % (n, err[:120]), flush=True)

    if do_merg:
        def one(n):
            time.sleep(0.2)
            return n, mergeable(n)
        with ThreadPoolExecutor(max_workers=4) as ex:
            for n, v in ex.map(one, nums):
                results[n]['mergeable_state'] = v
                if v in ('dirty', 'blocked'):
                    pass
        print('  mergeable states collected', flush=True)

    # 配对：共享 >=1 个文件（排除纯测试文件也可配对，但先全量报）
    by_file = {}
    for n in nums:
        for f in results[n]['files']:
            by_file.setdefault(f, []).append(n)
    for n in nums:
        seen = {}
        for f in results[n]['files']:
            for m in by_file[f]:
                if m != n:
                    seen.setdefault(m, []).append(f)
        results[n]['pairs'] = [{'n': m, 'overlap_files': fs}
                               for m, fs in sorted(seen.items())]
        if seen:
            print('  #%d pairs with %s' % (n, sorted(seen)), flush=True)

    out = os.path.join(DRAFTS, '_preflight_%s.json' % tag)
    json.dump({'tag': tag, 'results': results},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n_fail = sum(1 for n in nums if not results[n]['apply_ok'])
    n_pair = sum(1 for n in nums if results[n]['pairs'])
    print('wrote %s | apply-fail=%d paired=%d' % (out, n_fail, n_pair))


if __name__ == '__main__':
    main()
