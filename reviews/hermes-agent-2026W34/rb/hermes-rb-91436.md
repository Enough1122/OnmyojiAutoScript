> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Good root-cause work: routing drafts through `_thread_kwargs_for_send` fixes the string-vs-int `message_thread_id` rejection (and quietly removes an `int(thread_id)` ValueError waiting on non-numeric ids in `_try_send_rich_draft`), while the scoped `prefers_fresh_final_streaming` escape hatch gives degraded DM-topic turns a way to persist native tables instead of the bullet-list rewrite. The three new tests map cleanly onto report/happy/degraded paths. Findings:

1. plugins/platforms/telegram/adapter.py:1630 — `_thread_kwargs_for_draft` now forwards reply-routing kwargs (`reply_to_message_id` / reply parameters) into `sendMessageDraft`/`sendRichMessageDraft` payloads, but all new tests assert against mocked bots, so nothing verifies the real Bot API accepts those fields on *draft* endpoints. If Telegram rejects unknown/reply params there, every topic turn with a reply-to would fail drafts outright — recreating exactly the degradation this PR fixes. Suggestion: canary-check the two draft endpoints with reply kwargs (or strip reply keys from the draft payload until confirmed), and add a test pinning whichever decision you make.

2. plugins/platforms/telegram/adapter.py:2110 — enabling fresh-final reintroduces the brief duplicate-message flash that #46206 originally reverted, just narrowed to DM-topic-degraded turns. Acceptable tradeoff, but invisible when it fires; consider a debug log (or counter) when the topic fallback triggers so support can correlate user reports of double finals with this path.

3. plugins/platforms/telegram/adapter.py:1626 — `getattr(self, "_reply_to_mode", None)` papers over subclasses/instances lacking `_reply_to_mode`; if that attribute exists on the normal send path but resolves to None here, preview and final routing can disagree about reply placement mid-turn. Prefer reading the same attribute the send path reads (with a single shared accessor) so both paths can't drift.
