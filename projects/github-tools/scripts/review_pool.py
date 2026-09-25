#!/usr/bin/env python3
"""Durable PR-review worker pool.

Commands:
  claim <worker> <lease-seconds> [lane]
                                 Atomically claim the highest-priority eligible task.
                                 Idempotent for a worker: an existing running claim is
                                 renewed and returned instead of creating another.
                                 lane: fast prefers changed_files <= 15 and <=250 changed lines;
                                       deep prefers larger/high-churn tasks; any preserves
                                       PR-desc priority. Each lane falls back to the other
                                       queued work so it never starves.
  heartbeat <pr> <worker> <lease-seconds>
                                 Extend a running claim only for its current owner.
  release <pr> <worker> [reason]
                                 Return an owned claim to queued after confirmed worker exit.
  requeue <pr> <worker> [reason]
                                 Requeue a terminal result owned by that worker after correction.
  requeue <pr> <worker> <reason> <old-head>:<new-head>
                                 Atomically requeue only if the stored head still matches
                                 old-head, then replace it with new-head in the same transaction.
  result <pr> <result> <worker> [comment-url]
                                 Record done/clean/posted/corrected/skip for the current claimant.
                                 posted and corrected require a matching hermes-agent
                                 issuecomment URL; corrected is tracked separately from findings.
  stats                            Print status counts.
  metrics                          Print status counts, fresh/expired claims, queue bands, and last-24h completions.
"""
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

DONE_RESULTS = {"clean", "posted", "corrected", "skip", "deferred", "error"}
RECEIPT_CLOCK_SKEW_SECONDS = 5


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA journal_mode=WAL")
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()
    }
    if "claim_started_at" not in columns:
        try:
            conn.execute("ALTER TABLE tasks ADD COLUMN claim_started_at REAL")
        except sqlite3.OperationalError as exc:
            if "duplicate column name" not in str(exc).lower():
                raise
    # Legacy databases predate claim_started_at. Start enforcement now for
    # currently running claims rather than silently accepting old receipts.
    conn.execute(
        "UPDATE tasks SET claim_started_at = ? "
        "WHERE status = 'running' AND claim_started_at IS NULL",
        (time.time(),),
    )
    return conn


def _task_size(row: sqlite3.Row | dict) -> int:
    return (
        (row["changed_files"] or 0)
        + (row["additions"] or 0)
        + (row["deletions"] or 0)
    )


def _lane_clause(lane: str) -> tuple[str, str]:
    """Return lane-specific SQL and ORDER BY clause.

    Both lanes retain the same atomic claim and may fall back to any queued
    task, but fast workers avoid large PRs while deep workers avoid tiny
    dependency/docs PRs. A queue must never stall merely because one lane is
    empty.
    """
    if lane == "fast":
        return (
            "(COALESCE(changed_files, 0) <= 15 "
            "AND COALESCE(additions, 0) + COALESCE(deletions, 0) <= 250)",
            "COALESCE(changed_files, 0), COALESCE(additions, 0) + COALESCE(deletions, 0), pr DESC",
        )
    if lane == "deep":
        return (
            "(COALESCE(changed_files, 0) > 15 "
            "OR COALESCE(additions, 0) + COALESCE(deletions, 0) > 250)",
            "CASE WHEN COALESCE(changed_files, 0) > 100 OR COALESCE(additions, 0) + COALESCE(deletions, 0) > 5000 THEN 1 ELSE 0 END, COALESCE(changed_files, 0) ASC, COALESCE(additions, 0) + COALESCE(deletions, 0) ASC, pr DESC",
        )
    if lane in {"any", ""}:
        return "1=1", "pr DESC"
    raise ValueError(f"unknown lane: {lane}")


def _priority_order(lane_order: str) -> str:
    """Put re-review/requeue work ahead of ordinary frontier work."""
    priority = (
        "CASE WHEN result LIKE 'head changed:%' "
        "OR result LIKE 'previously deferred without review%' "
        "OR result LIKE 'resume:%' THEN 0 ELSE 1 END"
    )
    return f"{priority}, {lane_order}"


