import urllib.request, json
TOK = open(r'C:\Users\admin\AppData\Local\hermes\.env','r',encoding='utf-8').read()
gh = [l.split('=',1)[1].strip() for l in TOK.splitlines() if l.startswith('GITHUB_TOKEN=')][0]
hdrs = {'User-Agent':'Hermes','Accept':'application/vnd.github+json','Authorization':f'Bearer {gh}'}

def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=hdrs), timeout=15).read())

# 4 个 item
items = [
    ('PR', 56779, 'NousResearch/hermes-agent'),
    ('PR', 56124, 'NousResearch/hermes-agent'),
    ('ISS', 56776, 'NousResearch/hermes-agent'),
    ('ISS', 56123, 'NousResearch/hermes-agent'),
]

for kind, num, repo in items:
    print(f'\n========== {kind} #{num}  ({repo}) ==========')
    base = f'https://api.github.com/repos/{repo}'
    if kind == 'PR':
        d = get(f'{base}/pulls/{num}')
        print(f"标题: {d['title']}")
        print(f"状态: {d['state']} | draft: {d.get('draft')} | mergeable: {d.get('mergeable')}")
        print(f"分支: {d['head']['ref']} -> {d['base']['ref']}")
        print(f"创建: {d['created_at']}  更新: {d['updated_at']}")
        print(f"URL: {d['html_url']}")
    else:
        d = get(f'{base}/issues/{num}')
        print(f"标题: {d['title']}")
        print(f"状态: {d['state']}")
        print(f"创建: {d['created_at']}  更新: {d['updated_at']}")
        print(f"URL: {d['html_url']}")

    # 标签
    labels = [l['name'] for l in d.get('labels',[])]
    if labels:
        print(f"标签: {', '.join(labels)}")

    # comments count + 最新一条
    n_comments = d.get('comments', 0) or d.get('review_comments', 0)
    if kind == 'PR':
        n_comments = d.get('review_comments', 0)  # inline 评论
    print(f"评论数: {n_comments}")

    if n_comments:
        cmt = get(d['comments_url'])
        for c in cmt:
            u = c['user']['login']
            body = c['body'].replace('\r','').replace('\n',' / ')[:150]
            print(f"  · [{u}] {c['created_at'][:16]}")
            print(f"    {body}")

    # timeline events (有 label / assign / close / merge / review)
    print('  -- timeline (last 8) --')
    tl = get(f'{base}/issues/{num}/timeline?per_page=30')
    for ev in tl[-8:]:
        e = ev.get('event')
        a = ev.get('actor',{}).get('login','') if ev.get('actor') else ''
        if e in ('labeled','assigned','closed','merged','review_requested','review_dismissed','cross-referenced','mentioned','referenced','commented','head_ref_force_pushed'):
            extra = ''
            if e == 'labeled': extra = ev.get('label',{}).get('name','')
            if e == 'assigned': extra = ev.get('assignee',{}).get('login','')
            if e == 'review_requested': extra = ev.get('requested_reviewer',{}).get('login','')
            print(f"    [{ev['created_at'][:10]}] {e}  {a}  {extra}")

    # 是否有 review decision
    if kind == 'PR':
        rev = get(f'{base}/pulls/{num}/reviews')
        if rev:
            print(f"  -- reviews ({len(rev)}) --")
            for r in rev:
                print(f"    {r['user']['login']}: {r['state']}  @ {r['submitted_at'][:10]}")
                if r.get('body'):
                    print(f"      {r['body'][:150]}")
