> AI code review — automated review for reference; please use your judgment.

Review of "feat(discord): configurable presence/activity". Well-built presence support: placed in `on_ready` so it re-applies after every reconnect/RESUME (fixing the visually-offline #64932), attached to the bot's application_id so Discord renders real Rich Presence (icon + elapsed time) with graceful debug-level degradation when `application_info()` fails, the config→env bridge follows the established first-writer-wins DISCORD_* convention, and optional Rich-Presence asset keys are plumbed through with dev-portal guidance. Tests pin the YAML→env bridge. Suggestions:

1. plugins/platforms/discord/adapter.py:1410 (silent failure) — a presence failure (invalid asset key, missing permission) is swallowed at DEBUG while the user explicitly configured an activity; warning-level (or surfacing via `hermes mcp/discord test`-style verification) would close the "configured but not showing" support loop.

2. nit — unknown `activity_type` values silently map to playing; logging the unrecognized value would catch typos like "waching".
