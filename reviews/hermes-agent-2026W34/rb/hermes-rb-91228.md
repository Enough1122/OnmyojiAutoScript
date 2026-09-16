> AI code review — automated review for reference; please use your judgment.

Right fix for #91221, and the tests pin exactly the two layers (inner conversion vs. gather containment). One real edge case and two smaller points:

1. agent/context_references.py:284 — the comment promises "CancelledError/KeyboardInterrupt must keep propagating", but the code doesn't do that. `asyncio.CancelledError` and `KeyboardInterrupt` are `BaseException`, not `Exception`, so a cancelled child coroutine's outcome fails the `isinstance(outcome, Exception)` branch and falls through to `warning, block = outcome` — which raises `TypeError` (can't unpack an exception instance) instead of propagating cancellation. Suggested shape:

   ```python
   if isinstance(outcome, BaseException):
       if not isinstance(outcome, Exception):
           raise outcome
       warnings.append(...)
       continue
   ```

   or invert: handle `Exception` first, then `raise` any remaining `BaseException`. As written, cancellation inside a sibling corrupts the batch with an unrelated TypeError.
2. context_references.py:286 — the containment warning keeps only `outcome.__class__.__name__`; the actual reason (`str(outcome)`) is dropped, so an escaped failure is undebuggable from logs. Consider appending a truncated `str(outcome)` (e.g. 200 chars) — the inner path already surfaces full messages.
3. tests/test_context_refs_failure_isolation.py — great coverage of escape-containment and all-fail; consider one more test where a sibling raises `asyncio.CancelledError` to pin the propagation semantics from item 1 once fixed. (nit)

No blocking issues found beyond item 1 — it's an edge case, but it converts a rare cancellation into a confusing crash, which is what this PR set out to eliminate.
