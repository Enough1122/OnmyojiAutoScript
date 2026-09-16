# -*- coding: utf-8 -*-
"""diffs_continue11.py — fetch diffs for eligible candidates, enforce <60000B."""
import json, time, os, urllib.request
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
OUT = r'D:\Hermes\projects\github-tools\drafts\_campaign'
LIMIT = 60000

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github.v3.diff', 'Authorization': 'Bearer ' + tok}

ok = json.load(open(r'D:\Hermes\projects\github-tools\drafts\_continue11_ok.json', encoding='utf-8'))
os.makedirs(OUT, exist_ok=True)
print('eligible:', len(ok), flush=True)


def fetch(e):
    n = e['number']
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
    for i, r in enumerate(ex.map(fetch, ok), 1):
        res.append(r)
        if i % 50 == 0:
            print('  ...%d/%d %.0fs' % (i, len(ok), time.time() - t0), flush=True)

good = [r for r in res if r[2] in ('ok', 'cached')]
over = [r for r in res if r[2] == 'OVER']
err = [r for r in res if r[2].startswith('ERR')]
print('OK:', len(good), '| OVER 60KB:', len(over), '| ERR:', len(err), '| %.0fs' % (time.time() - t0))
print('over:', sorted(r[0] for r in over))
print('err:', sorted(r[0] for r in err))

final = sorted(r[0] for r in good)
json.dump(final, open(r'D:\Hermes\projects\github-tools\drafts\_continue11_final.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('FINAL ready:', len(final))
