> AI code review — automated review for reference; please use your judgment.

1. `hermes_cli/runtime_provider.py:~712–717` (`_bare_custom_result`) — when several custom endpoints are configured, a bare `provider: "custom"` now silently binds to **whichever entry scans first**, and requests/credentials flow there — why it matters: "first in config order" is an invisible contract; a user adding one more provider above the existing one changes where every bare-`custom` cron job sends its traffic with zero warning — suggestion: `logger.warning("provider 'custom' resolved to first configured endpoint %r; use provider: 'custom:%s' to pin", ...)` on the fallback path so the guess is observable and self-documenting.

2. `hermes_cli/runtime_provider.py:~870–872` — the fallback recurses via `_get_named_custom_provider(first_custom_alias)`; termination currently rests on the assumption that `custom_provider_slug(...)` can never produce the literal string `"custom"` — why it matters: a provider literally named to collide would recurse unboundedly inside resolution — suggestion: one cheap guard (`if first_custom_alias and first_custom_alias != requested_norm:`) plus a comment makes the invariant enforced instead of implied.

3. `hermes_cli/runtime_provider.py:~832–835` vs `~779–784` — the two scan passes capture `first_custom_alias` under different completeness rules (URL-only vs name+URL), so which entry becomes "first" can differ depending on whether the config uses the legacy inline format or `custom_providers:` — why it matters: same config shape change could silently re-point the bare-`custom` fallback even with identical logical entries — suggestion: unify the candidacy predicate into one small helper both loops share.

Nit: `_bare_custom_result` closes over `first_custom_alias` mutated later in the function body — correct in Python but easy to misread; computing the fallback explicitly after the scans (`if bare_custom_fallback and first_custom_alias: ...`) would read more honestly than a closure over a not-yet-assigned variable.

Overall: fixes a real, well-diagnosed regression (cron jobs with `provider: "custom"` auth-failing against Codex) while carefully preserving the base_url trust path when nothing is configured; the new test covering scoped-key resolution through the public `resolve_provider_client` entry point is exactly right. Item 1 is worth doing before merge since it's three lines.

— reviewer-a · automated agent review (Hermes week-review)
