> AI code review — automated review for reference; please use your judgment.

Clean, minimal escape hatch with unusually thorough tests (whitespace and casing variants included). Only polish-level items:

- cli.py:4283 — issue (discoverability/docs) — the new `HERMES_DISABLE_EXTENDED_KEYS` flag ships without any documentation change (website troubleshooting guide, README, or `hermes doctor` output) — why it matters — the exact users who need it are those whose terminal is already misbehaving under CJK IMEs; they will not read release notes, and #91624-style reports will keep arriving as duplicates — suggestion — add a short entry to the terminal-troubleshooting docs and, ideally, have doctor print the variable name when it detects WezTerm/WSL2 alongside a non-ASCII input complaint.

- cli.py:4284 — issue (consistency) — the truthy set {`1`,`true`,`yes`,`on`} is parsed inline; other Hermes env toggles may use a shared boolean-env helper or accept different word lists — why it matters — diverging spellings across flags (`y`? `enable`? bare-set-means-on?) trains users into wrong habits and invites bug reports like "I set it to YES and nothing happened" — suggestion — reuse the existing env-boolean parser if one exists (or extract one) so all Hermes toggles agree on accepted values.

- cli.py:4277 — nit — the docstring documents the enable-spellings implicitly but not the falsy contract (`0`/`false`/`off`/empty deliberately do *not* opt out); one sentence would preempt "why doesn't =0 disable?" confusion since several tools treat any non-empty value as true.

No blocking issues found. Behavior itself looks exactly right, including returning before any bytes are written so the exit-side reset stays balanced.

— reviewer-b (automated review)
