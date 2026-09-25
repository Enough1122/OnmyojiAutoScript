from __future__ import annotations

from pathlib import Path

SCRIPTS = [
    Path(__file__).resolve().parents[1] / "scripts" / "run_chunk3_continue.py",
    Path(__file__).resolve().parents[1] / "scripts" / "run_chunk3_99116.py",
    Path(__file__).resolve().parents[1] / "scripts" / "run_chunk4_continue.py",
]


def test_retired_legacy_publishers_have_guard_before_external_setup() -> None:
    for script in SCRIPTS:
        source = script.read_text(encoding="utf-8")

        guard_at = source.index("RETIRED")
        token_load_at = source.index("TOKEN = load_token()")

        assert guard_at < token_load_at
        assert "raise SystemExit" in source[guard_at:token_load_at]
        assert "review_pool.py" in source[guard_at:token_load_at]

