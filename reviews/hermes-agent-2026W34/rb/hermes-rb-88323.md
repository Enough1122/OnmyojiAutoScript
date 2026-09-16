> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Good consolidation plus a real false-alarm fix: extracting `scheduler_readiness_warning` into one shared module removes the CLI-local duplicate of the provider-resolution logic, and recognizing `HERMES_DESKTOP=1` as a legitimate readiness path (the desktop runs its own cron ticker without a gateway process) stops the built-in-scheduler warning from firing for every desktop user with no gateway installed. Surfacing the same warning through the `cronjob` tool's create response means the *agent* creating jobs also learns when they won't fire — arguably the most valuable consumer. All five readiness branches including the external-provider and desktop suppressions are pinned by tests.
