from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load_module(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run_bad_receipt_main(
    monkeypatch,
    tmp_path: Path,
    capsys,
    module_name: str,
    *,
    posted_response: dict | None = None,
    receipt_response: dict | None = None,
) -> tuple[int, str]:
    module = _load_module(module_name)
    pr_number = 123
    comment_id = 7
    body = "> AI code review — automated review for reference; please use your judgment.\n\nFinding."
    draft = tmp_path / f"{pr_number}.md"
    draft.write_text(body, encoding="utf-8")
    posted = {
        "id": comment_id,
        "html_url": (
            "https://github.com/NousResearch/hermes-agent/"
            f"pull/{pr_number}#issuecomment-{comment_id}"
        ),
        "user": {"login": "Enough1122"},
        "body": body,
    }
    posted.update(posted_response or {})
    receipt = dict(posted)
    receipt.update(receipt_response or {})

    def fake_g(url):
        if f"/issues/{pr_number}/comments" in url:
            return []
        if f"/issues/comments/{comment_id}" in url:
            return receipt
        raise AssertionError(f"unexpected GET {url}")

    class _Response:
        @staticmethod
        def read():
            return json.dumps(posted).encode("utf-8")

    monkeypatch.setattr(module, "MD_DIR", str(tmp_path))
    monkeypatch.setattr(module, "g", fake_g)
    monkeypatch.setattr(module, "urlopen", lambda request, timeout=0: _Response())
    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(module.sys, "argv", [module_name, str(pr_number)])

    exit_code = 0
    try:
        module.main()
    except SystemExit as exc:
        exit_code = int(exc.code or 0)
    return exit_code, capsys.readouterr().out.strip()


@pytest.mark.parametrize("module_name", ["post_review", "post_followup"])
def test_legacy_publisher_rejects_wrong_pr_receipt(
    monkeypatch, tmp_path, capsys, module_name
):
    exit_code, output = _run_bad_receipt_main(
        monkeypatch,
        tmp_path,
        capsys,
        module_name,
        posted_response={
            "html_url": (
                "https://github.com/NousResearch/hermes-agent/"
                "pull/999#issuecomment-7"
            )
        },
    )

    assert exit_code == 4
    assert "canonical issuecomment" in output
    assert not output.startswith("POSTED")


@pytest.mark.parametrize("module_name", ["post_review", "post_followup"])
def test_legacy_publisher_requires_issuecomment_fragment(
    monkeypatch, tmp_path, capsys, module_name
):
    exit_code, output = _run_bad_receipt_main(
        monkeypatch,
        tmp_path,
        capsys,
        module_name,
        posted_response={
            "html_url": "https://github.com/NousResearch/hermes-agent/pull/123"
        },
    )

    assert exit_code == 4
    assert "canonical issuecomment" in output
    assert not output.startswith("POSTED")


@pytest.mark.parametrize("module_name", ["post_review", "post_followup"])
def test_legacy_publisher_rejects_body_mismatch(
    monkeypatch, tmp_path, capsys, module_name
):
    exit_code, output = _run_bad_receipt_main(
        monkeypatch,
        tmp_path,
        capsys,
        module_name,
        receipt_response={"body": "different body"},
    )

    assert exit_code == 4
    assert "body mismatch" in output
    assert not output.startswith("POSTED")
