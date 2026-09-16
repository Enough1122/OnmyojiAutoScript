> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

This mirrors the CJK-bigram containment pattern faithfully: profile-owned `sessions.trigram_fts` resolved from the config adjacent to each `state.db` (no leaky global env bridge), trigger-drop quarantine with a durable `fts_trigram_stale` breadcrumb instead of destructive removal, marker kept until the controlled rebuild finishes so concurrent read-only opens stay on fallback, and parameterized `_fts_trigger_count` killing the would-be rebuild-on-every-open loop. The test matrix (fresh/quarantine/reenable/read-only-barrier/stale-recovery/optimize-retire) is genuinely thorough. Findings:

1. hermes_state.py:709 — config resolution fails *open* (`except Exception → return True`), and the init flow then treats the DB as trigram-enabled-with-stale-marker → `_reset_stale_trigram_schema` drops the quarantined table and rebuilds. So any transient failure (import cycle, unreadable YAML, managed-overlay hiccup) silently converts a *deliberately quarantined, corruption-prone* index back into an active one — exactly the opposite of what an operator who set `false` wants. Suggestion: have the resolver distinguish "resolved off" from "resolution failed" (return e.g. `None`) and, on failure, honor an existing `fts_trigram_stale` marker as still-quarantined instead of rebuilding.

2. hermes_state.py:3359 — the full config pipeline (raw read → deepcopy+merge → normalizers → env expansion → managed overlay) now runs synchronously in every `SessionDB.__init__`. Gateway/profile-aggregation code constructs many short-lived connections; this adds repeated disk I/O and merge work per open. Consider memoizing per (config_path, mtime) like other cached reads, or reusing whatever cache `read_user_config_raw` already maintains.

3. hermes_state.py:700 — the state layer now depends on five private helpers of `hermes_cli.config` (`_deep_merge`, `_normalize_*`, `read_user_config_raw`). The broad `except` masks drift until something renames one and everyone silently fails open (see #1). A tiny public accessor on the config module (e.g. `resolve_effective_config(path)`) would keep the layering honest and make breakage loud.

No blocking issues found beyond #1 — I'd want that one addressed or consciously accepted before merge given the PR's own motivation is recurrent trigram corruption.
