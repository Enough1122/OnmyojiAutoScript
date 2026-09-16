"""扫描 hermes-agent 仓库最近 issue，按 ROI 排序"""
import json, re, urllib.request
from datetime import datetime, timezone, timedelta

with open(r'C:\Users\admin\AppData\Local\hermes\.env', 'r', encoding='utf-8') as f:
    TOKEN = re.search(r'^GITHUB_TOKEN=(.+)$', f.read(), re.M).group(1).strip()

def gh(path, params=''):
    url = f'https://api.github.com{path}{params}'
    req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github+json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

# 7 天前
cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')

# 1) 24h-7d 新 issue (skip label:bug 全无 → 直接开 open + sort=created-desc)
print(f'=== 搜索 7 天内新 issue (cutoff {cutoff}) ===')
data = gh('/search/issues', f'?q=repo:NousResearch/hermes-agent+is:issue+is:open+created:>={cutoff}+-label:duplicate+-label:needs-decision+-label:wontfix&sort=created-desc&per_page=50')
print(f"total: {data.get('total_count','?')}")
items = data.get('items', [])
print(f"\n{'#':<7}{'created':<12}{'comments':<9}{'title':<70}")
for it in items:
    print(f"#{it['number']:<6}{it['created_at'][:10]:<12}{it['comments']:<9}{it['title'][:65]}")
