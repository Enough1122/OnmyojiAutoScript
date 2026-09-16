> AI code review — automated review for reference; please use your judgment.

The feature is worth having (replayed/delayed Feishu events after a restart are a real problem, the env knob with `0` disables cleanly, and dropping before dedup keeps ordering sane), but **this patch cannot run as written** — two blocking omissions:

1. **BLOCKING — missing settings field**: `_load_settings` now passes `max_message_age_seconds=...`, but `FeishuAdapterSettings` has no such field (nothing between `webhook_path` and `ws_reconnect_nonce` on the base). Every adapter startup will die with `TypeError: unexpected keyword argument`. Add `max_message_age_seconds: int = _DEFAULT_MAX_MESSAGE_AGE_SECONDS` to the dataclass.
2. **BLOCKING — missing import**: the new handler path calls `time.time()` but adapter.py never imports `time`. First inbound message raises NameError (after the settings fix). Add `import time`.
3. plugins/platforms/feishu/adapter.py:2621 — `int(create_time_ms)` is unguarded; a non-numeric `create_time` raises ValueError inside the event handler *before* dedup registration, so the event loop logs an exception and the message may be reprocessed forever. Use the module's existing `_coerce_*` helpers or try/except and treat unparsable timestamps as not-stale (let dedup own it).
4. Ops note worth a comment: staleness compares Feishu server timestamps to the local clock, so a host with >5min skew silently drops fresh messages. The env override covers it — document `FEISHU_MAX_MESSAGE_AGE_SECONDS=0` as the escape hatch next to the default constant. (nit)

Please add the field + import (and ideally a startup smoke test constructing `FeishuAdapterSettings` via `_load_settings`) before merging.
