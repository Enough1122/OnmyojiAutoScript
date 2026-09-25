"""Scan NousResearch/hermes-agent open issues in a 5-15 day window and screen
them against a local cache of ALL open PRs (no GitHub Search API needed).

Outputs a ranked shortlist of genuinely unclaimed, unfixed, uncollided bugs.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = "NousResearch/hermes-agent"
SCRATCH = Path("C:/Users/admin/AppData/Local/hermes/cache/scratch")
PR_CACHE = SCRATCH / "hermes-open-prs.jsonl"

ANCHOR = datetime(2026, 9, 25, 8, 5, 3, tzinfo=timezone.utc)
# Window is CLI-tunable so re-running a different band needs no edit.
# Usage: hermes_issue_scan.py <days_ago_newer> <days_ago_older>
#   5 15  -> the 5-to-15-day-old band  (2026-09-10 .. 2026-09-20)
#   15 30 -> the 15-to-30-day-old band (2026-08-26 .. 2026-09-10)
DAYS_NEWER = int(sys.argv[1]) if len(sys.argv) > 1 else 15   # closer to now
DAYS_OLDER = int(sys.argv[2]) if len(sys.argv) > 2 else 5    # further back
WINDOW_START = (ANCHOR - timedelta(days=DAYS_OLDER)).strftime("%Y-%m-%dT%H:%M:%SZ")
WINDOW_END = (ANCHOR - timedelta(days=DAYS_NEWER)).strftime("%Y-%m-%dT%H:%M:%SZ")

BAD_LABELS = {
    "duplicate", "invalid", "needs-repro", "needs-decision", "wontfix",
    "question", "stale", "help-wanted",
}
# Only real bug/security reports are in scope; skip feature/enhancement/docs.
GOOD_LABELS = {"type/bug", "type/security"}

FIX_CLAIM_RE = re.compile(
    r"\b(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?|address(?:e[sd])?)\b[^\n]{0,40}?"
    r"#(\d{4,6})",
    re.IGNORECASE,
)
ISSUE_REF_RE = re.compile(r"#(\d{4,6})")


def gh(args: list[str]) -> str:
    return subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    ).stdout


def search_issues() -> list[dict]:
    """Fetch the whole window WITHOUT the Search API.

    GitHub Search caps at 1000 results per query, so a wide window silently
    truncates (a 15-30 day window is >1600). Paginate the REST issues
    endpoint instead and filter on created_at client-side.
    """
    out: list[dict] = []
    seen: set[int] = set()
    page = 1
    # ~1669 open issues in a 15-day window at ~1/3 issue density vs PRs, so a
    # 15-day band needs well past 40 pages of 100. Cap high enough to be safe.
    while page <= 200:
        raw = gh([
            "api", "-X", "GET",
            f"repos/{REPO}/issues?state=open&per_page=100&page={page}"
            "&sort=created&direction=desc",
        ])
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print(f"page {page}: rate limited or bad payload; stopping at {len(out)}")
            break
        if not isinstance(data, list) or not data:
            break
        in_window = 0
        oldest = None
        for i in data:
            if "pull_request" in i:
                continue
            created = i.get("created_at", "")
            if oldest is None or created < oldest:
                oldest = created
            if WINDOW_START <= created <= WINDOW_END and i["number"] not in seen:
                seen.add(i["number"])
                out.append(i)
                in_window += 1
        print(f"  page {page}: {in_window} in window (oldest on page {oldest})")
        # sorted newest-first: once a whole page predates the window, stop.
        if oldest and oldest < WINDOW_START:
            print(f"  page {page} predates window start -> done")
            break
        page += 1
    print(f"window {WINDOW_START}..{WINDOW_END}: {len(out)} unique open issues")
    return out


def load_prs() -> list[dict]:
    prs = []
    with PR_CACHE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                prs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return prs


def pr_text(pr: dict) -> str:
    return f"{pr.get('title', '')}\n{pr.get('body', '')}".lower()


def title_tokens(title: str) -> set[str]:
    stop = {
        "the", "a", "an", "when", "with", "and", "or", "to", "of", "in", "on",
        "for", "is", "are", "does", "not", "but", "after", "before", "fix",
        "bug", "hermes", "agent", "issue", "pr", "from", "by", "at", "it",
    }
    return {t for t in re.findall(r"[a-z0-9_]{4,}", title.lower()) if t not in stop}


def main() -> int:
    issues = search_issues()
    prs = load_prs()

    pr_by_fix: dict[int, list[dict]] = defaultdict(list)
    pr_by_ref: dict[int, list[dict]] = defaultdict(list)
    for pr in prs:
        text = pr_text(pr)
        for num in set(FIX_CLAIM_RE.findall(text)):
            pr_by_fix[int(num)].append(pr)
        for num in set(ISSUE_REF_RE.findall(text)):
            pr_by_ref[int(num)].append(pr)

    # Title-bucket index for a cheap keyword-collision pass.
    pr_title_tokens: list[tuple[dict, set[str]]] = [
        (pr, title_tokens(pr.get("title", ""))) for pr in prs
    ]

    kept, dropped = [], defaultdict(list)
    for iss in issues:
        labels = {lbl["name"] for lbl in iss.get("labels", [])}
        if not labels & GOOD_LABELS:
            dropped["not-bug-or-security"].append(iss["number"])
            continue
        if labels & BAD_LABELS:
            dropped["mechanical-exclude"].append(iss["number"])
            continue
        n = iss["number"]
        fixers = pr_by_fix.get(n, [])
        if fixers:
            dropped["claimed-by-open-pr"].append(n)
            continue
        if iss.get("assignees"):
            dropped["assigned"].append(n)
            continue

        body = (iss.get("body") or "").lower()
        toks = title_tokens(iss.get("title", ""))
        loose = [
            pr["number"] for pr, pt in pr_title_tokens
            if pt and toks and len(toks & pt) / len(toks) >= 0.6
        ]
        refs = {p["number"] for p in pr_by_ref.get(n, [])}
        kept.append({
            "number": n,
            "title": iss.get("title", ""),
            "created": iss.get("created_at", ""),
            "comments": iss.get("comments", 0),
            "labels": sorted(labels & (GOOD_LABELS | {"p1", "p2", "p3"})),
            "body_len": len(iss.get("body") or ""),
            "loose_title_prs": sorted(set(loose))[:6],
            "body_ref_prs": sorted(refs)[:6],
        })

    kept.sort(key=lambda r: (-r["comments"], -r["body_len"]))
    print(f"window: {WINDOW_START} .. {WINDOW_END}")
    print(f"open issues in window: {len(issues)}")
    print(f"open PRs cached: {len(prs)}")
    for reason, nums in sorted(dropped.items()):
        print(f"  dropped {reason}: {len(nums)}")
    print(f"\nSURVIVORS after mechanical+collision screen: {len(kept)}")
    for row in kept:
        print(
            f"#{row['number']}\t{row['comments']}c\t{','.join(row['labels'])}\t"
            f"loose={row['loose_title_prs']}\tref={row['body_ref_prs']}\t"
            f"{row['title'][:110]}"
        )

    (SCRATCH / "hermes_survivors.json").write_text(
        json.dumps(kept, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