def claim(db_path: str, worker: str, lease_seconds: float, lane: str = "any") -> dict | None:
    conn = connect(db_path)
    now = time.time()
    lease_until = now + lease_seconds
    lane_filter, lane_order = _lane_clause(lane)
    try:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            """SELECT * FROM tasks
               WHERE status = 'running' AND claimed_by = ?
               ORDER BY updated_at DESC LIMIT 1""",
            (worker,),
        ).fetchone()
        if existing is not None:
            conn.execute(
                """UPDATE tasks SET lease_until = ?, updated_at = ?
                   WHERE pr = ? AND status = 'running' AND claimed_by = ?""",
                (lease_until, now, existing["pr"], worker),
            )
            conn.execute("COMMIT")
            return dict(existing) | {
                "status": "running",
                "claimed_by": worker,
                "lease_until": lease_until,
                "lane": lane or "any",
            }
        candidates = [
            (
                "SELECT * FROM tasks "
                "WHERE (status = 'queued' "
                f"       OR (status = 'running' AND COALESCE(lease_until, 0) <= ?)) "
                f"  AND ({lane_filter}) "
                f"ORDER BY {_priority_order(lane_order)} LIMIT 1",
                (now,),
            ),
            (
                "SELECT * FROM tasks "
                "WHERE status = 'queued' "
                f"   OR (status = 'running' AND COALESCE(lease_until, 0) <= ?) "
                "ORDER BY pr DESC LIMIT 1",
                (now,),
            ),
        ]
        row = None
        for query, params in candidates:
            row = conn.execute(query, params).fetchone()
            if row is not None:
                break
        if row is None:
            conn.execute("COMMIT")
            return None
        conn.execute(
            """UPDATE tasks
               SET status = 'running', claimed_by = ?, lease_until = ?,
                   result = NULL, comment_url = NULL,
                   claim_started_at = ?, updated_at = ?
               WHERE pr = ? AND (
                    status = 'queued'
                    OR (status = 'running' AND COALESCE(lease_until, 0) <= ?)
               )""",
            (worker, lease_until, now, now, row["pr"], now),
        )
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            conn.execute("ROLLBACK")
            return None
        conn.execute("COMMIT")
        return dict(row) | {
            "status": "running",
            "claimed_by": worker,
            "lease_until": lease_until,
            "lane": lane or "any",
        }
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def heartbeat(db_path: str, pr: int, worker: str, lease_seconds: float) -> None:
    conn = connect(db_path)
    now = time.time()
    lease_until = now + lease_seconds
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT claimed_by, status FROM tasks WHERE pr = ?", (pr,)
        ).fetchone()
        if row is None or row["status"] != "running" or row["claimed_by"] != worker:
            conn.execute("ROLLBACK")
            raise RuntimeError("claim owner mismatch")
        conn.execute(
            "UPDATE tasks SET lease_until = ?, updated_at = ? WHERE pr = ? AND claimed_by = ?",
            (lease_until, now, pr, worker),
        )
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def release(
    db_path: str,
    pr: int,
    worker: str,
    reason: str = "released by coordinator",
) -> None:
    conn = connect(db_path)
    now = time.time()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT claimed_by, status FROM tasks WHERE pr = ?", (pr,)
        ).fetchone()
        if row is None or row["status"] != "running" or row["claimed_by"] != worker:
            conn.execute("ROLLBACK")
            raise RuntimeError("claim owner mismatch")
        conn.execute(
            """UPDATE tasks
               SET status = 'queued', claimed_by = NULL, lease_until = NULL,
                   result = ?, comment_url = NULL, updated_at = ?
               WHERE pr = ? AND status = 'running' AND claimed_by = ?""",
            (f"resume: {reason}", now, pr, worker),
        )
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def requeue(
    db_path: str,
    pr: int,
    worker: str,
    reason: str = "terminal result corrected by coordinator",
    expected_head_sha: str | None = None,
    new_head_sha: str | None = None,
) -> None:
    conn = connect(db_path)
    now = time.time()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT claimed_by, status, head_sha FROM tasks WHERE pr = ?", (pr,)
        ).fetchone()
        if row is None or row["status"] not in DONE_RESULTS or row["claimed_by"] != worker:
            conn.execute("ROLLBACK")
            raise RuntimeError("claim owner mismatch")
        if expected_head_sha is not None and row["head_sha"] != expected_head_sha:
            conn.execute("ROLLBACK")
            raise RuntimeError(
                f"head changed: expected {expected_head_sha}, found {row['head_sha']}"
            )
        conn.execute(
            """UPDATE tasks
               SET status = 'queued', claimed_by = NULL, lease_until = NULL,
                   result = ?, comment_url = NULL,
                   head_sha = COALESCE(?, head_sha), updated_at = ?
               WHERE pr = ? AND status = ? AND claimed_by = ?""",
            (f"resume: {reason}", new_head_sha, now, pr, row["status"], worker),
        )
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def _validate_posted_comment_url(
    pr: int, comment_url: str, *, result: str = "posted"
) -> str | None:
    """Validate a GitHub issue-comment receipt and return its numeric comment ID."""
    if not comment_url.strip():
        raise ValueError(f"{result} result requires a comment URL")
    parsed = urlparse(comment_url.strip())
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ValueError(f"comment URL is not a GitHub URL: {comment_url}")
    if not re.fullmatch(r"/NousResearch/hermes-agent/(?:pull|issues)/(\d+)", parsed.path):
        raise ValueError(f"comment URL is not a hermes-agent PR URL: {comment_url}")
    if int(parsed.path.rsplit("/", 1)[1]) != pr:
        raise ValueError(f"comment URL does not match PR {pr}: {comment_url}")
    fragment = re.fullmatch(r"issuecomment-(\d+)", parsed.fragment)
    if not fragment:
        raise ValueError(f"comment URL is missing an issuecomment receipt: {comment_url}")
    return fragment.group(1)


