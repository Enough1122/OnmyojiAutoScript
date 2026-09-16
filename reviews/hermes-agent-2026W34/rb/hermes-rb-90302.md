> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: the import guard in _apptainer_exec_env returns the unmodified environment silently when tools.env_passthrough can't be imported. Since that fallback means "passthrough quietly does nothing on this install", a single logger.debug naming the exception would save someone an hour the first time the module layout shifts.

The implementation is exactly right for the constraint: allowlist-only forwarding keeps APPTAINER_CLEANENV's default-deny posture intact, the APPTAINERENV_ prefix plus the bare name covers both container semantics and non-cleanenv runs, scope-resolved values take precedence over host environ, and the tests pin all four behaviors including the negative case that non-allowlisted secrets never gain the prefix.

— Reviewed by Hermes AI reviewer (reviewer-f)
