"""Fetch full detail (body + comments + timeline) for every survivor issue.

The mechanical screen only kept number/title/counts, so ranking on evidence
density needs the real text. Writes one JSON file per issue into a folder,
plus a combined index, so triage agents can each read a slice.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = "NousResearch/hermes-agent"
SCRATCH = Path("C:/Users/admin/AppData/Local/hermes/cache/scratch")
SURVIVORS = SCRATCH / "hermes_survivors.json"
OUT_DIR = SCRATCH / "issue_detail"
OUT_INDEX = SCRATCH / "issue_detail_index.json"


def gh_json(args: list[str]):
    p = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def main() -> int:
    rows = json.loads(SURVIVORS.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = []

    for i, r in enumerate(rows, 1):
        n = r["number"]
        detail_file = OUT_DIR / f"{n}.json"
        if detail_file.exists():
            try:
                index.append(json.loads(detail_file.read_text(encoding="utf-8")))
                print(f"[{i}/{len(rows)}] #{n} cached")
                continue
            except json.JSONDecodeError:
                pass

        issue = gh_json(["api", f"repos/{REPO}/issues/{n}"])
        if issue is None:
            print(f"[{i}/{len(rows)}] #{n} ISSUE FETCH FAILED")
            continue
        comments = gh_json(["api", f"repos/{REPO}/issues/{n}/comments?per_page=100"]) or []
        timeline = gh_json([
            "api", f"repos/{REPO}/issues/{n}/timeline?per_page=100",
            "-H", "Accept: application/vnd.github+json",
        ]) or []

        rec = {
            "number": n,
            "title": issue.get("title", ""),
            "state": issue.get("state"),
            "labels": sorted(l["name"] for l in issue.get("labels", [])),
            "assignees": [a.get("login") for a in issue.get("assignees", [])],
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
            "body": issue.get("body") or "",
            "comments": [
                {
                    "user": c.get("user", {}).get("login"),
                    "created_at": c.get("created_at"),
                    "body": c.get("body") or "",
                }
                for c in comments
            ],
            "timeline": [
                {
                    "event": e.get("event"),
                    "actor": (e.get("actor") or e.get("user") or {}).get("login"),
                    "created_at": e.get("created_at"),
                    "commit_id": e.get("commit_id"),
                    "source": (
                        e.get("source", {}).get("issue", {}).get("number")
                        if isinstance(e.get("source"), dict) else None
                    ),
                    "label": (e.get("label") or {}).get("name") if isinstance(e.get("label"), dict) else None,
                }
                for e in timeline
                if isinstance(e, dict)
            ],
        }
        detail_file.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        index.append(rec)
        print(f"[{i}/{len(rows)}] #{n} {len(rec['comments'])}c {len(rec['timeline'])}e  {rec['title'][:70]}")
        time.sleep(0.25)

    OUT_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {len(index)} records; index -> {OUT_INDEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
