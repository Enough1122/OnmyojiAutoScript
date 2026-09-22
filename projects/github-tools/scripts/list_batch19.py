# -*- coding: utf-8 -*-
"""列出 batch19 候选（frontier #118225 之后的新 PR，只读）。输出 drafts/_batch19_list.json"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

FRONTIER = 118225
REPO = 'NousResearch/hermes-agent'
OUT = r'D:\Hermes\projects\github-tools\drafts\_batch19_list.json'


def gh(*args):
    r = subprocess.run(['gh', 'api'] + list(args), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:200])
    return json.loads(r.stdout or '{}')


# 1. 分页拉 created 倒序的 PR，取编号 > FRONTIER 的（多翻几页兜底）+ 全量编号区间枚举
nums = set()
for page in (1, 2, 3, 4, 5, 6):
    d = gh(f'search/issues?q=repo:{REPO}+type:pr+sort:created&order=desc&per_page=100&page={page}')
    items = d.get('items', [])
    for it in items:
        if it['number'] > FRONTIER:
            nums.add(it['number'])
    if len(items) < 100:
        break
print('from search:', len(nums))
top = max(nums)
# 全量区间枚举 118226..top（农场日增数百，search 分页会漏中间号段）
print('enumerating range %d..%d' % (FRONTIER + 1, top))
# 兜底：上界往上扫（新 PR 编号连续，找到连续 30 个 404/不存在即停）
top = max(nums)
cur = top + 1
miss = 0
while miss < 30 and cur < top + 400:
    try:
        p = gh(f'repos/{REPO}/pulls/{cur}')
        if p.get('number') == cur:
            nums.add(cur)
            miss = 0
        else:
            miss += 1
    except Exception:
        miss += 1
    cur += 1
nums = sorted(nums)
print('candidates > frontier:', len(nums), 'range %d..%d' % (min(nums), max(nums)))


def one(n):
    try:
        p = gh(f'repos/{REPO}/pulls/{n}')
        return n, {'state': p.get('state'), 'draft': p.get('draft'),
                   'author': (p.get('user') or {}).get('login'),
                   'title': (p.get('title') or '')[:80],
                   'comments': p.get('comments', 0),
                   'review_comments': p.get('review_comments', 0)}
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
print('eligible:', len(elig))
from collections import Counter
print('non-elig:', Counter(
    ('closed' if meta[n].get('state') != 'open' else
     'draft' if meta[n].get('draft') else
     'own' if meta[n].get('author') == 'Enough1122' else
     'has-comments' if (meta[n].get('comments', 0) + meta[n].get('review_comments', 0)) > 0 else
     'err')
    for n in nums if n not in elig))
json.dump(elig, open(OUT, 'w'), indent=1)
print('wrote', OUT)
