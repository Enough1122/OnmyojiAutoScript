# -*- coding: utf-8 -*-
"""sweep_posted13.py — authoritative API check for batch-48 (87 candidates in
drafts/_continue13_final.json). Writes drafts/_sweep13_posted.json (numbers with >=1
AI-header comment) and reports dup counts (numbers with >1, needing DELETE)."""
import json, time, urllib.request
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
REPO = 'NousResearch/hermes-agent'
ME = 'Enough1122'
HEADER = '> AI code review'

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok}

nums = json.load(open(r'D:\Hermes\projects\github-tools\drafts\_continue13_final.json', encoding='utf-8'))


def chk(n):
    for a in range(3):
        try:
            cs = json.loads(urlopen(Request('https://api.github.com/repos/%s/issues/%d/comments?per_page=100' % (REPO, n), headers=H), timeout=30).read())
            mine = [c for c in cs if (c.get('user') or {}).get('login') == ME and HEADER in (c.get('body') or '')]
            return {'n': n, 'cnt': len(mine), 'ids': [c['id'] for c in mine]}
        except Exception as e:
            if a == 2:
                return {'n': n, 'err': str(e)[:70]}
            time.sleep(2 + a * 2)


res = []
with ThreadPoolExecutor(max_workers=14) as ex:
    for i, r in enumerate(ex.map(chk, nums), 1):
        res.append(r)
        if i % 100 == 0:
            print('...%d/%d' % (i, len(nums)), flush=True)

posted1 = sorted(r['n'] for r in res if not r.get('err') and r['cnt'] >= 1)
dup = [(r['n'], r['cnt'], r['ids']) for r in res if not r.get('err') and r['cnt'] > 1]
errs = [r for r in res if r.get('err')]
print('POSTED(>=1):', len(posted1), '| DUP(>1):', len(dup), '| ERR:', len(errs))
print('dups:', dup[:20])
json.dump(posted1, open(r'D:\Hermes\projects\github-tools\drafts\_sweep13_posted.json', 'w', encoding='utf-8'), indent=0)
json.dump({'dups': dup, 'errs': errs}, open(r'D:\Hermes\projects\github-tools\drafts\_sweep13_dups.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
