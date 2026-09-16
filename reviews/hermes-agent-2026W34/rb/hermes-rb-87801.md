> AI code review — automated review; please use your judgment.

Correct one-line semantic fix: plugin `send_message_handler`s exist to intercept *model-initiated* sends (which always carry structured `args`), so requiring truthy `args` cleanly separates that lane from cron/standalone deliveries that call `_send_to_platform` directly with `args=None` — which previously got hijacked by an installed handler and never reached the adapter. The regression test proves both halves: handler not called for the cron-shaped call, and the normal adapter path succeeding.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
