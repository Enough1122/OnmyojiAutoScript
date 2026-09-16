> AI code review — automated review; please use your judgment.

Right call extracting the predicate (`_should_send_auto_reset_notice` is now unit-testable without a runner), and suppressing email reset notices matches how that channel behaves (batched/delayed delivery makes "your session was just reset" notices arrive uselessly late).

1. `gateway/config.py:~550, ~583` — adding `"email"` only changes the **default**; any user who has ever written a custom `notify_exclude_platforms` list keeps their old list and continues receiving email reset notices after upgrade — why it matters: the bug report this fixes will resurface for exactly the operators who customized anything — suggestion: note in the changelog ("add 'email' to your notify_exclude_platforms if you've customized it"), or union `email` into user-provided lists once as a migration.

2. Nit: the default tuple ````("api_server", "webhook", "email")```` now exists in three places (class attribute, `from_dict` fallback, and the new test) — a module-level `DEFAULT_NOTIFY_EXCLUDE_PLATFORMS` constant would keep them from drifting.

Also worth stating explicitly in the PR body: this makes platform exclusion **absolute** — previously suspended/`resume_pending_expired` resets notified even excluded platforms by design ("the user had an active session silently replaced"). The new tests pin the stricter semantics deliberately; just make sure that intent reversal is acknowledged as intended rather than incidental.

— reviewer-a · automated agent review (Hermes week-review)
