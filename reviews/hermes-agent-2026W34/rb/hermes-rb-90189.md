> AI code review — automated review for reference; please use your judgment.

Review of "feat(config): user-declared include files". Solid composition feature: declaration-order merging with declaring-file-wins precedence, relative-to-declarer resolution with expanduser/expandvars, recursive includes with seen-set cycle detection, cache signatures folding every included file's stat so edits invalidate correctly, and — the part most implementations forget — save-time stripping of include-sourced values so `save_config` doesn't duplicate include content into the main file unless the caller actually changed it (with a `preserve_keys` escape hatch). Suggestions:

1. hermes_cli/config.py:2020 (upstream readiness) — several comments are in French and one references fork lineage ("Fork bbad163343, restauré 17/08 après perte au merge upstream v0.20.1"), which is unreadable context for upstream reviewers and will rot — translate the comments to English and move the fork-provenance note into the PR description.

2. hermes_cli/config.py:_strip_included_config_values (explicit-equal edge) — a value the user EXPLICITLY sets in config.yaml to exactly the include's value gets stripped on next save (equality-based removal), silently re-exposing them to future include edits; if preserving explicit-main settings matters, thread the pre-merge main keys through `preserve_keys`, or at least document the "matches include ⇒ treated as inherited" rule.

3. nit (chain depth) — cycle detection prevents loops but not arbitrarily long acyclic include chains; harmless today, though a soft cap with a warning would keep pathological configs from slowing every load.
