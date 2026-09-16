> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: `'moa'` is now hardcoded inside the otherwise-generic helper. One virtual provider is fine; when the second one appears (a `default_routing`-style aggregate would qualify), promote this to an exported VIRTUAL_PROVIDERS set with a comment on why absence is authoritative for them specifically. The populated-catalog guard keeping unavailable/empty catalogs non-destructive is the important invariant, and both sides of it are pinned by tests.

— Reviewed by Hermes AI reviewer (reviewer-f)
