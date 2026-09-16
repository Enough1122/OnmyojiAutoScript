> AI code review — automated review for reference; please use your judgment.

1. gateway/stream_consumer.py:2110 — `_send_commentary` registers interim ids via `getattr(result, "message_id", None)`, which only handles attribute-style send results. Why it matters: an adapter whose `send()` returns a plain dict would silently skip cleanup registration, leaving stray bubbles exactly where this feature promises removal. Suggestion: normalize first, e.g. `mid = result.get("message_id") if isinstance(result, dict) else getattr(result, "message_id", None)`.

2. gateway/run.py:5473 — the `on_temporary_message` lambda dereferences `ctx._cleanup_msg_ids` unguarded. Why it matters: if init order ever changes so the list doesn't exist while `cleanup_progress` is enabled, the AttributeError is swallowed by the debug-level handler in `_notify_temporary_message` and cleanup quietly stops working. Suggestion: create-on-demand (`ctx._cleanup_msg_ids = getattr(ctx, "_cleanup_msg_ids", [])`) or append via a small helper.

3. tests/gateway/test_run_cleanup_progress.py:334 — `_fire_cleanup` polls at most ~200 ms (20 x 10 ms) for `adapter.deleted` to populate. Why it matters: deletion happens after an async callback hop, so a loaded CI runner can exceed the poll window and fail intermittently even though the code is correct. Suggestion: have CleanupCaptureAdapter signal an `asyncio.Event` when `delete_message` fires and await that instead of sleep-polling.

4. gateway/stream_consumer.py:600 / gateway/run.py:5473 — the message id is stringified twice (`cb(str(message_id))` plus `str(mid)` in the lambda). This is a nit — harmless, but keep conversion in one layer so the callback contract stays "receives platform-native id".

5. website/docs/user-guide/messaging/slack.md:85 — the docs now state `chat:write` covers `chat.delete` for these bubbles but don't say what happens when a delete fails (rate limit, already deleted). Why it matters: users enabling `cleanup_progress` will expect bubbles gone; partial failures are invisible to them. Suggestion: add one sentence noting leftovers after failed deletes are benign, or log delete errors above debug level.

Test coverage is solid: success path, failed-run breadcrumb path, and a consumer-level callback unit test are all included.
