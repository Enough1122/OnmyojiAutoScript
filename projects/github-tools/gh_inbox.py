import json, urllib.request
from urllib.request import Request, urlopen

TOK = open(r'C:\Users\admin\AppData\Local\hermes\.env', 'r', encoding='utf-8').read()
gh = [l.split('=', 1)[1].strip() for l in TOK.splitlines() if l.startswith('GITHUB_TOKEN=')][0]
hdrs = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {gh}'}

def g(u):
    return json.loads(urlopen(Request(u, headers=hdrs), timeout=20).read())

base = 'https://api.github.com'
d = g(base + '/notifications?per_page=100')
print(f'total notifications in inbox: {len(d)}')
print('=' * 100)
for n in d:
    t = n['subject']
    print(f"[{'UNREAD' if n['unread'] else 'read'}] {t['type']:<12} reason={n['reason']:<10} {n['updated_at'][:16]}")
    print(f"   {n['repository']['full_name']} | {t['title'][:95]}")
    print(f"   url: {t.get('url')}")
    print()

with open(r'D:\Hermes\projects\github-tools\drafts\_inbox_latest.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print(f'\nsnapshot saved: drafts/_inbox_latest.json ({len(d)} items)')
