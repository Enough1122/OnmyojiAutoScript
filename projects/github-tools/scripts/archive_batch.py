# -*- coding: utf-8 -*-
"""archive_batch.py — 归档本批状态并落盘断点。

输入: drafts/_batch115_status.json  {"<PR号>": "posted"|"clean"|"skip", ...}
动作:
  1. posted 的草稿 (Temp/opencode/campaign/{N}.md) 复制到 reviews/hermes-agent-2026W38/rb/{N}.md
  2. progress.txt 追加 "{N}\tposted|silent|skip"  (只追加尚未记录的编号)
  3. _campaign_state.json: posted / reviewed_clean 追加, frontier = max(已处理编号)
用法: python archive_batch.py [--dry-run]
"""
import json, os, shutil, sys

STATUS = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else r'D:\Hermes\projects\github-tools\drafts\_batch115_status.json'
BATCH_LIST = sys.argv[2] if len(sys.argv) > 2 else r'D:\Hermes\projects\github-tools\drafts\_batch115_list.json'
DRAFT = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
RB = r'D:\Hermes\reviews\hermes-agent-2026W38\rb'
PROG = r'D:\Hermes\reviews\hermes-agent-2026W38\progress.txt'
STATE = r'D:\Hermes\projects\github-tools\drafts\_campaign_state.json'

MAP = {'posted': 'posted', 'clean': 'silent', 'skip': 'skip', 'deferred': 'deferred'}
dry = '--dry-run' in sys.argv

st = json.load(open(STATUS, encoding='utf-8'))
items = sorted((int(k), v) for k, v in st.items())
print('status entries: %d (posted=%d clean=%d skip=%d)'
      % (len(items), sum(1 for _, v in items if v == 'posted'),
         sum(1 for _, v in items if v == 'clean'),
         sum(1 for _, v in items if v == 'skip')))

done = set()
for line in open(PROG, encoding='utf-8'):
    p = line.split('\t')
    if p and p[0].strip().isdigit():
        done.add(int(p[0]))

copied, appended = [], []
for n, v in items:
    if v == 'posted':
        src = os.path.join(DRAFT, '%d.md' % n)
        dst = os.path.join(RB, '%d.md' % n)
        if os.path.exists(src) and not os.path.exists(dst):
            if not dry:
                shutil.copyfile(src, dst)
            copied.append(n)
    if n not in done:
        appended.append((n, MAP[v]))

if not dry:
    with open(PROG, 'a', encoding='utf-8') as f:
        for n, s in appended:
            f.write('%d\t%s\n' % (n, s))

    cst = json.load(open(STATE, encoding='utf-8'))
    posted = cst.setdefault('posted', [])
    clean = cst.setdefault('reviewed_clean', [])
    for n, v in items:
        if v == 'posted' and n not in posted:
            posted.append(n)
        elif v == 'clean' and n not in clean:
            clean.append(n)
    # frontier 只在"批次内已记录的编号构成连续前缀"时前进，避免批次未跑完就跳过中间编号
    rec = {n for n, _ in items}
    batch = json.load(open(BATCH_LIST, encoding='utf-8'))
    f_new = cst.get('frontier', 0)
    for b in sorted(batch):
        if b in rec:
            f_new = max(f_new, b)
        else:
            break
    cst['frontier'] = f_new
    cst['posted_count'] = len(posted)
    json.dump(cst, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('rb copies: %d %s' % (len(copied), copied if len(copied) < 15 else ''))
print('progress appended: %d' % len(appended))
print('frontier now: %s' % (max(n for n, _ in items) if items else 'n/a'))
