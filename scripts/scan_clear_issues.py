"""
扫描一批 P2/P3 bug,过滤出真 clear 的(没 PR/没 claim),返回 top N。

新策略:不再依赖 Search API 找"无 PR"的 issue,而是:
1. Search API(用 urllib 避免 bash 转义问题)找一批候选 — 每个 label 单独搜
2. 对每个候选拉 timeline 二次过滤(高命中率)

用法: python scan_clear_issues.py [--max N] [--labels P2,P3]
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_OWNER = "NousResearch"
DEFAULT_REPO = "hermes-agent"


def load_token():
    for line in Path(r"C:\Users\admin\AppData\Local\hermes\.env").read_text().splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip()
    return None


def gh_search(token, q):
    """GitHub Search API,绕过 bash 转义问题"""
    req = urllib.request.Request(
        f"https://api.github.com/search/issues?q={urllib.parse.quote(q, safe=':')}&per_page=50",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("items", [])


def gh_get(token, path):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{DEFAULT_OWNER}/{DEFAULT_REPO}/{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def is_clear(issue_number, token):
    """拉 timeline 检查 cross-referenced"""
    try:
        tl = gh_get(token, f"issues/{issue_number}/timeline?per_page=30")
    except Exception:
        return True  # 出错默认 clear(避免误杀)
    for ev in tl:
        if ev.get("event") == "cross-referenced":
            src = (ev.get("source") or {}).get("issue") or {}
            src_num = src.get("number", 0)
            if src_num and src_num != issue_number:
                return False
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=10)
    p.add_argument("--labels", default="P2,P3")
    p.add_argument("--skip", type=str, default="")
    args = p.parse_args()

    skip = set(int(x) for x in args.skip.split(",") if x.strip())
    token = load_token()
    if not token:
        sys.exit("no token")

    labels = [l for l in args.labels.split(",") if l]
    print("Fetching candidates (one label at a time, due to GitHub Search OR syntax)...")

    # 每个 label 单独搜
    candidates = {}
    for lbl in labels:
        q = f"repo:{DEFAULT_OWNER}/{DEFAULT_REPO} is:issue is:open label:bug label:{lbl} created:>=2026-07-11 sort:created-desc"
        items = gh_search(token, q)
        for it in items:
            n = it["number"]
            if n in skip or n in candidates:
                continue
            candidates[n] = {
                "title": it["title"],
                "comments": it.get("comments", 0),
                "reactions": it.get("reactions", {}).get("+1", 0) + 1,
                "created": it["created_at"][:10],
                "label": lbl,
            }
    print(f"  {len(candidates)} unique candidates")

    print("\nFiltering via timeline (cross-referenced PRs)...")
    cleared = []
    blocked = 0
    for n, info in candidates.items():
        if is_clear(n, token):
            cleared.append((n, info))
        else:
            blocked += 1

    print(f"  {blocked} blocked, {len(cleared)} clear")

    print(f"\nCLEAR candidates:")
    for n, info in cleared[:args.max]:
        print(f"  #{n} [{info['label']}, r={info['reactions']}, c={info['comments']}, {info['created']}]")
        print(f"    {info['title'][:80]}")


if __name__ == "__main__":
    main()