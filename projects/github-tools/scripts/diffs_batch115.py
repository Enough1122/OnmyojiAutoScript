# -*- coding: utf-8 -*-
"""diffs_batch115.py — fetch diffs for the 100-PR batch starting at frontier 115076.

Input : drafts/_batch115_list.json (flat list of PR numbers, ascending)
Output: drafts/_campaign/{N}.diff  +  drafts/_batch115_final.json (numbers that passed)
Gate  : diff >= 100000B -> OVER (recorded, not fetched twice)
"""
import json, os, time
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
OUT = r'D:\Hermes\projects\github-tools\drafts\_campaign'
LIMIT = 100000

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8')
       if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github.v3.diff',
     'Authorization': 'Bearer ' + tok}

import sys
LIST = sys.argv[1] if len(sys.argv) > 1 else r'D:\Hermes\projects\github-tools\drafts\_batch115_list.json'
FINAL = sys.argv[2] if len(sys.argv) > 2 else r'D:\Hermes\projects\github-tools\drafts\_batch115_final.json'
nums = json.load(open(LIST, encoding='utf-8'))
os.makedirs(OUT, exist_ok=True)
print('batch:', len(nums), nums[0], '..', nums[-1], flush=True)


def fetch(n):
    p = os.path.join(OUT, '%d.diff' % n)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return n, os.path.getsize(p), 'cached'
    for a in range(3):
        try:
            d = urlopen(Request('%s/repos/%s/pulls/%d' % (BASE, REPO, n), headers=H), timeout=60).read()
            if len(d) >= LIMIT:
                return n, len(d), 'OVER'
            open(p, 'wb').write(d)
            return n, len(d), 'ok'
        except Exception as ex:
            if a == 2:
                return n, -1, 'ERR ' + str(ex)[:60]
            time.sleep(2 + a * 2)


t0 = time.time()
res = []
with ThreadPoolExecutor(max_workers=10) as ex:
    for i, r in enumerate(ex.map(fetch, nums), 1):
        res.append(r)
        if i % 25 == 0:
            print('  ...%d/%d %.0fs' % (i, len(nums), time.time() - t0), flush=True)

good = [r for r in res if r[2] in ('ok', 'cached')]
over = [r for r in res if r[2] == 'OVER']
err = [r for r in res if r[2].startswith('ERR')]
print('OK: %d | OVER 100KB: %d | ERR: %d | %.0fs' % (len(good), len(over), len(err), time.time() - t0))
print('over:', sorted(r[0] for r in over))
print('err:', sorted((r[0], r[2]) for r in err))

final = sorted(r[0] for r in good)
json.dump(final, open(FINAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('FINAL ready:', len(final))
