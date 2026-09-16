> AI code review — automated review for reference; please use your judgment.

Good tolerance-with-escalation shape: valid dicts pass through untouched, JSON-string form is parsed so existing broken configs start working immediately, unparseable shapes fall back to global effort with a once-per-distinct-value warning, and empty string/None stay silently unset. The test matrix covers every branch including the warn-once counter. Points:

1. Root cause left standing: `hermes config set` persisting map-shaped keys as quoted JSON strings will bite the *next* map-shaped agent key too (`reasoning_overrides` just happens to be the one someone noticed). Even with this coercion, please either fix `config set` to emit real YAML maps for object values or add a lint/validation warning at set-time — otherwise the codebase accumulates one per-key shim per map-shaped setting.
2. hermes_constants.py:_coerce_reasoning_overrides (~1316) — `import logging` appears inside both warn branches; the module almost certainly already has a module-level logger pattern available (or can create one) — hoisting removes two local imports and the inline `__name__` reference. (nit)
3. The success-path warning ("parsed it, but edit config.yaml…") fires once per distinct raw string — if a user's value embeds a timestamp or changes between edits, warnings re-arm per variant. Fine; just noting the key is content-addressed, not path-addressed. (nit)
4. Edge worth one assertion: ``reasoning_overrides`` = `"null"` / `"5"` (JSON-valid but non-dict) should hit the bad-shape branch, not crash — behavior follows from the code, but pinning it guards the json.loads fallback ordering. (nit)

No blocking issues found.
