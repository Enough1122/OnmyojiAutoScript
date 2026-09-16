> AI code review — automated review for reference; please use your judgment.

Correct fix for #88989 with the right security posture: `resolve_switch_key_env` returns only an env-var *name* (never the resolved secret — explicitly asserted), the `${VAR}`-wrapper detection fails safe on plain strings, and every global-switch site (both CLI paths + TUI persist) now writes `model.key_env` or clears a stale one, so a previous provider's env-var name can't 401 the next request. The test set covers registry lookup, named-provider precedence, env-ref expansion, custom-list matching, unknown-provider clearing, and asserts `model.api_key` is never written. Points:

1. hermes_cli/model_switch.py:`resolve_switch_key_env` (~500) — when a provider's registry entry lists multiple `api_key_env_vars`, the first is persisted unconditionally. A user whose environment actually exports the *second* documented variable ends up with a wrong-but-plausible `key_env`. Consider preferring whichever variable is currently present in `os.environ` before falling back to the first name. (nit)
2. Same function — the builtin-registry branch swallows all exceptions and returns ""; fine as last-resort, but a debug log would distinguish "no known env var" from "registry import broke". (nit)
3. Ordering is sensible (`key_env` explicit → `${ref}` expansion → registry default) and each tier is individually tested; one comment stating the precedence chain would help future maintainers adding tiers. (nit)
4. The TUI persist test writes real YAML and asserts both the new key_env and the absence of `api_key` — exactly the regression that matters for #88989. (positive)

No blocking issues found.
