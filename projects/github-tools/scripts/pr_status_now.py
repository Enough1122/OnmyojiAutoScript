#!/usr/bin/env python3
"""Check merged vs closed-unmerged for previously-open PRs + current status of remaining 5."""
import json
import subprocess

OLD_OPEN = [92058, 92057, 92056, 92055, 92054, 92053, 92052, 92051, 91984, 91983,
            91982, 91954, 91948, 91947, 91946, 91945, 91944, 91943, 91941, 91940,
            91576, 91562, 87717, 87037, 84511, 82220, 82211, 81784, 81752, 81622,
            81573, 81571, 81536, 81530, 81231, 81182, 81174, 81108, 81097, 81059,
            81053, 81009, 81008, 80785, 80779, 75476, 71884, 71490, 70725, 66926]

STILL_OPEN = [91984, 81530, 81108, 75476, 66926]

NODE = """      p{num}: pullRequest(number: {num}) {{
        number
        state
        merged
        closedAt
        mergeStateStatus
        reviewDecision
        comments(first: 50) {{
          nodes {{ author {{ login }} body createdAt }}
        }}
        statusCheckRollup {{
          contexts(first: 100) {{
            nodes {{
              ... on CheckRun {{ name conclusion }}
              ... on StatusContext {{ name: context state }}
            }}
          }}
        }}
      }}"""


def gh_graphql(query: str) -> dict:
    p = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    return json.loads(p.stdout)


def fetch(prs):
    out = {}
    B = 10
    for i in range(0, len(prs), B):
        chunk = prs[i:i + B]
        nodes = "\n".join(NODE.format(num=n) for n in chunk)
        q = 'query {\n  repository(owner: "NousResearch", name: "hermes-agent") {\n' + nodes + "\n  }\n}"
        payload = gh_graphql(q)
        if payload.get("errors"):
            raise RuntimeError(json.dumps(payload["errors"], indent=2))
        repo = payload["data"]["repository"]
        for n in chunk:
            pr = repo.get(f"p{n}")
            if pr:
                out[n] = pr
    return out


def main():
    data = fetch(OLD_OPEN)
    merged, closed_unmerged = [], []
    for n in OLD_OPEN:
        pr = data.get(n)
        if not pr:
            print(f"#{n}: FETCH FAILED")
            continue
        if pr["state"] == "OPEN":
            continue
        if pr["merged"]:
            merged.append(n)
        else:
            closed_unmerged.append(n)
    print(f"== MERGED ({len(merged)}): {merged}")
    print(f"== CLOSED UNMERGED ({len(closed_unmerged)}): {closed_unmerged}")

    print("\n===== 仍 OPEN 的 5 个详细状态 =====")
    for n in STILL_OPEN:
        pr = data[n]
        ctx = (pr["statusCheckRollup"] or {}).get("contexts", {}).get("nodes", []) or []
        required = next((c for c in ctx if c.get("name") == "All required checks pass"), None)
        ci = (required.get("conclusion") or required.get("state")) if required else "NO-ROLLUP"
        print(f"\n--- #{n} [{pr['state']}/{pr['mergeStateStatus']}] review={pr['reviewDecision'] or 'none'} CI={ci}")
        for c in pr["comments"]["nodes"][-4:]:
            body = c["body"][:250].replace("\n", " ")
            print(f"  [{c['createdAt'][:10]}] {(c['author'] or {}).get('login', '?')}: {body}")


if __name__ == "__main__":
    main()
