> AI code review — automated review for reference; please use your judgment.

This is how cause-mapping should be done: the message table is keyed to `PERSISTENCE_ERROR_CAUSES` with a completeness test that fails when a new bucket ships unmapped, the unstructured-error fallback now routes through `classify_persistence_error` (killing the documented ````"disk" in error_str```` misdiagnosis where corruption text stole the disk wording on #77386), and the per-cause wording fixes real harms — `turn_lease` no longer contradicts run_agent's "not saved" explainer, `compression_closed` asks for a client refresh against the *new* session id instead of a doomed retry, and `corrupt` finally tells operators the truth (permanent, disk space won't help) plus three concrete recovery steps. The negative assertions ("should already be saved" must not appear for permanent causes) are the right shape of test.

1. Nit (`gateway/run.py:~3952–3956`, corrupt message): the guidance hardcodes ````~/.hermes/state.db```` and ````~/.hermes/backups/````, but `HERMES_HOME` is configurable and native-Windows installs live under `%LOCALAPPDATA%\hermes` — an operator following the literal commands on such a setup salvages the wrong file — suggestion: interpolate the actual state-db path (it's known at this layer's caller) or phrase as "your state database (default ~/.hermes/state.db)".

2. Nit (`:~3948`, unknown bucket): "Your message should already be saved" is carried over for genuinely unclassified failures; given this PR's own standard of matching claims to evidence, a hedge ("the message may not have been saved") would be more honest for the one case where we know least.

— reviewer-a · automated agent review (Hermes week-review)
