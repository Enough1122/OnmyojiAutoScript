# -*- coding: utf-8 -*-
"""gh_inbox_triage.py - pull ALL unread notifications, resolve PR context concurrently,
classify each item for inbox processing. Writes drafts/_inbox_triage.json + prints TSV."""
import json, time, urllib.request
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
ME = 'Enough1122'
BASE = 'https://api.github.com'

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
HDRS = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok}

def g(url):
    req = Request(url, headers=HDRS)
    for attempt in range(3):
        try:
            return json.loads(urlopen(req, timeout=25).read())
        except Exception as e:
            if attempt == 2:
                return {'__error__': str(e)}
            time.sleep(1 + attempt)

def g_all(url):
    out = []
    while url:
        req = Request(url, headers=HDRS)
        resp = urlopen(req, timeout=30)
        out.extend(json.loads(resp.read()))
        link = resp.headers.get('Link', '')
        url = None
        for part in link.split(','):
            if 'rel="next"' in part:
                url = part[part.index('<')+1:part.index('>')]
    return out

notifs = g_all(BASE + '/notifications?per_page=100&all=false')
print('fetched %d unread notifications' % len(notifs), flush=True)

pr_urls = {}
for n in notifs:
    u = n['subject'].get('url') or ''
    if '/pulls/' in u:
        pr_urls[u] = None

def resolve_pr(url):
    d = g(url)
    if isinstance(d, dict) and '__error__' in d:
        return url, {'error': d['__error__']}
    return url, {
        'number': d.get('number'), 'state': d.get('state'),
        'merged': d.get('merged', False),
        'user': (d.get('user') or {}).get('login'),
        'head_ref': ((d.get('head') or {}).get('ref')),
    }

with ThreadPoolExecutor(max_workers=12) as ex:
    for url, info in ex.map(resolve_pr, list(pr_urls.keys())):
        pr_urls[url] = info

def latest_comment(lcu):
    if not lcu:
        return None
    d = g(lcu)
    if isinstance(d, dict) and '__error__' in d:
        return {'error': d['__error__']}
    if isinstance(d, list):
        d = d[-1] if d else {}
    return {
        'user': (d.get('user') or {}).get('login'),
        'created_at': d.get('created_at'),
        'body': (d.get('body') or '')[:300],
    }

def lc_of(lcu):
    with ThreadPoolExecutor(max_workers=16) as ex:
        return dict(zip(lcu, ex.map(latest_comment, lcu)))

lcus = [n['subject'].get('latest_comment_url') for n in notifs if n['reason'] in ('comment','mention','author')]
lcs = lc_of([u for u in lcus if u])

rows = []
for n in notifs:
    s = n['subject']
    su = s.get('url') or ''
    pr = pr_urls.get(su) or {}
    row = {
        'id': n['id'], 'reason': n['reason'],
        'type': s['type'], 'repo': n['repository']['full_name'],
        'title': s['title'], 'url': su,
        'html': su.replace('api.github.com/repos', 'github.com').replace('/pulls/', '/pull/'),
        'pr_user': pr.get('user'), 'pr_state': ('merged' if pr.get('merged') else pr.get('state')),
        'ours': (pr.get('user') == ME),
        'head_ref': pr.get('head_ref'),
        'latest_comment': lcs.get(s.get('latest_comment_url')),
        'updated_at': n['updated_at'],
    }
    if isinstance(row['latest_comment'], dict):
        row['lc_bot'] = bool((row['latest_comment'].get('user') or '').endswith('[bot]'))
    rows.append(row)

out = r'D:\Hermes\projects\github-tools\drafts\_inbox_triage.json'
import io
with open(out, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

from collections import Counter
print('by reason:', dict(Counter(r['reason'] for r in rows)))
print('by repo:', dict(Counter(r['repo'] for r in rows)))
print('ours:', sum(1 for r in rows if r['ours']), '| theirs:', sum(1 for r in rows if not r['ours']))
print('saved:', out)
print()
print('ID\tREASON\tOURS\tSTATE\tPR_USER\tLC_USER\tBOT\tREPO\tTITLE')
for r0 in rows:
    lc = r0.get('latest_comment') or {}
    print('\t'.join([
        r0['id'], r0['reason'], str(r0['ours']), str(r0['pr_state']),
        str(r0['pr_user']), str(lc.get('user')), str(r0.get('lc_bot')),
        r0['repo'], r0['title'][:80].replace('\t', ' ').replace('\n', ' '),
    ]))
