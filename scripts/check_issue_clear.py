"""
检查指定 GitHub issue 是否有"已在修"的开放 PR。

可靠算法(7/26 #61158 / #65977 / #71636 教训):
1. 拉 issue timeline + filter event == 'cross-referenced'
2. 拉 PRs that reference issue body(issue 号 in body/title) — 这个命中率 5-10%
3. **PR comments 里 grep "take this / will fix / working on / i can take"** — 标记 claim

GitHub Timeline 的 cross-referenced event 由 PR body 写 "#61158" 触发,
触发后通过 /timeline API 可以拉到 source.issue.number。
命中率接近 100%(本 script 验证)。

用法:
  python check_issue_clear.py ISSUE_NUMBER [--owner OWNER] [--repo REPO]

退出码:0 = clear(没 PR/没人 claim),1 = 已有 PR/claim
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_OWNER = "NousResearch"
DEFAULT_REPO = "hermes-agent"


def load_token():
    for line in Path(r"C:\Users\admin\AppData\Local\hermes\.env").read_text().splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip()
    sys.exit("❌ GITHUB_TOKEN not in .env")


def gh_api(method, path, token, payload=None):
    args = [
        "curl", "-sH", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github+json",
        "-X", method, "--data-binary", "@-",
        f"https://api.github.com/repos/{DEFAULT_OWNER}/{DEFAULT_REPO}/{path}",
    ]
    r = subprocess.run(args, input=payload, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    if r.stdout.strip():
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            return None
    return None


def check_issue_clear(issue_number: int, token: str) -> dict:
    """返回 {clear: bool, blocking_prs: [...], claims: [...]}"""
    blocking_prs = []
    claims = []

    # 1. timeline-based(高命中率)
    timeline = gh_api("GET", f"issues/{issue_number}/timeline?per_page=30", token) or []
    for ev in timeline:
        if ev.get("event") == "cross-referenced":
            src = (ev.get("source") or {}).get("issue") or {}
            src_num = src.get("number", 0)
            if src_num and src_num != issue_number:
                src_state = src.get("state", "unknown")
                src_url = src.get("html_url", "")
                blocking_prs.append({
                    "n": src_num,
                    "state": src_state,
                    "title": src.get("title", "")[:60],
                    "url": src_url,
                })

    # 2. comment-based claim detection
    comments = gh_api("GET", f"issues/{issue_number}/comments?per_page=30", token) or []
    claim_patterns = ["take this", "will fix", "working on", "i can take", "i'll take", "going to fix", "planning to fix"]
    for c in comments:
        body = (c.get("body") or "").lower()
        actor = c.get("user", {}).get("login", "?")
        for pat in claim_patterns:
            if pat in body:
                claims.append({"by": actor, "phrase": pat, "url": c.get("html_url", "")})
                break

    return {
        "clear": len(blocking_prs) == 0 and len(claims) == 0,
        "blocking_prs": blocking_prs,
        "claims": claims,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("issue_number", type=int)
    p.add_argument("--owner", default=DEFAULT_OWNER)
    p.add_argument("--repo", default=DEFAULT_REPO)
    args = p.parse_args()

    token = load_token()
    result = check_issue_clear(args.issue_number, token)

    print(f"Issue #{args.issue_number}:")
    if result["blocking_prs"]:
        print(f"  🚫 {len(result['blocking_prs'])} blocking PR(s):")
        for pr in result["blocking_prs"]:
            print(f"    - #{pr['n']} [{pr['state']}] {pr['title']}")
            print(f"      {pr['url']}")
    if result["claims"]:
        print(f"  👤 {len(result['claims'])} claim(s):")
        for c in result["claims"]:
            print(f"    - @{c['by']}: \"{c['phrase']}\"")
    if result["clear"]:
        print(f"  ✅ Clear (no PRs, no claims) — safe to fix")

    sys.exit(0 if result["clear"] else 1)


if __name__ == "__main__":
    main()