from __future__ import annotations

import importlib.util
import json
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "review_pool.py"


def _init(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE tasks (
        pr INTEGER PRIMARY KEY,
        title TEXT,
        head_sha TEXT,
        changed_files INTEGER,
        additions INTEGER,
        deletions INTEGER,
        url TEXT,
        status TEXT NOT NULL DEFAULT 'queued',
        claimed_by TEXT,
        lease_until REAL,
        result TEXT,
        comment_url TEXT,
        updated_at REAL DEFAULT (unixepoch('now'))
    )"""
    )
    conn.executemany(
        "INSERT INTO tasks(pr, title) VALUES (?, ?)",
        [(2, "two"), (1, "one")],
    )
    conn.commit()
    conn.close()


def _load_pool_module():
    spec = importlib.util.spec_from_file_location("review_pool_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _stub_github_receipt(
    monkeypatch,
    module,
    *,
    login: str,
    html_url: str | None = None,
    created_at: str | None = None,
) -> None:
    real_run = subprocess.run
    created = created_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def fake_run(command, *args, **kwargs):
        if not command or command[0] != "gh":
            return real_run(command, *args, **kwargs)
        if "--jq" not in command:
            raise AssertionError("receipt check must use gh --jq output")
        jq = command[command.index("--jq") + 1]
        if jq == 'if .user.login == "Enough1122" then .html_url else empty end':
            value = html_url if login == "Enough1122" else ""
            return subprocess.CompletedProcess(command, 0, value + "\n", "")
        if jq == "{author: .user.login, url: .html_url, created_at: .created_at}":
            value = {
                "author": login if login == "Enough1122" else "",
                "url": html_url if login == "Enough1122" else "",
                "created_at": created if login == "Enough1122" else "",
            }
            return subprocess.CompletedProcess(
                command, 0, json.dumps(value) + "\n", ""
            )
        if jq == ".created_at":
            value = created if login == "Enough1122" else ""
            return subprocess.CompletedProcess(command, 0, value + "\n", "")
        raise AssertionError(f"unexpected receipt jq: {jq}")

    monkeypatch.setattr(module.subprocess, "run", fake_run)


def test_claim_returns_highest_priority_and_marks_running(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)

    result = _run(db, "claim", "worker-a", "120")

    assert result.returncode == 0, result.stderr
    payload = result.stdout.strip().splitlines()
    assert '"pr": 2' in payload[0]
    assert '"status": "running"' in payload[0]
    assert '"claimed_by": "worker-a"' in payload[0]


def test_claim_is_idempotent_for_same_worker(
    tmp_path: Path,
) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    first = _run(db, "claim", "worker-a", "120")
    assert first.returncode == 0, first.stderr

    second = _run(db, "claim", "worker-a", "120")

    assert second.returncode == 0, second.stderr
    first_pr = json.loads(first.stdout)["pr"]
    second_pr = json.loads(second.stdout)["pr"]
    assert second_pr == first_pr
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT pr FROM tasks WHERE status = 'running' AND claimed_by = 'worker-a'"
    ).fetchall()
    conn.close()
    assert rows == [(first_pr,)]


def test_result_then_next_claim_does_not_return_same_task(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0

    done = _run(db, "result", "2", "clean", "worker-a")

    assert done.returncode == 0, done.stderr
    next_claim = _run(db, "claim", "worker-a", "120")
    assert next_claim.returncode == 0, next_claim.stderr
    assert '"pr": 1' in next_claim.stdout


def test_result_rejects_wrong_claim_owner(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0

    result = _run(db, "result", "2", "clean", "worker-b")

    assert result.returncode != 0
    assert "claim owner mismatch" in result.stderr


def test_posted_result_records_comment_url_and_worker_separately(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)

    module.record_result(str(db), 2, "posted", "worker-a", url)
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("posted", "worker-a", "posted", url)


def test_posted_result_rejects_receipt_created_before_current_claim(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    conn = sqlite3.connect(db)
    claimed_at = conn.execute(
        "SELECT updated_at FROM tasks WHERE pr = 2 AND status = 'running'"
    ).fetchone()[0]
    conn.close()
    old_created = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(claimed_at - 60)
    )
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(
        monkeypatch,
        module,
        login="Enough1122",
        html_url=url,
        created_at=old_created,
    )

    try:
        module.record_result(str(db), 2, "posted", "worker-a", url)
    except ValueError as exc:
        assert "receipt predates current claim" in str(exc)
    else:
        raise AssertionError("old receipt was accepted as a new posted result")
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a", None, None)


def test_corrected_result_rejects_receipt_created_before_current_claim(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    conn = sqlite3.connect(db)
    claimed_at = conn.execute(
        "SELECT claim_started_at FROM tasks WHERE pr = 2 AND status = 'running'"
    ).fetchone()[0]
    conn.close()
    old_created = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(claimed_at - 60)
    )
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(
        monkeypatch,
        module,
        login="Enough1122",
        html_url=url,
        created_at=old_created,
    )

    try:
        module.record_result(str(db), 2, "corrected", "worker-a", url)
    except ValueError as exc:
        assert "receipt predates current claim" in str(exc)
    else:
        raise AssertionError("old receipt was accepted as a new correction")
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a", None, None)


def test_posted_result_rejects_missing_comment_url(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0

    result = _run(db, "result", "2", "posted", "worker-a")

    assert result.returncode != 0
    assert "posted result requires a comment URL" in result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a", None, None)


def test_posted_result_rejects_mismatched_pr_comment_url(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    wrong_url = "https://github.com/NousResearch/hermes-agent/pull/999#issuecomment-1"

    result = _run(db, "result", "2", "posted", "worker-a", wrong_url)

    assert result.returncode != 0
    assert "comment URL does not match PR 2" in result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a", None, None)


def test_posted_result_rejects_third_party_receipt_author(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="whyyagswhy", html_url=url)

    try:
        module.record_result(str(db), 2, "posted", "worker-a", url)
    except ValueError as exc:
        assert "receipt author is not Enough1122" in str(exc)
    else:
        raise AssertionError("third-party receipt was accepted")
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a", None, None)


def test_posted_result_rejects_receipt_url_mismatch(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(
        monkeypatch,
        module,
        login="Enough1122",
        html_url="https://github.com/NousResearch/hermes-agent/pull/999#issuecomment-1",
    )

    try:
        module.record_result(str(db), 2, "posted", "worker-a", url)
    except ValueError as exc:
        assert "receipt URL mismatch" in str(exc)
    else:
        raise AssertionError("mismatched receipt URL was accepted")
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a", None, None)


def test_expired_claim_can_be_reclaimed(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "0").returncode == 0

    result = _run(db, "claim", "worker-b", "120")

    assert result.returncode == 0, result.stderr
    assert '"pr": 2' in result.stdout
    assert '"claimed_by": "worker-b"' in result.stdout


def test_claim_returns_empty_json_when_queue_drained(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    assert _run(db, "result", "2", "clean", "worker-a").returncode == 0
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    assert _run(db, "result", "1", "clean", "worker-a").returncode == 0

    result = _run(db, "claim", "worker-a", "120")

    assert result.returncode == 0
    assert result.stdout.strip() == "null"


def test_heartbeat_extends_only_current_owner_lease(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "0").returncode == 0

    result = _run(db, "heartbeat", "2", "worker-a", "120")

    assert result.returncode == 0, result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, lease_until FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row[0:2] == ("running", "worker-a")
    assert row[2] > 0


def test_heartbeat_rejects_wrong_owner_and_does_not_extend_lease(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "0").returncode == 0
    conn = sqlite3.connect(db)
    before = conn.execute("SELECT lease_until FROM tasks WHERE pr = 2").fetchone()[0]
    conn.close()

    result = _run(db, "heartbeat", "2", "worker-b", "120")

    assert result.returncode != 0
    assert "claim owner mismatch" in result.stderr
    conn = sqlite3.connect(db)
    after = conn.execute("SELECT lease_until FROM tasks WHERE pr = 2").fetchone()[0]
    conn.close()
    assert after == before


def test_release_returns_owned_claim_to_queue(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0

    result = _run(db, "release", "2", "worker-a", "worker exited before result")

    assert result.returncode == 0, result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, lease_until, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row[0:3] == ("queued", None, None)
    assert "worker exited before result" in row[3]
    assert row[4] is None


def test_release_rejects_wrong_owner(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0

    result = _run(db, "release", "2", "worker-b", "not owner")

    assert result.returncode != 0
    assert "claim owner mismatch" in result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", "worker-a")


def test_requeue_terminal_result_only_for_matching_owner(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 2, "posted", "worker-a", url)

    result = _run(
        db,
        "requeue",
        "2",
        "worker-a",
        "coordinator found a non-owner URL",
    )

    assert result.returncode == 0, result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, lease_until, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row[0:3] == ("queued", None, None)
    assert "non-owner URL" in row[3]
    assert row[4] is None


def test_requeue_can_atomically_replace_stale_head(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 2, "posted", "worker-a", url)

    module.requeue(
        str(db),
        2,
        "worker-a",
        reason="PR head changed after the old receipt",
        new_head_sha="a" * 40,
    )

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, head_sha, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("queued", None, "a" * 40, None)


def test_requeue_cli_accepts_reason_and_expected_new_head_pair(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    conn = sqlite3.connect(db)
    conn.execute("UPDATE tasks SET head_sha = ? WHERE pr = 2", ("b" * 40,))
    conn.commit()
    conn.close()
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 2, "posted", "worker-a", url)

    result = _run(
        db,
        "requeue",
        "2",
        "worker-a",
        "head drift",
        f"{'b' * 40}:{'a' * 40}",
    )

    assert result.returncode == 0, result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, head_sha, result FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("queued", None, "a" * 40, "resume: head drift")


def test_requeue_rejects_stale_expected_head_and_preserves_terminal_result(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 2, "posted", "worker-a", url)
    conn = sqlite3.connect(db)
    conn.execute("UPDATE tasks SET head_sha = ? WHERE pr = 2", ("b" * 40,))
    conn.commit()
    conn.close()

    try:
        module.requeue(
            str(db),
            2,
            "worker-a",
            reason="PR head changed after audit",
            expected_head_sha="c" * 40,
            new_head_sha="a" * 40,
        )
    except RuntimeError as exc:
        assert "head changed" in str(exc)
    else:
        raise AssertionError("stale expected head was accepted")

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, head_sha, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("posted", "worker-a", "b" * 40, "posted", url)


def test_requeue_rejects_wrong_owner_and_preserves_terminal_result(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 2, "posted", "worker-a", url)

    result = _run(db, "requeue", "2", "worker-b", "not owner")

    assert result.returncode != 0
    assert "claim owner mismatch" in result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, claimed_by, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("posted", "worker-a", "posted", url)


def _set_sizes(db: Path, sizes: list[tuple[int, int, int, int]]) -> None:
    conn = sqlite3.connect(db)
    for pr, files, additions, deletions in sizes:
        conn.execute(
            "UPDATE tasks SET changed_files=?, additions=?, deletions=? WHERE pr=?",
            (files, additions, deletions, pr),
        )
    conn.commit()
    conn.close()


def test_claim_fast_lane_prefers_small_task_and_deep_lane_prefers_large(
    tmp_path: Path,
) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(2, 20, 500, 0), (1, 1, 2, 0)])

    fast = _run(db, "claim", "worker-fast", "120", "fast")
    deep = _run(db, "claim", "worker-deep", "120", "deep")

    assert fast.returncode == 0, fast.stderr
    assert deep.returncode == 0, deep.stderr
    assert '"pr": 1' in fast.stdout
    assert '"pr": 2' in deep.stdout


def test_high_churn_small_pr_goes_to_deep_lane(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(1, 2, 500, 0), (2, 10, 2, 0)])

    fast = _run(db, "claim", "worker-fast", "120", "fast")
    deep = _run(db, "claim", "worker-deep", "120", "deep")

    assert fast.returncode == 0, fast.stderr
    assert deep.returncode == 0, deep.stderr
    assert '"pr": 2' in fast.stdout
    assert '"pr": 1' in deep.stdout


def test_deep_lane_avoids_head_of_line_blocking_on_xl_task(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(1, 393, 75000, 0), (2, 20, 500, 0)])

    deep = _run(db, "claim", "worker-deep", "120", "deep")

    assert deep.returncode == 0, deep.stderr
    assert '"pr": 2' in deep.stdout


def test_claim_lane_falls_back_when_its_lane_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(2, 20, 500, 0), (1, 20, 500, 0)])

    fast = _run(db, "claim", "worker-fast", "120", "fast")

    assert fast.returncode == 0, fast.stderr
    assert '"pr": 2' in fast.stdout


def test_claim_rejects_unknown_lane(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)

    result = _run(db, "claim", "worker-a", "120", "turbo")

    assert result.returncode != 0
    assert "unknown lane" in result.stderr


def test_claim_prioritizes_head_drift_requeues_over_newer_pr(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(2, 1, 2, 0), (1, 1, 2, 0)])
    conn = sqlite3.connect(db)
    conn.execute(
        "UPDATE tasks SET result=? WHERE pr=1",
        ("head changed: reviewed old; current new; re-review current diff",),
    )
    conn.commit()
    conn.close()

    result = _run(db, "claim", "worker-a", "120", "fast")

    assert result.returncode == 0, result.stderr
    assert '"pr": 1' in result.stdout


def test_metrics_reports_queue_bands_and_claim_health(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(2, 1, 2, 0), (1, 20, 500, 0)])
    assert _run(db, "claim", "worker-a", "0", "fast").returncode == 0

    result = _run(db, "metrics")

    assert result.returncode == 0, result.stderr
    payload = result.stdout.strip().splitlines()[0]
    data = json.loads(payload)
    assert data["status_counts"] == {"queued": 1, "running": 1}
    assert data["expired_claims"] == 1
    assert data["fresh_claims"] == 0
    assert data["queue_bands"]["small"] == 0
    assert data["queue_bands"]["large"] == 1


def test_metrics_uses_churn_threshold_for_queue_bands(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    _set_sizes(db, [(1, 1, 500, 0), (2, 10, 2, 0)])

    result = _run(db, "metrics")

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout.strip().splitlines()[0])
    assert data["queue_bands"] == {"small": 1, "large": 1}


def test_metrics_reports_recent_completion_throughput(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    assert _run(db, "result", "2", "clean", "worker-a").returncode == 0
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/1#issuecomment-1"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 1, "posted", "worker-a", url)

    result = _run(db, "metrics")

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout.strip().splitlines()[0])
    assert data["completed_24h"] == {
        "total": 2,
        "posted": 1,
        "clean": 1,
        "corrected": 0,
    }


def test_corrected_result_requires_and_records_owned_receipt(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-9"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)

    module.record_result(str(db), 2, "corrected", "worker-a", url)

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, result, comment_url, lease_until FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("corrected", "corrected", url, None)


def test_corrected_result_rejects_missing_comment_url(tmp_path: Path) -> None:
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0

    result = _run(db, "result", "2", "corrected", "worker-a")

    assert result.returncode != 0
    assert "corrected result requires a comment URL" in result.stderr
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, result, comment_url FROM tasks WHERE pr = 2"
    ).fetchone()
    conn.close()
    assert row == ("running", None, None)


def test_metrics_separates_corrections_from_posted_findings(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_pool_module()
    db = tmp_path / "pool.db"
    _init(db)
    assert _run(db, "claim", "worker-a", "120").returncode == 0
    url = "https://github.com/NousResearch/hermes-agent/pull/2#issuecomment-9"
    _stub_github_receipt(monkeypatch, module, login="Enough1122", html_url=url)
    module.record_result(str(db), 2, "corrected", "worker-a", url)

    result = _run(db, "metrics")

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout.strip().splitlines()[0])
    assert data["completed_24h"] == {
        "total": 1,
        "posted": 0,
        "clean": 0,
        "corrected": 1,
    }

