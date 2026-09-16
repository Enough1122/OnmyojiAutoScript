> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right contract design: replacing a presentation heuristic's scope creep with an explicit, persisted `follow_profile_config`/`room_plumbing` marker (set by session.create consumers, stamped into `model_config` by `_ensure_session_db_row`, honored by `_stored_session_runtime_overrides`) fixes the "bot DMs stuck on Nous credits" class at the identity level instead of guessing from titles. Keeping the hidden+"Group:" shape as a *legacy fallback only*, and leaving normal 1:1 stored-runtime restore untouched (including hidden non-room chats), is exactly the narrow behavior you want — and the test matrix covers marker-in-dict/marker-in-JSON/legacy-shape/unmarked-row/stamp-and-omit for both contracts.

Nit (non-blocking): tui_gateway/server.py:4154-4207 — the `room_plumbing` and `follow_profile_config` checks are two ~20-line near-identical copies of "parse model_config (dict or JSON string), read flag" plus duplicated comments; a tiny `_model_config_flag(row, key) -> bool` helper would collapse them, remove the double parse of the same JSON blob, and keep comment drift from reintroducing subtle differences between the two contracts.
