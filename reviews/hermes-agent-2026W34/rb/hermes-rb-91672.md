> AI code review — automated review for reference; please use your judgment.

The discover-linearly-validate-in-callback restructuring is the right shape for killing the quadratic paths, and keeping `_CFG_SECRET_WORD_RE` as an exact skip-gate preserves the fast path. Items to verify:

- agent/redact.py:878 — issue — the new callback delegates keyword validation to `_key_has_secret_keyword(name)`, which the diff does not define; the old regex embedded `_SECRET_CFG_NAMES` (`api[ _.-]?key`, etc.), which accepts the fused form `apikey` and separator variants (`api-key`, `api key`) — why it matters — if the helper tokenizes only on underscore/dot boundaries, keys like `cfg.apikey=…` or `my-api-token=…` silently stop being redacted — a real leak regression — suggestion — confirm the helper treats the fused/separated forms as hits (ideally reuse `_SECRET_CFG_NAMES` directly), and pin each variant with a test.

- agent/redact.py:884 — issue — `_redact_dotted_config` hand-rolls quote stripping and env-lookup skipping instead of calling `_redact_env` like every sibling path — why it matters — any behavior embedded in `_redact_env` beyond plain masking (minimum-length thresholds, multi-line values, future tweaks) now applies everywhere except dotted config keys, and the two paths will drift — suggestion — extract the shared mask-decision into one function used by both callbacks, or add explicit parity tests (quoted value, `os.getenv` value, short value) locking the dotted behavior to the others.

- agent/redact.py:158 — issue — the lower-env callback drops names whose *last* underscore segment is not a secret suffix, but the old alternation also matched suffix-at-start names via `(?:_|^)`; combined with the new requirement that `_` appear in the name, edge spellings like `_secret=` (leading underscore) behave differently across paths — why it matters — inconsistent treatment of near-identical spellings confuses users about what gets redacted — suggestion — add a table-driven test enumerating `_secret=`, `__key=`, `key2=`, `api_key=` and assert intended outcomes per spelling.

- tests/agent/test_redact.py:680 — issue (coverage/flakiness) — the wall-clock assertion `elapsed < 3.0` guards against quadratic blowup but can false-fail on heavily loaded CI runners even for linear code — why it matters — a flaky security test erodes trust in exactly the suite meant to protect this invariant — suggestion — keep the timing bound but make it robust (e.g., compare against a doubled-input scaling check: t(200k) < 4×t(100k) + slack), or profile operation counts via instrumentation.

No blocking issues found — item 1 is the only one with potential security impact; please verify it explicitly.

— reviewer-b (automated review)
