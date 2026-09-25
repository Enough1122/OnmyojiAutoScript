from __future__ import annotations

import builtins
import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "count_candidates.py"


def _load_module(monkeypatch: pytest.MonkeyPatch):
    real_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if str(path).lower().endswith("\\.env"):
            return io.StringIO("GITHUB_TOKEN=test-token\n")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)
    spec = importlib.util.spec_from_file_location("count_candidates_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    pr: dict,
    reviews: list[dict],
) -> tuple[dict, dict]:
    module = _load_module(monkeypatch)
    state_path = tmp_path / "state.json"
    out_path = tmp_path / "snapshot.json"
    state_path.write_text(
        json.dumps({"frontier": 100, "deferred": [99]}), encoding="utf-8"
    )
    module.STATE = str(state_path)
    module.OUT = str(out_path)

    def fake_get(url: str, retries: int = 3):
        if "/pulls?" in url:
            return ([{"number": pr["number"]}], "")
        if url.endswith(f"/pulls/{pr['number']}/reviews"):
            return (reviews, "")
        if url.endswith(f"/pulls/{pr['number']}"):
            return (pr, "")
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(module, "get", fake_get)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "100"])
    module.main()

    snapshot = json.loads(out_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    return snapshot, state


def test_existing_attention_stays_eligible_for_semantic_deduplication(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    snapshot, _state = _run_snapshot(
        monkeypatch,
        tmp_path,
        {
            "number": 123,
            "title": "already reviewed",
            "draft": False,
            "comments": 2,
            "review_comments": 1,
            "changed_files": 3,
            "additions": 20,
            "deletions": 5,
            "created_at": "2026-09-25T00:00:00Z",
        },
        [{"id": 1}, {"id": 2}],
    )

    row = snapshot["rows"][0]
    assert row["eligible"] is True
    assert row["lane"] == "fast"
    assert row["deferred"] is False


def test_large_diff_stays_eligible_in_deep_lane_and_preserves_deferred_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    snapshot, state = _run_snapshot(
        monkeypatch,
        tmp_path,
        {
            "number": 124,
            "title": "large change",
            "draft": False,
            "comments": 0,
            "review_comments": 0,
            "changed_files": 20,
            "additions": 200,
            "deletions": 60,
            "created_at": "2026-09-25T00:00:00Z",
        },
        [],
    )

    row = snapshot["rows"][0]
    assert row["eligible"] is True
    assert row["lane"] == "deep"
    assert row["deferred"] is False
    assert snapshot["deferred"] == []
    assert state["deferred"] == [99]
