> AI code review — automated review for reference; please use your judgment.

1. `plugins/platforms/a2a/tools.py:~158–164` — the new comment promises "`0` **or null** ⇒ indefinite", but `timeout: null` in YAML hits `int(None)` → `TypeError` → falls back to `_DEFAULT_TIMEOUT`, i.e. *not* indefinite — why it matters: a user following the comment writes `timeout:` (empty) expecting an unbounded wait and gets a 300s cutoff with nothing explaining the gap — suggestion: handle it explicitly (`if raw_timeout is None: timeout = None`) before the `int()` attempt, or correct the comment to match the docs ("0 ⇒ indefinite").

2. `plugins/platforms/a2a/tools.py:~160–166` — negative values sail through the new normalization (`timeout: -1` → `-1`) and reach the socket layer, where behavior is undefined/exception-dependent; the old code had the same hole, but this hunk is exactly where a clamp belongs — suggestion: treat `raw_timeout < 0` like a malformed value (fall back to `_DEFAULT_TIMEOUT`).

3. Nit (`:165`): `raw_timeout in (0, None)` — after the `int()` conversion the `None` member is unreachable (the failure path substitutes the default); dropping it (or restructuring per item 1) makes the sentinel handling honest.

Otherwise solid: capping the card fetch at 30s independently of an indefinite task wait is the right split (dead peers still fail fast), and the docs addition clearly explains the semantics with a realistic example.

— reviewer-a · automated agent review (Hermes week-review)
