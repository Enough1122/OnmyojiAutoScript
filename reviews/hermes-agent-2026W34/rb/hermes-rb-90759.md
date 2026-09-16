> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): show persisted no-agent cron runs". Clean fix: script-only jobs never write conversational sessions, so surfacing the persisted `last_run_at` as the execution record is the right UX, `noAgentRunTime` is a well-guarded pure helper (type + NaN checks) with its own unit tests, and the prop widening to `job` keeps the effect deps correctly pinned to `job.id`. Suggestions:

1. apps/desktop/src/app/chat/sidebar/cron-jobs-section.tsx:443 (unverified i18n key) — the new line renders `{c.last}` but this PR adds no i18n keys, so it depends on `cron.last` pre-existing in ALL five locales — please confirm each translation reads naturally as a standalone prefix before a timestamp (e.g. ja/zh word order), since "Last" glued to a formatted date can read awkwardly after translation.

2. apps/desktop/src/app/chat/sidebar/cron-jobs-section.tsx:440 (render-branch coverage) — the helper is tested but the sidebar's new ternary (empty runs + no-agent → time line instead of "No runs") has no component test; one render assertion would pin both branches of that condition, including that agent jobs still show `noRuns`.

3. apps/desktop/src/app/cron/job-state.ts:23 (nit, semantics) — the line is labeled simply "Last <time>"; if `last_run_at` also updates when the script exits non-zero, users may read a failing job as healthy — consider pairing the timestamp with the row's state dot or a failure suffix if that data is available at this layer.

No blocking issues found.
