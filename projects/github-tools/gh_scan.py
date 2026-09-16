import urllib.request, json, os
TOK = open(r'C:\Users\admin\AppData\Local\hermes\.env','r',encoding='utf-8').read()
gh = [l.split('=',1)[1].strip() for l in TOK.splitlines() if l.startswith('GITHUB_TOKEN=')][0]
hdrs = {'User-Agent':'Hermes','Accept':'application/vnd.github+json','Authorization':f'Bearer {gh}'}

def get(url):
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code} {e.reason}'

# 验证 token 是谁
me, err = get('https://api.github.com/user')
if err:
    print('TOKEN 失败:', err)
else:
    print(f"=== 当前登录: {me['login']}  ({me.get('name')}) ===")
    print(f"   public_repos: {me['public_repos']}  followers: {me['followers']}\n")

# 仓库
repos, _ = get('https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member')
print('=== 仓库 (含私有) ===')
for r in repos:
    desc = (r.get('description') or '')[:45]
    priv = ' [私有]' if r.get('private') else ''
    print(f"  {r['name']:<35}{priv:<8} | {desc:<47} | ★{r['stargazers_count']} | {r['updated_at'][:10]}")

# 全网 mention/assign/PR review request
print('\n=== mention 你 (any repo) ===')
d, _ = get('https://api.github.com/search/issues?q=is:open+mentions:Enough1122&per_page=10')
for it in d.get('items',[]):
    repo = it['repository_url'].split('/')[-1]
    print(f"  [{it['state']}] {repo}/{it['title'][:55]}")
    print(f"     {it['html_url']}")
print(f"  total: {d.get('total_count',0)}")

print('\n=== 你创建的 PR (任何 repo) ===')
d, _ = get('https://api.github.com/search/issues?q=is:open+is:pr+author:Enough1122&per_page=10')
for it in d.get('items',[]):
    repo = it['repository_url'].split('/')[-1]
    print(f"  [{it['state']}] {repo}/{it['title'][:55]}")
    print(f"     {it['html_url']}")
print(f"  total: {d.get('total_count',0)}")

print('\n=== review-requested=你 (你被请求 review 的 PR) ===')
d, _ = get('https://api.github.com/search/issues?q=is:open+is:pr+review-requested:Enough1122&per_page=10')
for it in d.get('items',[]):
    repo = it['repository_url'].split('/')[-1]
    print(f"  [{it['state']}] {repo}/{it['title'][:55]}")
    print(f"     {it['html_url']}")
print(f"  total: {d.get('total_count',0)}")

print('\n=== 你创建的 Issue (任何 repo) ===')
d, _ = get('https://api.github.com/search/issues?q=is:open+is:issue+author:Enough1122&per_page=10')
for it in d.get('items',[]):
    repo = it['repository_url'].split('/')[-1]
    print(f"  [{it['state']}] {repo}/{it['title'][:55]}")
    print(f"     {it['html_url']}")
print(f"  total: {d.get('total_count',0)}")

# 你所有 repo 的 open issue / pr
print('\n=== 各 repo 详情 (open) ===')
for r in repos:
    name = r['name']
    iss, _ = get(f"https://api.github.com/search/issues?q=is:open+is:issue+repo:Enough1122/{name}&per_page=5")
    prs, _ = get(f"https://api.github.com/search/issues?q=is:open+is:pr+repo:Enough1122/{name}&per_page=5")
    ic, pc = iss.get('total_count',0), prs.get('total_count',0)
    if ic or pc:
        print(f"\n  [{name}]  open issue:{ic}  open pr:{pc}")
        for it in iss.get('items',[])[:3]:
            print(f"    ISSUE  {it['title'][:55]}")
            print(f"            {it['html_url']}")
        for it in prs.get('items',[])[:3]:
            print(f"    PR     {it['title'][:55]}")
            print(f"            {it['html_url']}")
