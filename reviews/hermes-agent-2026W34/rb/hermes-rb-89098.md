> AI code review — automated review for reference; please use your judgment.

Tidy opt-out: the guard sits before any work in `_restore_session_model`, honors both `resume.restore_model: false` and a bare `resume: false` scalar, keeps the documented precedence intact (`-m` still wins over everything), and avoids the twin-defaults trap — `cli.py` reads with a `.get(..., True)` fallback instead of duplicating the default from `config_defaults.py`. The dashboard schema entry plus the one-field-category fold into `general` follows the exact precedent set by `session.terminal_continue`, comment included.

No blocking issues found.

Nit: the two new tests cover dict-shaped configs only — the `elif resume_cfg is False` scalar-shorthand branch has no coverage (and an explicit `resume: null` currently falls through to *enabled*, which may or may not be intended for users who write bare keys). One parametrized case over `False / True / None / {"restore_model": false}` would pin all four shapes before someone "simplifies" the branch away.

— Reviewed by Hermes AI reviewer (reviewer-f2)
