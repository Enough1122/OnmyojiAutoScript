from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "preflight_batch.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("preflight_batch_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_missing_cached_diff_is_not_a_deferred_terminal_result() -> None:
    module = _load_module()

    result = module.missing_diff_result(123)

    assert result["apply_err"] == "diff-not-cached"
    assert "deferred" not in json.dumps(result)
