> AI code review — automated review for reference; please use your judgment.

This is what an auth-surface extension should look like: exact-path rules that fail closed on conflicts, scope enforcement with a distinct 403 *and* `token_authenticated=False` so downstream gates can't be fooled, loopback checks that treat DNS as a non-boundary and ignore `X-Forwarded-For`, constant-time comparisons everywhere, provider-registration reordered after route registration so a failed seam can't leave a half-enabled credential, and mounted end-to-end tests covering cross-service 403s, non-loopback fallback, and write-refusal. Genuinely strong. Items:

- hermes_cli/dashboard_auth/token_auth.py:186 — issue (verification) — `is_token_route(path)` without a method still answers True for a route whose rule is method-scoped, while the actual middleware now falls through for other methods — why it matters — any remaining caller of the two-arg-era signature (route bookkeeping, diagnostics, or a second auth layer deciding "this path is token-handled, skip me") will act on stale semantics exactly where methods matter most — suggestion — grep all `is_token_route(` call sites and either migrate them to pass `request.method` or rename the legacy shape (`is_token_route_path`) so the compiler finds stragglers.

- hermes_cli/dashboard_auth/token_auth.py:263 — nit — `authenticate_token`'s contract grew a subtle case (a recognized-but-under-scoped principal is returned instead of None, relying on the caller to 403); today the middleware is the only caller and re-checks the scope anyway, so behavior is right, but the doubled check invites drift — suggestion — document the "caller must enforce" contract in the docstring bullet list explicitly, or drop the pre-filter inside `authenticate_token` and let the middleware own scoping entirely.

No blocking issues found — item 1 is a quick audit.

— reviewer-b (automated review)
