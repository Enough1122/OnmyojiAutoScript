> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix for a self-contradictory doctor report: plugin-declared providers register a `ProviderProfile` with the runtime registry and never reach the static model catalog, so catalog-only resolution flagged exactly the providers the doctor itself listed as known. Falling back to `resolve_registered_provider_id` (with alias→canonical resolution) closes that, the docstring explains *why* the two registries diverge, and the test suite's invariant — "anything the registry lists must satisfy the validation" — is the right way to pin the relationship rather than snapshotting today's bundled set.
