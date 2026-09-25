from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "post_batch.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("post_batch_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_post_batch_delegates_each_pr_to_post_one(monkeypatch):
    module = _load_module()
    calls = []

    def fake_post(pr, sleep_secs):
        calls.append((pr, sleep_secs))
        return f"POSTED {pr} https://github.com/NousResearch/hermes-agent/pull/{pr}#issuecomment-1"

    monkeypatch.setattr(module.post_one, "post", fake_post)

    pr, status = module._one(123)

    assert pr == 123
    assert status.startswith("POSTED 123")
    assert calls == [(123, 0.0)]
