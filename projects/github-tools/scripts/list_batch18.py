# -*- coding: utf-8 -*-
"""列出 batch18 候选（118152 之后的新 PR，只读）。输出 drafts/_batch18_list.json"""
import json
from concurrent.futures import ThreadPoolExecutor
import subprocess

REPO = 'NousResearch/hermes-agent'
OUT = r'D:\Hermes\projects\github-tools\drafts\_batch18_list.json'

CANDS = [118143, 118160, 118162, 118163, 118164, 118166, 118167, 118168,
         118169, 118170, 118171, 118172, 118173, 118174, 118177, 118179,
         118180, 118183, 118184, 118185, 118186, 118188, 118190, 118191,
         118192, 118193, 118195, 118197, 118198, 118199, 118200, 118201,
         118202, 118204, 118205, 118206, 118207, 118209, 118210, 118211,
         118212, 118213, 118215, 118217, 118221, 118222, 118223, 118224,
         118225]


def one(n):
    try:
        r = subprocess.run(['gh', 'api', f'repos/{REPO}/pulls/{n}'],
                           capture_output=True, text=True, timeout=60)
        p = json.loads(r.stdout or '{}')
        return n, {'state': p.get('state'), 'draft': p.get('draft'),
                   'author': (p.get('user') or {}).get('login'),
                   'title': (p.get('title') or '')[:80],
                   'comments': p.get('comments', 0),
                   'review_comments': p.get('review_comments', 0)}
    except Exception as e:
        return n, {'err': str(e)[:100]}


meta = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for n, m in ex.map(one, CANDS):
        meta[n] = m

elig = [n for n in CANDS if (lambda m: m.get('state') == 'open' and not m.get('draft')
        and m.get('author') != 'Enough1122'
        and m.get('comments', 0) == 0 and m.get('review_comments', 0) == 0
        and 'err' not in m)(meta[n])]
print('candidates:', len(CANDS), '| eligible:', len(elig))
from collections import Counter
print('non-elig:', Counter(
    ('closed' if meta[n].get('state') != 'open' else
     'draft' if meta[n].get('draft') else
     'own' if meta[n].get('author') == 'Enough1122' else
     'has-comments' if (meta[n].get('comments', 0) + meta[n].get('review_comments', 0)) > 0 else
     'err')
    for n in CANDS if n not in elig))
for n in CANDS:
    if n not in elig:
        print('  skip', n, meta[n].get('state'), 'draft=' + str(meta[n].get('draft')),
              meta[n].get('author'), (meta[n].get('title') or '')[:60])
json.dump(elig, open(OUT, 'w'), indent=1)
print('wrote', OUT)
