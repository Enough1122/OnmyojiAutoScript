from __future__ import annotations

import builtins
import io
import json
import re
import runpy
import sys
import urllib.request
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "diffs_batch115.py"


def test_large_diff_is_saved_and_included_for_deep_review(
    monkeypatch, tmp_path: Path
) -> None:
    real_open = builtins.open
    list_path = tmp_path / "batch.json"
    final_path = tmp_path / "final.json"
    out_dir = tmp_path / "campaign"
    list_path.write_text("[123]\n", encoding="utf-8")

    def fake_open(path, *args, **kwargs):
        if str(path).lower().endswith("\\.env"):
            return io.StringIO("GITHUB_TOKEN=test-token\n")
        return real_open(path, *args, **kwargs)

    class Response:
        def read(self):
            return b"x" * 120_000

    def fake_urlopen(request, timeout=0):
        return Response()

    source = SCRIPT.read_text(encoding="utf-8")
    source = re.sub(
        r"^OUT = .*?$",
        f"OUT = r'{out_dir.as_posix()}'",
        source,
        count=1,
        flags=re.MULTILINE,
    )
    script_copy = tmp_path / "diffs_batch115_under_test.py"
    script_copy.write_text(source, encoding="utf-8")
    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(sys, "argv", [str(script_copy), str(list_path), str(final_path)])

    runpy.run_path(str(script_copy), run_name="__main__")

    assert json.loads(final_path.read_text(encoding="utf-8")) == [123]
    assert (out_dir / "123.diff").read_bytes() == b"x" * 120_000
