> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Nicely scoped acknowledgment feature: the `reaction_only` set grants zero prompt/dispatch authority — an event must be *both* explicitly p-tagged to this bot *and* contain a mention before even the 👀 fires, unknown senders get nothing, and every path still terminates in the unauthorized-ignore branch. The three tests map exactly onto those boundaries (reacts+no-dispatch, no-tag-no-reaction, stranger-no-reaction), and the YAML/env plumbing mirrors the adjacent `BUZZ_ALLOWED_USERS` pattern faithfully.

Nit (non-blocking): plugins/platforms/buzz/adapter.py:415 — document the precedence when a pubkey appears in **both** `allowed_users` and `reaction_only_users`: the allow-list check runs first, so such an agent gets full dispatch rights and the reaction-only intent is silently ignored. Either reject that configuration at init with a warning or state the allowlist-wins rule in the config docs so operators don't mistake reaction_only for a restriction.
