> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: `_credential_env_hint` swallows registry lookup failures with a bare `except Exception: pass`. The synthesized fallback keeps the message sane, so this is cosmetic — but a logger.debug there would distinguish "provider genuinely unknown" from "registry import broke" when someone debugs why hints regressed. Both sync and async error paths were updated consistently, and the test set covers the real regression (#89516), the underscore-vs-hyphen synthesis trap, and the never-raises contract.

— Reviewed by Hermes AI reviewer (reviewer-f)
