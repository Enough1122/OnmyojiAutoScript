> AI code review — automated review for reference; please use your judgment.

1. tools/skills_sync.py:1140 — the plain-reset outcome is now detected by reading the manifest AFTER the resync (re-baselined vs skipped vs no-bundled). Why it matters: this is inference from a side effect rather than from sync_skills' own decision, so a future change to how sync records entries (e.g. writing tombstones, or deferring manifest writes) silently flips users back to the dishonest message. Suggestion: have sync_skills return/report per-skill disposition (it already computes the skip-vs-rebaseline decision internally) and let reset consume that instead of re-reading the file.

2. Nice consistency catch in the collision hint: `hermes skills reset <name>` correctly became `reset <name> --restore` there, since under the new semantics a plain reset can never make an overwritten-name collision accept upstream.

The docs discipline is exemplary — CLI help, slash help, argparse descriptions, website reference, user guide AND the zh-Hans translation all tell the same three-branch story, the old source-scanning invariant test was retired in favor of direct unit tests of the extracted notice helper (with the empty-list silence pinned), and the three new reset outcomes each carry a behavioral test including the orphan/no-bundled case where pointing at --restore would be wrong.
