> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right guard for an easy-to-hit footgun: `hermes setup` serializes empty defaults into config.yaml, and an explicit-key empty `[]` was clobbering a carefully set `TERMINAL_DOCKER_VOLUMES` from the environment. Keeping the env value with a warning preserves operator intent, and the four tests cover every combination (empty-config/non-empty-env, non-empty override, both-empty, env-absent) so the guard's exact boundaries are pinned.

Nit (non-blocking): hermes_cli/config.py:3497 — the guard removes the ability to *deliberately clear* mounts from config (empty list + no env var works, but empty list + set env now keeps the env). If someone needs to clear env-provided volumes they must edit the environment instead of config, which the warning text doesn't say. Consider appending "…or remove the env var to clear" so the escape hatch is discoverable.
