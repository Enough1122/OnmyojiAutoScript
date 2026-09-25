from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "post_one.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("post_one_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _patch_post_state(
    monkeypatch,
    tmp_path: Path,
    *,
    comments,
    reviews=(),
    inline=(),
    posted_response=None,
    receipt_response=None,
):
    module = _load_module()
    pr_number = 123
    draft_dir = tmp_path / "drafts"
    draft_dir.mkdir()
    draft = draft_dir / f"{pr_number}.md"
    draft.write_text("> AI code review — automated review for reference; please use your judgment.\n\nNew finding.\n", encoding="utf-8")
    monkeypatch.setattr(module, "MD_DIRS", [str(draft_dir)])
    monkeypatch.setattr(module, "BASE", "https://api.github.test")

    posted_payload = {
        "id": 1,
        "html_url": f"https://github.com/NousResearch/hermes-agent/pull/{pr_number}#issuecomment-1",
        "user": {"login": "Enough1122"},
        "body": "> AI code review — automated review for reference; please use your judgment.\n\nNew finding.",
    }
    posted_payload.update(posted_response or {})
    receipt_payload = dict(posted_payload)
    receipt_payload.update(receipt_response or {})

    monkeypatch.setattr(module, "g", lambda url: (
        {"state": "open", "draft": False}
        if f"/pulls/{pr_number}" in url
        else receipt_payload
        if "/issues/comments/" in url
        else comments
        if f"/issues/{pr_number}/comments" in url
        else list(reviews)
        if f"/pulls/{pr_number}/reviews" in url
        else list(inline)
    ))

    posted = {}

    def _open(req, timeout=0):
        import json

        payload = json.loads(req.data.decode("utf-8"))
        posted["body"] = payload["body"]
        return SimpleNamespace(read=lambda: json.dumps(posted_payload).encode("utf-8"))

    monkeypatch.setattr(module, "urlopen", _open)
    return module, pr_number, posted


def test_existing_other_user_comment_does_not_block_new_finding(monkeypatch, tmp_path):
    module, pr_number, posted = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[{"user": {"login": "someone"}, "body": "Existing independent review."}],
    )

    result = module.post(pr_number)

    assert result.startswith("POSTED"), result
    assert "New finding." in posted["body"]


def test_existing_formal_review_and_inline_comment_do_not_block_new_finding(monkeypatch, tmp_path):
    module, pr_number, posted = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[],
        reviews=[{"user": {"login": "maintainer"}, "state": "COMMENTED"}],
        inline=[{"user": {"login": "maintainer"}, "body": "Existing inline note."}],
    )

    result = module.post(pr_number)

    assert result.startswith("POSTED"), result
    assert "New finding." in posted["body"]


def test_my_existing_different_ai_review_does_not_block_new_finding(monkeypatch, tmp_path):
    module, pr_number, posted = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[{
            "user": {"login": "Enough1122"},
            "body": "> AI code review — automated review for reference; please use your judgment.\n\nPrior independent finding.",
        }],
    )

    result = module.post(pr_number)

    assert result.startswith("POSTED"), result
    assert "New finding." in posted["body"]


def test_post_receipt_author_readback_fails_for_third_party_author(monkeypatch, tmp_path):
    module, pr_number, _ = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[],
        receipt_response={"user": {"login": "whyyagswhy"}},
    )

    result = module.post(pr_number)

    assert result.startswith("ERR"), result
    assert "read-back author" in result


def test_post_receipt_rejects_wrong_pr(monkeypatch, tmp_path):
    module, pr_number, _ = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[],
        posted_response={
            "html_url": "https://github.com/NousResearch/hermes-agent/pull/999#issuecomment-1"
        },
    )

    result = module.post(pr_number)

    assert result.startswith("ERR"), result
    assert "canonical" in result


def test_post_receipt_requires_issuecomment_fragment(monkeypatch, tmp_path):
    module, pr_number, _ = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[],
        posted_response={
            "html_url": "https://github.com/NousResearch/hermes-agent/pull/123"
        },
    )

    result = module.post(pr_number)

    assert result.startswith("ERR"), result
    assert "issuecomment" in result


def test_post_receipt_rejects_body_mismatch(monkeypatch, tmp_path):
    module, pr_number, _ = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[],
        receipt_response={"body": "different body"},
    )

    result = module.post(pr_number)

    assert result.startswith("ERR"), result
    assert "body mismatch" in result


def test_my_exact_existing_review_still_blocks_duplicate(monkeypatch, tmp_path):
    module, pr_number, posted = _patch_post_state(
        monkeypatch,
        tmp_path,
        comments=[{
            "user": {"login": "Enough1122"},
            "body": "> AI code review — automated review for reference; please use your judgment.\n\nNew finding.",
        }],
    )

    result = module.post(pr_number)

    assert result.startswith("SKIP_DUPE"), result
    assert posted == {}
