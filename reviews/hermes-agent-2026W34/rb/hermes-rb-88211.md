> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Small, deliberate change: both send paths now use force_push=True so system/agent outputs reach the user as visible bubbles instead of riding the reply token, which fixes deliveries silently vanishing when the reply token was stale or consumed by the postback cache. The pending-postback branch is intentionally left untouched, which is right - that path exists precisely to hold responses behind a button tap.

Nit: force_push drops the reply-threading context in the LINE UI, so users lose the visual "this message answers that message" linkage the reply token provided. If that linkage mattered for cron digests, a follow-up could try push-with-quote; otherwise fine as-is.