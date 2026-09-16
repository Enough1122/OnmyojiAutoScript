> AI code review — automated review for reference; please use your judgment.

Nicely judged split: bare commands get full `strip()` (Slack's thread composer happily appends newlines after a lone `!reset`), while parameterized commands only lose `\r\n` padding so the existing guarantee that argument whitespace is preserved stays intact — the two behaviors are deliberately different and the code comments say why. The parametrized test covers LF, CRLF, double-newline, mixed trailing spaces, *and* retains the historical leading-space case from the deleted test, so nothing regressed silently.

No blocking issues found.

Nit: this composer-padding normalization is almost certainly not Slack-specific — Telegram and Discord mobile composers exhibit the same trailing-newline behavior, and their adapters will want the identical bare-vs-parameterized rule. Worth hoisting into a small shared helper (e.g. `normalize_command_padding(text) -> str` next to the other command-probe utilities) now while there's exactly one caller, rather than copy-pasting the branch per adapter later.

— Reviewed by Hermes AI reviewer (reviewer-f2)
