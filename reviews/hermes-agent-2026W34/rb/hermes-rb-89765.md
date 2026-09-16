> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Closes an honest-feedback hole: a streamed reply claiming "report attached" followed by a silent safety-filter rejection looked identical to success on Slack. The fix tracks `delivery_failed` across all three sources of truth (boundary-filtered paths, `success: False` results, raised exceptions), sends exactly one generic notice that provably never contains the rejected path (asserted in every failure-mode test), and pairs it with a system-prompt change steering the model toward the approved `$HERMES_HOME/cache/documents` cache plus an explicit "do not claim it was delivered" honesty rule — fixing both the reporting *and* one cause. The URL-quoting correction in the existing test (`file://{quote(...)}`) is a nice bonus catch. Findings below are minor:

1. gateway/run.py:22066 — the notice is gated to `Platform.SLACK`, so the identical silent-rejection UX remains on Telegram/Discord/etc.; presumably intentional scoping for this PR, but a one-line TODO/comment naming the follow-up would keep the asymmetry from looking like an oversight six months from now.
