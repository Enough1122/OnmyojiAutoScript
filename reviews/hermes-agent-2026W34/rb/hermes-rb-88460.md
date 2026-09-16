> AI code review — automated review for reference; please use your judgment.

This closes the long-standing `TODO(profile-secrets)` correctly: pairing mirrors under multiplexing now write to the *active profile's* `.env` via the HERMES_HOME override while suppressing the process-global `os.environ` publication (`update_environ=False`) that would contaminate sibling profiles, the live in-scope mapping is updated too so the current turn sees its own grant, read-only scope mappings report False instead of being weakened, and the end-to-end tests prove sibling isolation down to file contents and the untouched process env. The `update_environ` kwarg defaulting to True keeps every existing caller on legacy behavior. One nit:

- hermes_cli/config.py:4090 — nit — `save_env_value`'s return changed from implicit `None` to a meaningful `bool`; any caller that treated "no exception" as success is unaffected, but one that checked truthiness of the old None would now see managed-scope refusals differently — worth a quick grep of `save_env_value(` call sites for truthiness checks.

No blocking issues found.

— reviewer-b (automated review)
