> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): preserve authorization denial outcomes". Correct fix for a real observability gap: unauthorized-user denials return an empty response, which the processing-complete hook counted as a SUCCESSFUL no-op, so metrics/plugins never saw policy blocks as failures. The explicit `_hermes_processing_outcome` marker stamped at the denial site and honored (with an isinstance guard) ahead of the empty-response heuristic is the minimal change, and tests cover both the adapter honoring an explicitly failed handler and the unauthorized Slack path end-to-end. Two nits:

1. gateway/run.py + platforms/base.py share the magic string `"_hermes_processing_outcome"` across modules with no single definition — hoist it to a named constant on ProcessingOutcome (or the platforms base module) so a rename can't silently break the channel.

2. nit — only the authorization denial stamps the marker today; other explicit-empty-as-failure paths (e.g. blocked-by-policy responses elsewhere) may deserve the same treatment later; the mechanism makes that a one-liner now.
