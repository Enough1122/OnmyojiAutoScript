> AI code review — automated review; please use your judgment.

1. `agent/chat_completion_helpers.py:~936–951` (`_create_with_data_envelope_unwrap`) — switching every non-MOA provider to `with_raw_response.create()` **disables the SDK's automatic HTTP-error raising**: a 400/401/429/500 now arrives as a raw response whose JSON (e.g. ````{"error": {...}}````) fails the envelope check, flows into `ChatCompletion.model_validate`, and surfaces as a `ValidationError` instead of `APIStatusError` with its status code — why it matters: the whole failover/retry stack classifies failures off those exceptions (rate-limit backoff, auth recovery, overflow routing); this silently converts every upstream HTTP error into an unclassifiable validation failure for all OpenAI-wire providers, far beyond the envelope quirk being fixed — suggestion: after fetching the raw response, check `raw_response.status_code` and call `raw_response.parse()` (which raises the canonical SDK error) when it's >= 400 before doing any envelope logic; add tests asserting a 429 raw body still raises the SDK error type.

2. Test gap (`tests/test_data_envelope_unwrap.py`): no case covers a non-2xx raw response, which is exactly the hole in item 1 — also ````json.loads(getattr(raw_response, "text", ""))```` swallowing *every* exception means a truncated/HTML error page becomes `{}` → confusing ValidationError; distinguishing empty-body-from-error vs success shapes would make failures legible.

3. Nit: new test file lacks a trailing newline at EOF.

The envelope detection itself is nicely conservative ("choices" absent + dict `data` present, no-op otherwise) and rebuilding via `ChatCompletion.model_validate` gives downstream real choices — the mechanism is fine; it just must not eat HTTP errors on the way.

— reviewer-a · automated agent review (Hermes week-review)
