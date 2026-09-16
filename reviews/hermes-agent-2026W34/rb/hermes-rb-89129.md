> AI code review — automated review for reference; please use your judgment.

Careful piece of validation work: direct `@preset/<slug>` references are accepted account-scoped without a pointless `/models` probe (and the tests *forbid* that probe via AssertionError — exactly the right way to pin intent), malformed slugs are rejected before any network I/O with a clear character-class message, combined `<model>@preset/<slug>` references validate their base normally, and both auto-correct sites re-attach the preset suffix so a typo fix can't silently strip routing configuration. The negative controls (`@preset/` under plain `openai`, and under a custom-endpoint proxy) prove the shortcut doesn't leak past provider boundaries, and the subprocess test exercises the real alias→switch→validate chain end to end.

No blocking issues found.

Nit: the suffix re-attachment (`f"{auto[0]}{preset_suffix}"` / `corrected_with_suffix`) is hand-wired into two separate auto-correct return blocks; a tiny `_apply_preset_suffix(base)` closure defined next to the parse would keep a third future correction site from forgetting it. Same for the twice-repeated "URL-safe identifiers" message text — worth hoisting beside `CLARIFY`-style constants so the wording can't drift between the two rejection paths.

— Reviewed by Hermes AI reviewer (reviewer-f2)
