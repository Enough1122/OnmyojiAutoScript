# -*- coding: utf-8 -*-
"""collect_verdicts.py — 合并子代理的 verdict JSON，产出状态种子 + 待发清单。

子代理不再靠聊天框汇报：每个 chunk 完工写
    drafts/_verdict_{tag}_{chunk}.json
格式：
    {"chunk": "chunk1",
     "verdicts": [{"n": 115078, "v": "CLEAN|DRAFT|SKIP_STALE",
                   "level": "blocker|nonblocking|null",
                   "note": "一句话发现",
                   "evidence": "file:line 证据（blocker 必填）"}, ...]}
其中 v=DRAFT 表示写了草稿（Temp/opencode/campaign/{N}.md），
SKIP_STALE 需在 note 写原因。

本脚本：
  1. 合并全部 verdict 文件，检查 10 行齐全（缺数即报错）。
  2. 校验：DRAFT 的草稿文件存在且首行是规定声明；
     草稿谈到的主文件在 diff 头里出现（防 116701 式错配——只做文件名级
     检查，深层语义仍靠主流程/核验）。
  3. 输出 drafts/_{tag}_collect.json（含 posted/clean/skip 初判 +
     blocker 清单 + 待核验清单），并打印汇总。

v 值映射到归档状态：DRAFT→待发（主流程发帖后记 posted）、
CLEAN→clean、SKIP_STALE→skip。

用法:
    python collect_verdicts.py batch14 3     # 期待 3 个 chunk 文件
    python collect_verdicts.py batch14       # 有几个算几个
"""
import glob
import json
import os
import re
import sys

DRAFTS = r'D:\Hermes\projects\github-tools\drafts\_campaign'
DD = r'D:\Hermes\projects\github-tools\drafts'
MD_DIR = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
HEADER = '> AI code review'


def diff_files(n):
    files = set()
    try:
        with open(os.path.join(DRAFTS, '%d.diff' % n), encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^diff --git a/(.*) b/(.*)$', line.rstrip('\n'))
                if m:
                    files.add(m.group(1))
                    files.add(m.group(2))
    except FileNotFoundError:
        pass
    return {os.path.basename(x) for x in files}


def main():
    if len(sys.argv) < 2:
        print('usage: collect_verdicts.py <tag> [expect_chunks]')
        return 2
    tag = sys.argv[1]
    expect = int(sys.argv[2]) if len(sys.argv) > 2 else None
    pats = sorted(glob.glob(os.path.join(
        DD, '_verdict_%s_*.json' % tag)))
    print('verdict files: %d %s' % (len(pats), [os.path.basename(p) for p in pats]))
    if expect and len(pats) < expect:
        print('WAIT: expect %d chunks, only %d arrived' % (expect, len(pats)))
        return 1

    verdicts = {}
    for p in pats:
        d = json.load(open(p, encoding='utf-8'))
        for v in d.get('verdicts', []):
            verdicts[int(v['n'])] = v

    batch = json.load(open(os.path.join(DD, '_%s_list.json' % tag), encoding='utf-8'))
    missing = [n for n in batch if n not in verdicts]
    if missing:
        print('WAIT: missing verdicts for %s' % missing)
        return 1

    problems, blockers, drafts_nb, clean, skip = [], [], [], [], []
    for n in sorted(verdicts):
        v = verdicts[n]
        vv = v.get('v')
        if vv == 'CLEAN':
            clean.append(n)
        elif vv == 'SKIP_STALE':
            skip.append(n)
        elif vv == 'DRAFT':
            lvl = v.get('level')
            mp = os.path.join(MD_DIR, '%d.md' % n)
            if not os.path.exists(mp):
                problems.append('#%d DRAFT but no draft file' % n)
                continue
            head = open(mp, encoding='utf-8').read(120)
            if HEADER not in head:
                problems.append('#%d draft missing header' % n)
            # 错配粗筛：草稿里形如 path/to/file.py:123 的引用，
            # 至少一个 basename 要出现在 diff 头里
            refs = {os.path.basename(x) for x in
                    re.findall(r'[a-zA-Z0-9_./-]+\.(?:py|ts|tsx|js|go|rs|yaml|yml|toml|md):\d+', open(mp, encoding='utf-8').read())}
            df = diff_files(n)
            if refs and df and not (refs & df):
                problems.append('#%d MISMATCH? draft refs %s not in diff files %s'
                                % (n, sorted(refs)[:4], sorted(df)[:6]))
            if lvl == 'blocker':
                if not v.get('evidence'):
                    problems.append('#%d blocker without evidence' % n)
                blockers.append(n)
            else:
                drafts_nb.append(n)
        else:
            problems.append('#%d unknown verdict %r' % (n, vv))

    seed = {}
    for n in clean:
        seed[str(n)] = 'clean'
    for n in skip:
        seed[str(n)] = 'skip'
    for n in blockers + drafts_nb:
        seed[str(n)] = 'pending-verify'
    out = os.path.join(DD, '_%s_collect.json' % tag)
    json.dump({'tag': tag, 'seed': seed, 'blockers': blockers,
               'drafts_nb': drafts_nb, 'clean': clean, 'skip': skip,
               'problems': problems},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('clean=%d skip=%d blockers=%d drafts_nb=%d' % (len(clean), len(skip), len(blockers), len(drafts_nb)))
    print('blockers:', blockers)
    if problems:
        print('PROBLEMS:')
        for p in problems:
            print('  !', p)
    print('wrote ' + out)


if __name__ == '__main__':
    main()
