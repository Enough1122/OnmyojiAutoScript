#!/usr/bin/env python3
"""求出 Enough1122 在 hermes-agent 已评论 PR 的最大编号（真实上界），
再列出编号大于该上界、仍 open 的新 PR。只读，不发帖。
"""
import json
import os
import subprocess

OWNER, NAME, SELF = "NousResearch", "hermes-agent", "Enough1122"


def gh(args, env):
    p = subprocess.run(["gh"] + args, capture_output=True, text=True,
                       env=env, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def load_env():
    env = os.environ.copy()
    dotenv = r"C:\Users\admin\AppData\Local\hermes\.env"
    if os.path.exists(dotenv):
        with open(dotenv, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    env["GH_TOKEN"] = line.split("=", 1)[1].strip().strip('"')
    return env


def commented_max(env):
    """按 PR 创建时间倒序取我评论过的 PR，求最大编号。"""
    q = (f"repo:{OWNER}/{NAME}+type:pr+commenter:{SELF}")
    code, out, err = gh(
        ["api", f"search/issues?q={q}&sort=created&order=desc&per_page=100",
         "--jq", ".items[] | \"\\(.number) \\(.created_at)\""],
        env)
    if code != 0:
        print("search failed:", err[:500])
        return None, None
    rows = [l.split() for l in out.strip().splitlines() if l.strip()]
    nums = [int(r[0]) for r in rows]
    times = {int(r[0]): r[1] for r in rows}
    return max(nums), times


def has_my_comment(env, numbers):
    """批量查一批 PR 里哪些有我的评论。返回 {number: bool}。"""
    fields = "\n".join(
        f'    p{n}: pullRequest(number: {n}) {{ number state '
        f'comments(first: 100) {{ nodes {{ author {{ login }} }} }} }}'
        for n in numbers)
    query = (f'query {{ repository(owner:"{OWNER}", name:"{NAME}") {{\n'
             f'{fields}\n}}}}\n')
    code, out, err = gh(["api", "graphql", "-f", f"query={query}"], env)
    if code != 0:
        print("graphql failed:", err[:500])
        return {}
    try:
        data = json.loads(out)
    except Exception:
        print("bad json:", out[:300])
        return {}
    if "errors" in data:
        print("graphql errors:", json.dumps(data["errors"])[:600])
        return {}
    res = {}
    for v in data["data"]["repository"].values():
        if not v:
            continue
        authors = {(c["author"] or {}).get("login")
                   for c in v["comments"]["nodes"]}
        res[v["number"]] = SELF in authors
    return res


def main():
    env = load_env()
    mx, times = commented_max(env)
    if mx is None:
        return 1
    print(f"[1] search 上界候选: #{mx} (created {times.get(mx)})")

    # 从上界往上扫，找连续未评论的断点
    cur = mx + 1
    real_max = mx
    gap_streak = 0
    step = 40
    while gap_streak < 3:
        batch = list(range(cur, cur + step))
        res = has_my_comment(env, batch)
        if not res:
            break
        hit = [n for n, v in res.items() if v]
        if hit:
            real_max = max(hit)
            gap_streak = 0
        else:
            gap_streak += 1
        cur += step
    print(f"[2] 真实已评论最大编号: #{real_max}")

    created = times.get(real_max)
    # 若真实上界不在首批 100 里，单独取创建时间
    if not created:
        code, out, _ = gh(
            ["api", f"repos/{OWNER}/{NAME}/pulls/{real_max}",
             "--jq", ".created_at"], env)
        created = out.strip()
    print(f"[3] 该 PR 创建于: {created}")

    # 编号大于上界、仍 open 的新 PR
    q = (f"repo:{OWNER}/{NAME}+type:pr+state:open+created:%3E{created}")
    code, out, err = gh(
        ["api", f"search/issues?q={q}&sort=created&order=asc&per_page=30",
         "--jq", ".items[] | \"\\(.number) | \\(.created_at) | \\(.title)\""],
        env)
    code2, out2, _ = gh(
        ["api", f"search/issues?q={q}&per_page=1", "--jq", ".total_count"],
        env)
    print(f"[4] 编号更大且仍 open 的新 PR 总数: {out2.strip()}")
    print()
    print("最早待 review 的 30 个（按创建时间升序）:")
    print(out.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
