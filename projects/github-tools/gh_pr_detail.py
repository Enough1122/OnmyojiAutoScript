import json, re, urllib.request
from urllib.request import Request, urlopen

TOK = open(r'C:\Users\admin\AppData\Local\hermes\.env', 'r', encoding='utf-8').read()
gh = [l.split('=', 1)[1].strip() for l in TOK.splitlines() if l.startswith('GITHUB_TOKEN=')][0]
hdrs = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {gh}'}

def g(u):
    try:
        return json.loads(urlopen(Request(u, headers=hdrs), timeout=20).read())
    except urllib.error.HTTPError as e:
        return {'__err__': f'HTTP {e.code}'}

def clean(s, n=220):
    if not s:
        return '(no body)'
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = s.replace('\r', '').replace('\n', ' / ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:n]

repo = 'NousResearch/hermes-agent'
base = f'https://api.github.com/repos/{repo}'

nums = [int(x) for x in input('PR numbers (space separated): ').split()]

for num in nums:
    try:
        pr = g(f'{base}/pulls/{num}')
    except Exception as e:
        print(f'PR {num}: ERR {e}'); continue
    if isinstance(pr, dict) and pr.get('__err__'):
        print(f'PR {num}: {pr}'); continue
    print('=' * 100)
    print(f"PR #{num}  [{pr['state']}{'/draft' if pr.get('draft') else ''}]  by {pr['user']['login']}")
    print(f"TITLE: {pr['title']}")
    print(f"BRANCH: {pr['head']['ref']} -> {pr['base']['ref']}")
    print(f"CREATED: {pr['created_at'][:16]}   UPDATED: {pr['updated_at'][:16]}")
    print(f"URL: {pr['html_url']}")

    # issue comments (general thread)
    ic = g(pr['comments_url'])
    if isinstance(ic, list) and ic:
        print(f'\n-- issue comments ({len(ic)}) --')
        for c in ic[-6:]:
            print(f"  [{c['user']['login']}] {c['created_at'][:16]}")
            for line in clean(c['body'], 400).split(' / '):
                print(f"      {line[:200]}")

    # reviews
    rv = g(f'{base}/pulls/{num}/reviews')
    if isinstance(rv, list) and rv:
        print(f'\n-- reviews ({len(rv)}) --')
        for r in rv[-6:]:
            print(f"  [{r['user']['login']}] state={r['state']} {r['submitted_at'][:16]}")
            for line in clean(r.get('body'), 300).split(' / '):
                print(f"      {line[:160]}")

    # review comments (inline)
    rc = g(f'{base}/pulls/{num}/comments?per_page=100')
    if isinstance(rc, list) and rc:
        print(f'\n-- inline review comments ({len(rc)}) --')
        for c in rc[-6:]:
            print(f"  [{c['user']['login']}] {c['created_at'][:16]} {c.get('path','')}:{c.get('line')}")
            for line in clean(c['body'], 300).split(' / '):
                print(f"      {line[:160]}")
