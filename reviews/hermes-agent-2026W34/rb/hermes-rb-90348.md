> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct root-cause fix: a handoff thread the bot itself created was invisible to the thread registry, so follow-up replies inside it were gated by channel-level mention policy and silently dropped under REQUIRE_MENTION. The try/except/**else** restructure puts `_threads.mark` exactly where success is proven on both creation paths (direct and seed-message fallback), keeps failure paths mark-free, and three gateway tests pin mark-once/no-seed-send-on-direct/failure-doesn't-mark, plus an end-to-end test proving an unmentioned reply in a freshly created handoff thread is now admitted. Findings below are minor:

1. plugins/platforms/discord/adapter.py:7391 — `_threads.mark(thread_id)` sits unprotected inside the `else` block: if the registry write ever raises (disk-backed store, unexpected shape), the function throws *after* Discord already created the thread — callers see an exception instead of a usable id, and the fallback path never runs despite the direct creation having succeeded. Wrapping the two `mark` calls in a log-and-continue keeps thread creation authoritative over bookkeeping.

2. tests/e2e/test_discord_adapter.py — the e2e test asserts admission via `handle_message` being awaited, but nothing asserts the negative control (an unmentioned reply in an *untracked* thread still rejected), which is the behavior this fix is supposed to change; one assertion there would guard against the registry check being loosened globally later.
