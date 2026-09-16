import urllib.request, json, pathlib

env = pathlib.Path(r'C:\Users\admin\AppData\Local\hermes\.env').read_text(encoding='utf-8')
gh = [l.split('=',1)[1].strip() for l in env.splitlines() if l.startswith('GITHUB_TOKEN=')][0]

body = pathlib.Path(r'D:\Hermes\_github_issue_draft_personality_i18n.md').read_text(encoding='utf-8').lstrip()
# 去掉了顶部那个 ## 标题,因为 GitHub 用 title 字段,body 里再放会重复
if body.startswith('## '):
    body = body.split('\n', 1)[1].lstrip('\n')

title = 'Desktop app "Personality" picker labels are all English — unreadable for Simplified Chinese users (and most non-English locales)'

payload = json.dumps({'title': title, 'body': body}).encode('utf-8')
req = urllib.request.Request(
    'https://api.github.com/repos/NousResearch/hermes-agent/issues',
    data=payload,
    headers={
        'User-Agent': 'Hermes-Agent (AI assistant on behalf of @Enough1122)',
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {gh}',
        'Content-Type': 'application/json',
    },
    method='POST',
)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        resp = json.loads(r.read())
        print('OK')
        print('URL :', resp['html_url'])
        print('NUM :', resp['number'])
        print('ID  :', resp['id'])
        print('TIME:', resp['created_at'])
except urllib.error.HTTPError as e:
    print(f'FAIL HTTP {e.code} {e.reason}')
    print(e.read().decode()[:800])