def _verify_posted_receipt(
    pr: int,
    comment_url: str,
    comment_id: str,
    *,
    claim_started_at: float | None = None,
) -> None:
    """Read the GitHub comment back and reject a receipt we did not author."""
    expected_url = (
        f"https://github.com/NousResearch/hermes-agent/pull/{pr}"
        f"#issuecomment-{comment_id}"
    )
    receipt = subprocess.run(
        [
            "gh",
            "api",
            f"repos/NousResearch/hermes-agent/issues/comments/{comment_id}",
            "--jq",
            "{author: .user.login, url: .html_url, created_at: .created_at}",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if receipt.returncode != 0:
        detail = receipt.stderr.strip() or f"exit {receipt.returncode}"
        raise RuntimeError(f"receipt read-back failed: {detail}")
    try:
        data = json.loads(receipt.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError("receipt read-back returned invalid JSON") from exc
    if data.get("author") != "Enough1122":
        raise ValueError("receipt author is not Enough1122")
    if str(data.get("url") or "").rstrip("/") != expected_url.rstrip("/"):
        raise ValueError(f"receipt URL mismatch: {data.get('url')}")
    if comment_url.rstrip("/") != expected_url.rstrip("/"):
        raise ValueError(f"comment URL mismatch: {comment_url}")
    if claim_started_at is not None:
        created_at = str(data.get("created_at") or "")
        try:
            created_epoch = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
        except ValueError as exc:
            raise RuntimeError("receipt read-back returned invalid created_at") from exc
        if created_epoch < claim_started_at - RECEIPT_CLOCK_SKEW_SECONDS:
            raise ValueError("receipt predates current claim")


def record_result(
    db_path: str,
    pr: int,
    result: str,
    worker: str,
    comment_url: str = "",
) -> None:
    if result not in DONE_RESULTS:
        raise ValueError(f"unknown result: {result}")
    comment_id = None
    conn = connect(db_path)
    try:
        # Snapshot the current claim before any network verification. The final
        # transaction below rechecks owner/status so an expired/reassigned claim
        # can never win a race with a slow GitHub read-back.
        claim = conn.execute(
            "SELECT claimed_by, status, claim_started_at FROM tasks WHERE pr = ?",
            (pr,),
        ).fetchone()
        if (
            claim is None
            or claim["status"] != "running"
            or claim["claimed_by"] != worker
        ):
            raise RuntimeError("claim owner mismatch")
        claim_started_at = claim["claim_started_at"]
        if result in {"posted", "corrected"}:
            comment_id = _validate_posted_comment_url(pr, comment_url, result=result)
            _verify_posted_receipt(
                pr,
                comment_url,
                comment_id,
                claim_started_at=claim_started_at,
            )
        now = time.time()
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT claimed_by, status, claim_started_at FROM tasks WHERE pr = ?", (pr,)
        ).fetchone()
        if (
            row is None
            or row["status"] != "running"
            or row["claimed_by"] != worker
            or row["claim_started_at"] != claim_started_at
        ):
            conn.execute("ROLLBACK")
            raise RuntimeError("claim owner mismatch")
        status = result
        conn.execute(
            """UPDATE tasks
               SET status = ?, result = ?, comment_url = NULLIF(?, ''),
                   lease_until = NULL, updated_at = ?
               WHERE pr = ? AND claimed_by = ?""",
            (status, result, comment_url, now, pr, worker),
        )
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def stats(db_path: str) -> dict[str, int]:
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM tasks GROUP BY status"
        ).fetchall()
        return {row["status"]: row["n"] for row in rows}
    finally:
        conn.close()


def metrics(db_path: str) -> dict:
    """Return a compact coordinator health/throughput snapshot."""
    conn = connect(db_path)
    now = time.time()
    try:
        status_rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM tasks GROUP BY status"
        ).fetchall()
        status_counts = {row["status"]: row["n"] for row in status_rows}
        claim_row = conn.execute(
            """SELECT
                   SUM(CASE WHEN lease_until IS NULL OR lease_until <= ? THEN 1 ELSE 0 END) AS expired,
                   SUM(CASE WHEN lease_until > ? THEN 1 ELSE 0 END) AS fresh
               FROM tasks WHERE status = 'running'""",
            (now, now),
        ).fetchone()
        band_row = conn.execute(
            """SELECT
                   SUM(CASE WHEN COALESCE(changed_files, 0) <= 15
                                  AND COALESCE(additions, 0) + COALESCE(deletions, 0) <= 250
                            THEN 1 ELSE 0 END) AS small,
                   SUM(CASE WHEN COALESCE(changed_files, 0) > 15
                                  OR COALESCE(additions, 0) + COALESCE(deletions, 0) > 250
                            THEN 1 ELSE 0 END) AS large
               FROM tasks WHERE status = 'queued'"""
        ).fetchone()
        completion_row = conn.execute(
            """SELECT
                   SUM(CASE WHEN updated_at >= ? THEN 1 ELSE 0 END) AS completed_24h,
                   SUM(CASE WHEN updated_at >= ? AND status = 'posted' THEN 1 ELSE 0 END) AS posted_24h,
                   SUM(CASE WHEN updated_at >= ? AND status = 'clean' THEN 1 ELSE 0 END) AS clean_24h,
                   SUM(CASE WHEN updated_at >= ? AND status = 'corrected' THEN 1 ELSE 0 END) AS corrected_24h
               FROM tasks
               WHERE status IN ('clean', 'posted', 'corrected', 'skip', 'deferred')""",
            (now - 86400, now - 86400, now - 86400, now - 86400),
        ).fetchone()
        return {
            "status_counts": status_counts,
            "fresh_claims": int(claim_row["fresh"] or 0),
            "expired_claims": int(claim_row["expired"] or 0),
            "queue_bands": {
                "small": int(band_row["small"] or 0),
                "large": int(band_row["large"] or 0),
            },
            "completed_24h": {
                "total": int(completion_row["completed_24h"] or 0),
                "posted": int(completion_row["posted_24h"] or 0),
                "clean": int(completion_row["clean_24h"] or 0),
                "corrected": int(completion_row["corrected_24h"] or 0),
            },
        }
    finally:
        conn.close()


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "usage: review_pool.py <db> "
            "<claim|heartbeat|release|requeue|result|stats|metrics> ...",
            file=sys.stderr,
        )
        return 2
    db_path = sys.argv[1]
    action = sys.argv[2]
    try:
        if action == "claim" and len(sys.argv) in (5, 6):
            lane = sys.argv[5] if len(sys.argv) == 6 else "any"
            task = claim(db_path, sys.argv[3], float(sys.argv[4]), lane)
            print(json.dumps(task, ensure_ascii=False))
            return 0
        if action == "heartbeat" and len(sys.argv) == 6:
            heartbeat(db_path, int(sys.argv[3]), sys.argv[4], float(sys.argv[5]))
            return 0
        if action == "release" and len(sys.argv) in (5, 6):
            reason = sys.argv[5] if len(sys.argv) == 6 else "released by coordinator"
            release(db_path, int(sys.argv[3]), sys.argv[4], reason)
            return 0
        if action == "requeue" and len(sys.argv) in (5, 6, 7):
            reason = sys.argv[5] if len(sys.argv) >= 6 else "terminal result corrected by coordinator"
            if len(sys.argv) == 7:
                head_pair = sys.argv[6].split(":")
                if (
                    len(head_pair) != 2
                    or any(not re.fullmatch(r"[0-9a-fA-F]{40}", sha) for sha in head_pair)
                ):
                    print("head drift requeue requires <old-head>:<new-head>", file=sys.stderr)
                    return 2
                expected_head_sha, new_head_sha = head_pair
            else:
                expected_head_sha = new_head_sha = None
            requeue(
                db_path,
                int(sys.argv[3]),
                sys.argv[4],
                reason,
                expected_head_sha=expected_head_sha,
                new_head_sha=new_head_sha,
            )
            return 0
        if action == "result" and len(sys.argv) in (6, 7):
            worker = sys.argv[5]
            comment_url = sys.argv[6] if len(sys.argv) == 7 else ""
            record_result(db_path, int(sys.argv[3]), sys.argv[4], worker, comment_url)
            return 0
        if action == "stats":
            print(json.dumps(stats(db_path), ensure_ascii=False, sort_keys=True))
            return 0
        if action == "metrics" and len(sys.argv) == 3:
            print(json.dumps(metrics(db_path), ensure_ascii=False, sort_keys=True))
            return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("invalid arguments", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
