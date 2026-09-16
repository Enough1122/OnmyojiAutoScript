> AI code review — automated review for reference; please use your judgment.

Review of "feat(gateway): add required inbound plugin gates". Strong ops posture for the core feature: startup preflight verifies each required plugin is loaded/enabled/error-free AND that every declared hook is actually registered (`hook_names` now exported by list_plugins), failures write `startup_failed` runtime status and exit with the fatal code instead of limping along, and once gates are configured a pre_gateway_dispatch invocation failure blocks the message (fail-closed). Config validation is strict and well-tested. Concerns:

1. hermes_cli/plugins.py:1932 (crash → silent message loss) — `invoke_hook` now converts ANY registered plugin's exception into `{"action": "skip", "reason": "hook_error"}` for pre_gateway_dispatch/pre_gateway_media_download — so one buggy plugin callback makes the gateway DROP inbound media (or block dispatch) on EVERY message, even for deployments that never opted into `required_plugins` — that's a big default-behavior change hidden inside a gating PR; make hook_error fail-OPEN (log + continue) by default and flip to fail-closed only when the runner has required gates configured (the runner already knows).

2. Scope — the title promises required-plugin gates, but the PR also ships a complete, unrelated STT dedupe subsystem (`_transcribe_audio_deduped` LRU + inode/mtime keys + 335-line test file) plus telegram document handling — both are genuinely well built (shield() for shared futures, failure eviction, first-delivery echo semantics), but bundling them makes revert/bisect harder; consider splitting.

3. gateway/config.py:941 (design confirmations) — two strictness choices deserve explicit docs: (a) `required_plugin_hooks_missing` forbids presence-only gating (every required plugin MUST declare ≥1 hook — an empty-list "just ensure it loads" use case is impossible), and (b) HERMES_SAFE_MODE + required plugins refuses startup outright, which could block recovery if the operator needs the gateway up to disable the plugin — if both are deliberate, say why in the config reference.

4. gateway/run.py:7040 (nit, identity matching) — `_loaded_by_id` compares plugin ids/names case-sensitively against stripped-but-unnormalized config strings; a "MyPlugin" vs "myplugin" mismatch reads as "unavailable" — normalizing case here would match how the rest of the config layer behaves.

No blocking issues found beyond item 1, which changes default message-handling behavior for existing plugin users.
