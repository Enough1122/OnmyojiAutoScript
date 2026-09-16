> AI code review — automated review; please use your judgment.

Review of "chore(i18n): add locale source-equality audit". Well-judged tooling: exact-match reporting framed as REVIEW EVIDENCE rather than automatic defect, non-blocking by default with an explicit `--fail-on-equal` CI gate, namespace scoping with descendant inclusion, deterministic grouped output, and tests covering flattening rules, filtering, CLI exit codes, and the fail-mode interaction with namespace filters. Two suggestions:

1. scripts/locale_source_equality.py (not wired anywhere) — nothing in this PR invokes the audit (no workflow step, pre-commit hook, or docs mention); as shipped it's manual-only, so untranslated keys will keep accumulating invisibly — either add a scheduled/report-only CI job or document the canonical invocation next to the other i18n tooling.

2. nit — matching is byte-exact, so a target that differs only by trailing whitespace escapes the report; normalizing whitespace (and maybe casefolding optionally behind a flag) would catch near-copies that are equally untranslated.
