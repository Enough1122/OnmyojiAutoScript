# -*- coding: utf-8 -*-
"""scan_window_99385.py — pull review candidates for window 99385-100453.

SOP filter (search level): is:pr is:open comments:0, sharded by created date.
Dedupes against drafts/_campaign_state.json posted[] and any number < WINDOW_MIN.
Writes drafts/_continue11_raw.json
"""
import json, time, urllib.request
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
WINDOW_MIN = 99385
WINDOW_MAX = 100453

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok}


def g(url, retry=4):
    for a in range(retry):
        try:
            r = urlopen(Request(url, headers=H), timeout=30)
            return json.loads(r.read()), r.headers.get('Link', '')
        except Exception as e:
            if a == retry - 1:
                print('  ERR', str(e)[:80])
                return None, ''
            time.sleep(3 + a * 3)
    return None, ''


SHARDS = [
    ('2026-08-31T12:00:00Z', '2026-08-31T18:00:00Z'),
    ('2026-08-31T18:00:00Z', '2026-09-01T00:00:00Z'),
    ('2026-09-01T00:00:00Z', '2026-09-01T06:00:00Z'),
    ('2026-09-01T06:00:00Z', '2026-09-01T12:00:00Z'),
    ('2026-09-01T12:00:00Z', '2026-09-01T15:35:00Z'),
]

state = json.load(open(r'D:\Hermes\projects\github-tools\drafts\_campaign_state.json', encoding='utf-8'))
posted = set(state['posted'])
print('already posted:', len(posted))

raw = {}
for (s, e) in SHARDS:
    page = 1
    while True:
        q = ('%s/search/issues?q=repo:%s+is:pr+is:open+comments:0+created:%s..%s'
             '&per_page=100&page=%d&sort=created&order=asc' % (BASE, REPO, s, e, page))
        d, _ = g(q)
        if d is None:
            break
        items = d.get('items', [])
        for it in items:
            raw[it['number']] = {
                'number': it['number'], 'title': it['title'],
                'created_at': it['created_at'], 'user': (it.get('user') or {}).get('login'),
                'html_url': it['html_url'],
            }
        print('shard %s..%s page %d -> %d (total %d, cum %d)' % (s[:16], e[:16], page, len(items), d.get('total_count'), len(raw)))
        time.sleep(2.5)
        if len(items) < 100 or page >= 10:
            break
        page += 1

# window filter + dedupe
cand = []
for n in sorted(raw):
    if n < WINDOW_MIN or n > WINDOW_MAX:
        continue
    if n in posted:
        continue
    cand.append(raw[n])

print('raw searched:', len(raw), '| in window:', sum(1 for n in raw if WINDOW_MIN <= n <= WINDOW_MAX),
      '| new candidates after dedupe:', len(cand))

out = r'D:\Hermes\projects\github-tools\drafts\_continue11_raw.json'
json.dump(cand, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved:', out)
