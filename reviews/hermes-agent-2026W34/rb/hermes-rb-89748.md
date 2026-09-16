> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct race analysis and fix: `call_soon_threadsafe` only *schedules*, so a pending interim put could lose to `run.completed`/sentinel enqueued directly on the loop thread the moment `run_in_executor` resolved — blocking the executor thread until the loop has actually applied each put restores the happens-before ordering, the loop-thread passthrough avoids self-deadlock, and the 2s bound keeps a dying loop from stranding the worker. The tests are exactly what this needs: an end-to-end SSE ordering regression plus unit coverage of the happens-before guarantee, same-thread passthrough, and multi-event submission order. Findings below are minor:

1. gateway/platforms/api_server.py:_enqueue_run_event — when `applied.wait(timeout=2.0)` times out, the interim event is silently dropped (identical to the pre-fix behavior, but now *after* deliberately stalling the executor thread for 2s). A single `logger.debug`/`warning` naming the run and event type on that branch would make a stalled-loop incident diagnosable instead of looking like flaky SSE gaps.
