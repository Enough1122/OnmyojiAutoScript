> AI code review — automated review for reference; please use your judgment.

Review of "fix(kanban): expose and render profile display_name in dashboard picker (#89957)". Clean feature slice: `display_name` rides along in /profiles while `name` stays the routing key, `profileLabel` mirrors the CLI's format_profile_label convention exactly, and unset names fall back to the bare id. Suggestions:

1. plugins/kanban/dashboard/dist/index.js:1944 (default indicator lost) — the old rendering appended "(default)" to the orchestrator option and showed a default badge on description rows; `profileLabel` drops both, so after this PR users cannot see WHICH profile is the default anywhere in the panel — append the tag when `p.is_default` (e.g. `profileLabel(p) + (p.is_default ? " (default)" : "")`) or add a separate badge back.

2. tests/plugins/test_kanban_dashboard_plugin.py:1268 (bundle-substring assertions) — the second test asserts exact source substrings of the shipped bundle ("dn + " (" + p.name + ")"" etc.); any formatting or refactor of profileLabel breaks it even when behavior is fine — since the bundle is readable JS, prefer extracting `profileLabel` via node/vm (the pattern other hermes-bots tests already use) or rendering through a DOM harness so the test checks BEHAVIOR.

3. repo hygiene (verify) — this edits `dist/index.js` directly; confirm the kanban dashboard really is hand-maintained at HEAD (no bundler step) — otherwise a future rebuild silently reverts the label fix while these substring tests are the only thing keeping it visible.
