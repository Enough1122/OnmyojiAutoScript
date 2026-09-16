> AI code review — automated review for reference; please use your judgment.

Correct platform fix: comparing the *resolved* candidate against `Path("/tmp").resolve()` handles macOS's `/tmp → /private/tmp` alias without widening the rule (the `hermes-*` first-component requirement is checked on the resolved relative path, so a symlink escaping to `/etc` still fails via the same resolve). Splitting the two `except` arms so an unresolvable path fails closed is also right, and the macos-only test binds a real `/tmp` directory rather than mocking the alias.

— reviewer-b (automated review)

No blocking issues found.
