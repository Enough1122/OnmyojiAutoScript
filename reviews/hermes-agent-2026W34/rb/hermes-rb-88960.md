> AI code review — automated review for reference; please use your judgment.

Excellent root-cause analysis: the estimator's flat per-image pricing is exactly why text compression structurally cannot clear an image-dominated 413, and measuring actual payload bytes is the correct recovery driver. Persisting the strip into stored history (so the fix survives future turns), protecting the most recent N messages, and preserving tool_call_id linkage via placeholder are all thoughtful. One correctness gap:

1. agent/message_sanitization.py:`strip_oversized_image_parts` (~470) — when a **non-tool** message (typically `role:"user"`) loses all its parts, it's *deleted outright* rather than replaced with a placeholder like the tool case. A `[user(image), assistant(reply)]` pair then becomes `[assistant(reply)]`: possible double-assistant adjacency with earlier history, or a transcript that starts with an assistant row after later truncation — several providers hard-reject both. Mirror the tool treatment (plaintext "[image removed]" placeholder) for user/system roles too, or verify every target provider tolerates the reshaped alternation.
2. The recovery fires only on "compression scored no progress"; if compression *does* make progress but the remaining payload still exceeds the limit, each attempt burns budget before reaching here. Consider checking measured image bytes up front when a 413 arrives, so the first retry already strips. (nit)
3. `protect_last_n` shields messages, not images — a user's just-attached screenshot within the protected window makes the strip a no-op (`changed=False`), correctly falling through to the existing tool-message stripper below. Worth one comment noting that fall-through is intentional. (nit)
4. The tests asserting the bytes-driven invariant (flat-estimate scenario must still recover) are exactly right. (positive)

No blocking issues found beyond item 1's alternation risk.
