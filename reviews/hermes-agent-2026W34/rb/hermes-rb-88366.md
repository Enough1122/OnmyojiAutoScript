> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right isolation fix: an autouse fixture patching `find_gateway_pids`, `supports_systemd_services`, and `find_profile_gateway_processes` keeps the updater's yes-path gateway restart logic from discovering — and potentially signalling — real system services on a developer machine. Patching at the `hermes_cli.gateway` boundary (where the update flow looks them up) rather than deeper is the correct level, and making it autouse means future tests added to this file inherit the safety by default.
