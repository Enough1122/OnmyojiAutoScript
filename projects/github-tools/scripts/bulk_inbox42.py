# -*- coding: utf-8 -*-
"""bulk-fetch latest bodies for the 42 non-pending inbox threads."""
import json, subprocess
from concurrent.futures import ThreadPoolExecutor

D = json.load(open(r'C:/Users/admin/AppData/Local/Temp/opencode/inbox47.json', encoding='utf-8'))
PEND = {'86940', '117678', '85388', '110400', '113903'}
targets = [(x['id'], x['num'].split('/')[-1], x['lcu']) for x in D
           if x['num'].split('/')[-1] not in PEND]


def sh(*a):
    r = subprocess.run(['gh', 'api'] + list(a), capture_output=True, text=True, timeout=60)
    return r.stdout


def one(t):
    tid, num, lcu = t
    if not lcu or lcu == 'NO-LCU':
        pr = json.loads(sh(f'repos/NousResearch/hermes-agent/pulls/{num}') or '{}')
        return {'tid': tid, 'num': num, 'kind': 'event-only',
                'state': pr.get('state'), 'merged': bool(pr.get('merged_at')),
                'title': (pr.get('title') or '')[:70]}
    cid = lcu.split('/')[-1]
    try:
        c = json.loads(sh(f'repos/NousResearch/hermes-agent/issues/comments/{cid}') or '{}')
        if 'user' not in c:
            return {'tid': tid, 'num': num, 'kind': 'fetch-fail'}
        return {'tid': tid, 'num': num, 'kind': 'comment',
                'user': c['user']['login'], 'created': c['created_at'],
                'body': (c.get('body') or '')[:700]}
    except Exception as e:
        return {'tid': tid, 'num': num, 'kind': 'err', 'e': str(e)[:80]}


with ThreadPoolExecutor(max_workers=8) as ex:
    out = list(ex.map(one, targets))
json.dump(out, open(r'C:/Users/admin/AppData/Local/Temp/opencode/inbox42.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('saved', len(out))
for r in out:
    if r['kind'] == 'comment':
        print(f"[{r['num']}] {r['user']} {r['created'][:16]}: {(r['body'] or '')[:120].replace(chr(10),' ')}")
    else:
        print(f"[{r['num']}] {r['kind']} {r.get('state')} merged={r.get('merged')} {r.get('title','')[:60]}")
