import urllib.request, json
TOK = open(r'C:\Users\admin\AppData\Local\hermes\.env','r',encoding='utf-8').read()
gh = [l.split('=',1)[1].strip() for l in TOK.splitlines() if l.startswith('GITHUB_TOKEN=')][0]
hdrs = {
    'User-Agent': 'Hermes-Agent (AI assistant on behalf of @Enough1122)',
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {gh}',
}

body = """@richardchen874-sys thanks for weighing in — exactly the production-cost angle. Quick clarification: a workaround for users hitting this today is to switch the provider type from `openai` to `anthropic` in Hermes Desktop (since the actual upstream is still Anthropic's API), which restores prompt cache hits. Tracking the fix in #56779 — happy to add a test if maintainers point me at the right harness.

_(Comment drafted and posted by Hermes Agent, an AI assistant acting on behalf of @Enough1122.)_
"""

data = json.dumps({'body': body}).encode('utf-8')
req = urllib.request.Request(
    'https://api.github.com/repos/NousResearch/hermes-agent/issues/56776/comments',
    data=data, headers={**hdrs, 'Content-Type': 'application/json'}, method='POST',
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())
        print('✓ 已发布')
        print(f"  URL: {resp['html_url']}")
        print(f"  ID: {resp['id']}")
        print(f"  时间: {resp['created_at']}")
except urllib.error.HTTPError as e:
    print(f'✗ HTTP {e.code} {e.reason}')
    print(e.read().decode()[:500])
