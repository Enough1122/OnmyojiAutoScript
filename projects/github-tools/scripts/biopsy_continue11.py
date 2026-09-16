# -*- coding: utf-8 -*-
"""biopsy_continue11.py — SOP live-verification for window candidates.

For each candidate: GET /pulls/{n} + /issues/{n}/comments + /pulls/{n}/reviews
must ALL be zero-comment / zero-review / open / non-draft, changed_files<=8.
Writes drafts/_continue11_ok.json (eligible) and _continue11_skip.json.
"""
import json, time, urllib.request, sys
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok}

cand = json.load(open(r'D:\Hermes\projects\github-tools\drafts\_continue11_raw.json', encoding='utf-8'))
print('candidates:', len(cand), flush=True)

state = json.load(open(r'D:\Hermes\projects\github-tools\drafts\_campaign_state.json', encoding='utf-8'))
posted = set(state['posted'])


def g(url, retry=3):
    for a in range(retry):
        try:
            return json.loads(urlopen(Request(url, headers=H), timeout=30).read())
        except Exception as e:
            if a == retry - 1:
                return {'__error__': str(e)[:90]}
            time.sleep(1.5 + a * 2)


def biopsy(c):
    n = c['number']
    if n in posted:
        return {'number': n, 'ok': False, 'reason': 'already posted'}
    pr = g('%s/repos/%s/pulls/%d' % (BASE, REPO, n))
    if isinstance(pr, dict) and '__error__' in pr:
        return {'number': n, 'ok': False, 'reason': 'pulls err ' + pr['__error__']}
    if pr.get('state') != 'open':
        return {'number': n, 'ok': False, 'reason': 'state=' + str(pr.get('state'))}
    if pr.get('draft'):
        return {'number': n, 'ok': False, 'reason': 'draft'}
    cf = pr.get('changed_files')
    if cf is None or cf > 8:
        return {'number': n, 'ok': False, 'reason': 'changed_files=%s' % cf}

    cm = g('%s/repos/%s/issues/%d/comments?per_page=100' % (BASE, REPO, n))
    if isinstance(cm, dict) and '__error__' in cm:
        return {'number': n, 'ok': False, 'reason': 'comments err ' + cm['__error__']}
    if len(cm):
        return {'number': n, 'ok': False, 'reason': 'comments=%d' % len(cm)}

    rv = g('%s/repos/%s/pulls/%d/reviews?per_page=100' % (BASE, REPO, n))
    if isinstance(rv, dict) and '__error__' in rv:
        return {'number': n, 'ok': False, 'reason': 'reviews err ' + rv['__error__']}
    if len(rv):
        return {'number': n, 'ok': False, 'reason': 'reviews=%d' % len(rv)}

    return {
        'number': n, 'ok': True, 'title': pr.get('title'),
        'user': (pr.get('user') or {}).get('login'),
        'changed_files': cf,
        'additions': pr.get('additions'), 'deletions': pr.get('deletions'),
        'created_at': pr.get('created_at'),
        'head_sha': (pr.get('head') or {}).get('sha'),
        'html_url': pr.get('html_url'),
    }


t0 = time.time()
res = []
with ThreadPoolExecutor(max_workers=14) as ex:
    for i, r in enumerate(ex.map(biopsy, cand), 1):
        res.append(r)
        if i % 50 == 0:
            print('  ...%d/%d  ok=%d  %.0fs' % (i, len(cand),
                  sum(1 for x in res if x['ok']), time.time() - t0), flush=True)

ok = sorted([r for r in res if r['ok']], key=lambda x: x['number'])
bad = [r for r in res if not r['ok']]
print('ELIGIBLE:', len(ok), '| SKIPPED:', len(bad), '| %.0fs' % (time.time() - t0))

from collections import Counter
print('skip reasons:', dict(Counter(r['reason'].split('=')[0] for r in bad)))

json.dump(ok, open(r'D:\Hermes\projects\github-tools\drafts\_continue11_ok.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(bad, open(r'D:\Hermes\projects\github-tools\drafts\_continue11_skip.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('numbers:', [r['number'] for r in ok])
