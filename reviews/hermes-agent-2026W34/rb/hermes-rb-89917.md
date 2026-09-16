> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Clean micro-fix: hoisting `_load_xai_config()` into a single call removes both the redundant deepcopy and the TOCTOU window where the two reads could observe different configs, and the counting test pins exactly-once semantics while neutralizing the env-var short-circuit. Nothing else to flag.

No blocking issues found.