> AI code review — automated review; please use your judgment.

1. `plugins/platforms/discord/adapter.py` (`on_interaction` / `CronDeliveryView._fired`) — the once-per-user dedup lives on the **View instance**, but REST-delivered cron messages have no persistent view: every click constructs a fresh `CronDeliveryView` in `on_interaction`, so `_fired` starts empty and the same user can fire `snooze`/`dismiss`/custom actions **unlimited times**, forever (no live view means `on_timeout` never disables the buttons either) — why it matters: a cron delivery with a destructive custom action becomes an endlessly repeatable remote trigger — suggestion: derive idempotency from state outside the view (e.g. record ````(message_id, user, action)```` in the adapter and check it in `_on_button`), and/or have `on_interaction` edit the message to disable the row after first use.

2. Test gap — the module adds several easily-unit-tested pure helpers (`_parse_delivery_block`, `_build_embed_from_spec`, `_delivery_embed_to_rest_json`, `_delivery_buttons_to_rest_json`, `_delivery_buttons_from_message`) plus the `cron:` custom_id grammar, and ships **zero tests** — why it matters: the custom_id format ````cron:{delivery_id}:{action}:{index}```` is load-bearing across two code paths (live view + interaction reconstruction) and silently breaks if `action` ever contains `:" — suggestion: add parser/serializer round-trip tests and validate/escape the action name charset at spec-parse time.

3. Nit (`send()` rich-delivery block): the image probe message is deleted after harvesting its attachment URL; if the delete fails, an orphan image message stays behind — harmless but worth a debug log like other best-effort paths here.

The layered design itself is good: fenced ````discord-delivery```` JSON as the transport, plain-text fallback on any rich-path failure, per-field length caps matching Discord limits, URL buttons exempted from the action dispatch, and graceful `Already handled` / error ephemerals on the interactive path.

— reviewer-a · automated agent review (Hermes week-review)
