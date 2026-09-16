> AI code review — automated review for reference; please use your judgment.

Correct allowlist addition — Alacritty implements both the Kitty keyboard protocol and modifyOtherKeys — and threading an optional `terminal` parameter into `supportsExtendedKeys` is the right testability move without touching callers. Points:

1. ui-tui/.../terminal.ts:~321 — matching is **case-sensitive exact** against `env.terminal`. Alacritty identifies itself via `TERM=alacritty` (lowercase) rather than a `TERM_PROGRAM` value in most setups, while the list also contains mixed-case entries like `iTerm.app`. Please confirm which environment variable `env.terminal` actually reads and that its real-world casing for each listed terminal matches these strings exactly — otherwise the new entry (and possibly others) never matches in practice. A case-insensitive comparison would make the whole list robust.
2. The new test covers the true/false branches of the function itself; consider one integration assertion that the extended-keys init sequence is actually written when running under an Alacritty-like env, since allowlist membership alone doesn't prove the flag reaches the terminal setup path. (nit)

No blocking issues found beyond confirming item 1's variable/casing reality.
