> AI code review — automated review for reference; please use your judgment.

Correctly scoped authorization fix: the new escape hatch fires only when both sides carry non-blank *and equal* DM `chat_id`s — which is exactly the key `build_session_key` uses for such DMs — while every other shape (missing chat on either side, differing chats) keeps the original strict user-id equality check and fails closed. Mirroring the live-origin `_same_origin_chat` branch keeps the persisted fallback consistent with the session-key contract instead of inventing a third rule, and the paired test pins both the namespace-flip allow and the different-chat denial, so this is not an ownership widening.

No blocking issues found.

Nit: the 18-line inline rationale at gateway/slash_commands.py:1209-1226 nearly duplicates the test's docstring word-for-word; a one-liner pointing at #89123 (with the full story kept in the test and issue) would keep the conditional itself scannable.

— Reviewed by Hermes AI reviewer (reviewer-f2)
