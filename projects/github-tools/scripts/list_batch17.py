# -*- coding: utf-8 -*-
"""列出 frontier 之后仍 open 的候选 PR（只读）。输出 drafts/_batch17_list.json"""
import json, subprocess, os
from concurrent.futures import ThreadPoolExecutor

FRONTIER = 117738
REPO = 'NousResearch/hermes-agent'
OUT = r'D:\Hermes\projects\github-tools\drafts\_batch17_list.json'
META = r'D:\Hermes\projects\github-tools\drafts\_batch17_meta.json'

def gh(*args):
    r = subprocess.run(['gh', 'api'] + list(args), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:200])
    return json.loads(r.stdout or '{}')

# 1. 取 frontier 之后创建的全部 PR 编号（分页）
nums = []
page = 1
while True:
    d = gh(f'search/issues?q=repo:{REPO}+type:pr+created:>2026-09-21T00:30:00Z&per_page=100&page={page}')
    for it in d.get('items', []):
        if it['number'] > FRONTIER:
            nums.append(it['number'])
    total = d.get('total_count', 0)
    if len(d.get('items', [])) < 100 or page * 100 >= total:
        break
    page += 1
nums = sorted(set(nums))
print('candidates > frontier:', len(nums), 'range %d..%d' % (min(nums), max(nums)))

# 2. 逐个查状态/作者/draft/评论数
def one(n):
    try:
        p = gh(f'repos/{REPO}/pulls/{n}')
        return n, {'state': p.get('state'), 'draft': p.get('draft'),
                   'author': (p.get('user') or {}).get('login'),
                   'title': (p.get('title') or '')[:80],
                   'comments': p.get('comments', 0),
                   'review_comments': p.get('review_comments', 0),
                   'add': p.get('additions', 0), 'del': p.get('deletions', 0),
                   'files': p.get('changed_files', 0)}
    except Exception as e:
        return n, {'err': str(e)[:100]}

meta = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for n, m in ex.map(one, nums):
        meta[n] = m

elig = [n for n in nums if (lambda m: m.get('state') == 'open' and not m.get('draft')
        and m.get('author') != 'Enough1122'
        and m.get('comments', 0) == 0 and m.get('review_comments', 0) == 0
        and 'err' not in m)(meta[n])]
# 有 review 的需要再查（pulls 列表不带 reviews 数）→ 留给 post_one 的 liveness 复检 + 起草前复查
print('open+non-draft+non-own+zero-comments:', len(elig))
from collections import Counter
print('non-elig reasons:', Counter(
    ('closed' if meta[n].get('state') != 'open' else
     'draft' if meta[n].get('draft') else
     'own' if meta[n].get('author') == 'Enough1122' else
     'has-comments' if (meta[n].get('comments', 0) + meta[n].get('review_comments', 0)) > 0 else
     'err')
    for n in nums if n not in elig))

json.dump(elig, open(OUT, 'w'), indent=1)
json.dump({str(k): v for k, v in meta.items()}, open(META, 'w', ensure_ascii=False), indent=1)
print('wrote', OUT)
