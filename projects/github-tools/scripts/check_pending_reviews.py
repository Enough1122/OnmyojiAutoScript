#!/usr/bin/env python3
"""核对 tmp/reviews/ 下的 review body 对应 PR 的线上状态。

只读工具：对每个 PR 查询 state 与是否已有 Enough1122 的评论，
输出待发清单（open 且尚未评论）。不做任何写操作。
"""
import json
import os
import subprocess
import sys

REPO_OWNER = "NousResearch"
REPO_NAME = "hermes-agent"
SELF = "Enough1122"
BODY_DIR = r"D:\Hermes\tmp\reviews"


def build_query(numbers):
    fields = []
    for n in numbers:
        fields.append(
            f'    p{n}: pullRequest(number: {n}) {{ number state '
            f'comments(first: 100) {{ nodes {{ author {{ login }} }} }} }}'
        )
    body = "\n".join(fields)
    return (
        "query {\n  repository(owner: \"%s\", name: \"%s\") {\n%s\n  }\n}\n"
        % (REPO_OWNER, REPO_NAME, body)
    )


def main():
    names = sorted(
        int(f[:-3]) for f in os.listdir(BODY_DIR) if f.endswith(".md")
    )
    if not names:
        print("no review bodies found")
        return 1

    query = build_query(names)
    env = os.environ.copy()
    # 加载 token
    dotenv = r"C:\Users\admin\AppData\Local\hermes\.env"
    if os.path.exists(dotenv):
        with open(dotenv, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    env["GH_TOKEN"] = line.split("=", 1)[1].strip().strip('"')
                    break

    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True, env=env, encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        print("gh failed:", proc.stderr[:2000])
        return 1

    data = json.loads(proc.stdout)
    if "errors" in data:
        print("graphql errors:", json.dumps(data["errors"])[:2000])
        return 1

    repo = data["data"]["repository"]
    pending, posted, closed = [], [], []
    for key, pr in repo.items():
        if not pr:
            continue
        n = pr["number"]
        authors = {
            (c["author"] or {}).get("login")
            for c in pr["comments"]["nodes"]
        }
        if SELF in authors:
            posted.append(n)
        elif pr["state"] != "OPEN":
            closed.append(n)
        else:
            pending.append(n)

    print(f"total bodies   : {len(names)}")
    print(f"already posted : {len(posted)}")
    print(f"closed/skip    : {len(closed)}")
    print(f"pending send   : {len(pending)}")
    print()
    print("PENDING:")
    print(" ".join(str(x) for x in sorted(pending)))
    if closed:
        print()
        print("CLOSED (do not post):")
        print(" ".join(str(x) for x in sorted(closed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
