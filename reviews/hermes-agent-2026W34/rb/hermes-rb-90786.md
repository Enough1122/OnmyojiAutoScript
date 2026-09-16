> AI code review — automated review for reference; please use your judgment.

1. tools/environments/base.py:583 — scoped-session markers are now excluded from the snapshot by appending names to an inline string, while their INJECTION lives elsewhere (scrub_kanban_env puts HERMES_DELEGATED_CHILD_CONTEXT into subprocess env). Why it matters: every future scope marker must be remembered in two places, and forgetting this dump reproduces #90782 verbatim for the new marker. Suggestion: define one SCOPED_SESSION_ENV_MARKERS tuple next to the injectors and build both the injection filtering and this exclusion string from it — then the leak class closes structurally instead of per-incident.

2. Good test hygiene: the unit case pins both marker families in the dump text, and the end-to-end test exercises the real LocalEnvironment snapshot path (with the Windows skipif matching its POSIX bash assumption) and asserts on the failure consequence, not just absence of the string.
