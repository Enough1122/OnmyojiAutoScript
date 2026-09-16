> AI code review — automated review for reference; please use your judgment.

Genuinely useful drift-guard visibility (#89513): unpinned jobs silently resolving to `cron.model` instead of the global model is exactly the kind of implicit routing users discover only when a bill or a model mismatch shows up, and the pinned/fleet/global badge plus always-populated model row makes fire-time resolution legible. The routing logic lives in pure exported functions (`jobModelRouting`, `cronModelChoiceLabel`) with a test matrix covering pin-with-provider, pin-without-provider, fleet-configured, fleet-empty, and global cases. Points:

1. apps/desktop/src/app/cron/index.tsx — the `fleetConfig` derivation (read config → shape `{model, provider}`) is duplicated verbatim in `CronJobDetail` and `CronEditorDialog`. Extract a `useCronFleetConfig()` hook so a future field rename (`cron.model_provider`) updates one place.
2. index.tsx:~830 — the badge labels ("Pinned" / "Fleet default" / "Global default") are hardcoded English while every surrounding string goes through `t.`; same for `'Global default'` inside `jobModelRouting`. Route them through i18n like the rest of the panel, or note that this surface is intentionally English-only. (nit)
3. The editor's initial-choice mapping (pinned → its combo; unpinned+fleet → `MODEL_FLEET_VALUE`; else default) is tested only via the label helpers — add one assertion that saving with `MODEL_FLEET_VALUE` selected persists `model: ""` (i.e., the sentinel never leaks into the stored job), since that mapping happens outside the pure functions. (nit)
4. Tone choice (good/warn/muted per kind) is a nice at-a-glance signal; consider also showing the resolved label as the pill tooltip for narrow sidebars where the row truncates. (nit)

No blocking issues found.
