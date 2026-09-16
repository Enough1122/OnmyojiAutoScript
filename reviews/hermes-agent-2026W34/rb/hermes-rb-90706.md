> AI code review — automated review for reference; please use your judgment.

Correct and minimal: `custom:<name>` identities are real runtime shapes that must survive `resolve_provider` verbatim rather than collapse to bare `custom`, mirroring `is_runtime_provider_routable` keeps the two paths consistent, and the test that pins that agreement plus empty-suffix fail-closed cases shows good care. Two nits on identity hygiene:

1. hermes_cli/auth.py:2099 — because `normalized` only does `.strip().lower()` on the whole string, `"custom: grok"` passes the suffix check (`"grok".strip()` is non-empty) but is returned **with the interior space** as `"custom: grok"` — an identity no `custom_providers` key will ever contain, failing later at runtime-provider lookup with a confusing miss. Strip the suffix before reassembling: `name = normalized.split(":", 1)[1].strip(); return f"custom:{name}"`.
2. auth.py:2100 — resolution succeeds without checking that `<name>` actually exists in the configured `custom_providers`; a typo'd name now travels further before failing (at base_url lookup instead of at config validation). If the config is already loaded in scope here, an existence check with a "did you mean one of ..." error would keep failures early; otherwise document that this branch intentionally defers existence to runtime.
3. Case handling: the returned identity is lowercased; confirm `custom_providers` keys are normalized to lowercase at config load too, else mixed-case config keys won't match the resolved id. One line in the test file asserting the expected casing contract would pin it. (nit)

No blocking issues found.
