> AI code review — automated review for reference; please use your judgment.

Correct fix for a subtle cancellation cycle (poll → fatal handler → disconnect → cancels poll → recovery aborted): detecting "am I the poll task" and handing recovery to an independently-owned task with done-callback bookkeeping is exactly right, and the integration test drives the *real* runner to prove WhatsApp reaches the reconnect queue with attempts=0 while `runner.stop` stays untouched. Keeping the inline await for non-poll callers preserves existing semantics. Nothing to add.

— reviewer-b (automated review)

No blocking issues found.
