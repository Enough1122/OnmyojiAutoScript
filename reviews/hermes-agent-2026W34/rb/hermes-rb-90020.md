> AI code review — automated review for reference; please use your judgment.

Strong at-most-once→at-least-once correction across all three notification paths (kanban batches, delegation completions, shutdown drain): a `False` return from `_run_prompt_submit` now releases the claim and defers instead of acknowledging away the only copy, the kanban batch is restored *ahead* of newer pending entries preserving order, and the poller thread now binds HERMES_HOME to the session's profile with an unusually well-argued comment explaining why the propagate-context idiom fails at this spawn site. Tests drive the real thread against per-profile DBs and prove the launch home stays untouched. Items:

- tui_gateway/server.py:10085 — issue (verification) — the kanban path sets `_restore_batch = True` on *any* exception from `_run_prompt_submit`, but an exception raised **after** the turn actually started (mid-turn crash propagating out) means the notification was already being delivered; re-queueing then double-delivers on retry — why it matters — the whole PR distinguishes "rejected before start" from "delivered"; the exception arm currently conflates them — suggestion — confirm `_run_prompt_submit` can only raise pre-turn, or return a tri-state (started / rejected-before-start / error) so the retry decision is explicit.

- tui_gateway/compute_host.py:607 — nit — good catch passing `profile_home` before the poller thread starts; consider asserting in `_start_notification_poller` that `_session_home(session)` resolves non-empty, so a future caller that forgets the field fails loudly in tests rather than silently claiming against the launch profile again.

No blocking issues found — item 1 wants a definitive answer about the mid-turn exception shape.

— reviewer-b (automated review)
