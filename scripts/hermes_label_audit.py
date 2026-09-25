"""Check whether the GOOD_LABELS filter is wrongly discarding real bugs:
dump the full label distribution of open issues in the 5-15 day window,
and list every issue with NO type/* label at all (labeling may lag).
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone

REPO = "NousResearch/hermes-agent"
ANCHOR = datetime(2026, 9, 25, 8, 5, 3, tzinfo=timezone.utc)
START = (ANCHOR - timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
END = (ANCHOR - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh(args: list[str]) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=False).stdout


def main() -> None:
    issues: list[dict] = []
    for page in (1, 2, 3):
        raw = gh([
            "api", "-X", "GET", "search/issues", "-f",
            f"q=repo:{REPO} is:issue is:open created:{START}..{END}",
            "-f", "per_page=100", "-f", f"page={page}",
        ])
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print("STOP: rate limited / bad payload")
            break
        items = [i for i in data.get("items", []) if "pull_request" not in i]
        issues.extend(items)
        total = data.get("total_count", 0)
        if len(data.get("items", [])) < 100 or len(issues) >= total:
            break

    print(f"window {START} .. {END}; total_count={total}; fetched={len(issues)}\n")

    dist: Counter[str] = Counter()
    unlabeled, no_type = [], []
    for i in issues:
        labels = [lbl["name"] for lbl in i.get("labels", [])]
        for lb in labels:
            dist[lb] += 1
        if not labels:
            unlabeled.append(i)
        elif not any(lb.startswith("type/") for lb in labels):
            no_type.append(i)

    print("=== label frequency ===")
    for lb, n in dist.most_common(40):
        print(f"{n:5}  {lb}")

    print(f"\n=== issues with NO labels at all: {len(unlabeled)} ===")
    for i in sorted(unlabeled, key=lambda x: -x.get("comments", 0))[:40]:
        print(
            f"#{i['number']}\t{i.get('comments',0)}c\t{i['created_at'][:10]}\t"
            f"{i.get('title','')[:105]}"
        )

    print(f"\n=== issues with labels but no type/* label: {len(no_type)} ===")
    for i in sorted(no_type, key=lambda x: -x.get("comments", 0))[:40]:
        labels = ",".join(lbl["name"] for lbl in i.get("labels", []))
        print(
            f"#{i['number']}\t{i.get('comments',0)}c\t{labels[:40]}\t"
            f"{i.get('title','')[:95]}"
        )


if __name__ == "__main__":
    main()
