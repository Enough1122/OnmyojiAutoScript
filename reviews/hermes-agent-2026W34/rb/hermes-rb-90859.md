> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Fixes a real footgun with good blast-radius analysis in the docstring: `hermes plugins doctor` defaults to `.", so pre-guard it would copytree an arbitrary directory (worst case, $HOME with cloud-storage placeholders) before the runtime ever rejected it. The two-stage resolution is now principled — directories must actually hold a discoverable manifest (flat or one-level category layout, mirroring `_scan_directory`), ids must be relative without dot components (so `." can't resolve to the whole plugins root), and the two failure modes get distinct actionable errors. The four new tests cover the bug scenario itself, the default-target no-copy guarantee, category layouts, and installed-id shadowing.

Nit (non-blocking): hermes_cli/plugin_dev.py:_holds_plugin — the discovery rule is duplicated by hand ("mirrors `_scan_directory`"), which means the next change to real plugin discovery (deeper nesting, extra manifest names, pyproject-based plugins…) silently desyncs Doctor's guard from what actually loads. Import/reuse the manager's directory-test directly (or extract a tiny shared `plugin_manifest_under(path)` helper into hermes_cli.plugins) so there's exactly one definition of "looks like a plugin".
