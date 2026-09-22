# -*- coding: utf-8 -*-
"""bulk-fetch latest bodies for inbox keeps (excl. already-triaged pendings)."""
import json, subprocess
from concurrent.futures import ThreadPoolExecutor

D = json.load(open(r'C:/Users/admin/AppData/Local/Temp/opencode/inbox61.json', encoding='utf-8'))
PEND = {'85388', '86940', '110400', '113903', '117678', '108372', '117351', '117379', '118104'}
targets = [(x['id'], x['num'].split('/')[-1], x['lcu']) for x in D
           if x['num'].split('/')[-1] not in PEND]
print('targets:', len(targets))


def sh(*a):
    r = subprocess.run(['gh', 'api'] + list(a), capture_output=True, text=True, timeout=60)
    return r.stdout


def one(t):
    tid, num, lcu = t
    if not lcu:
        try:
            pr = json.loads(sh(f'repos/NousResearch/hermes-agent/pulls/{num}') or '{}')
            return {'tid': tid, 'num': num, 'kind': 'event-only',
                    'state': pr.get('state'), 'merged': bool(pr.get('merged_at')),
                    'author': (pr.get('user') or {}).get('login'),
                    'title': (pr.get('title') or '')[:70]}
        except Exception as e:
            return {'tid': tid, 'num': num, 'kind': 'err'}
    cid = lcu.split('/')[-1]
    try:
        c = json.loads(sh(f'repos/NousResearch/hermes-agent/issues/comments/{cid}') or '{}')
        if 'user' not in c:
            lst = json.loads(sh(f'repos/NousResearch/hermes-agent/issues/{num}/comments?per_page=3') or '[]')
            c = lst[-1] if lst else {}
            if 'user' not in c:
                return {'tid': tid, 'num': num, 'kind': 'fetch-fail'}
        return {'tid': tid, 'num': num, 'kind': 'comment',
                'user': c['user']['login'], 'created': c['created_at'],
                'body': (c.get('body') or '')[:600]}
    except Exception:
        return {'tid': tid, 'num': num, 'kind': 'err'}


with ThreadPoolExecutor(max_workers=8) as ex:
    out = list(ex.map(one, targets))
json.dump(out, open(r'C:/Users/admin/AppData/Local/Temp/opencode/inbox52.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for r in out:
    if r['kind'] == 'comment':
        print(f"[{r['num']}] {r['user']} {r['created'][:16]}: {(r['body'] or '')[:110].replace(chr(10),' ')}")
    else:
        print(f"[{r['num']}] {r['kind']} {r.get('state')} merged={r.get('merged')} {r.get('title','')[:55]}")
