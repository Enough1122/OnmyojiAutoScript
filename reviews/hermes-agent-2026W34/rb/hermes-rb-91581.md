> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Well-targeted fallback: retry *only* on rg's own parser diagnostic naming a PCRE2-only construct, with nice negative tests proving path-embedded trigger phrases don't trip it. Points:

- **tools/file_operations.py:416-435 (_rg_diagnostic_requires_pcre2) — the exact two-line suffix match will silently break across rg versions.** Requiring nonempty[-2:] to equal the fixed recommendation text bakes in ripgrep's *current* wording *and* line-wrap width; any release that rewraps ("...which can handle backreferences and look-around." on one line, or different phrasing) disables the feature with zero signal — every look-around/backref search regresses to a plain error. Suggestion: keep the strong first-line anchor ("rg: regex parse error:") but match the recommendation by normalized-whitespace substring ("consider enabling pcre2") instead of exact trailing lines. Your multiline_missing_path test still passes under that rule because the anchor line won't match there.

- **tools/file_operations.py:~3219 (retry command) — the "set -o pipefail;" prefix assumes bash.** Under Debian/Ubuntu where /bin/sh is dash, "set -o pipefail" errors out, so the retry itself would fail with a shell-syntax diagnostic unrelated to the search — and inconsistently with how cmd_parts was originally assembled (which apparently needs no prefix). Suggestion: build the retry exactly like the original command (insert --pcre2 into the same template) rather than prepending shell state changes; if pipefail matters, apply it to the first invocation too.

- **tools/file_operations.py:~3221 — hardcoded timeout=60 on the retry diverges from the caller's budget.** The first attempt runs with whatever timeout the operation configured; the second pins 60s regardless. Long searches with tighter budgets lose their bound. Pass through the original timeout value.

- **No memoization of PCRE2 availability.** On an rg built without PCRE2, every look-around pattern costs a doomed extra exec returning a confusing "pcresupport"-style error. A one-time probe (or caching the failure per process) would degrade cleanly back to the normal error path.

- **tests/tools/test_search_rg_pattern_handling.py — gaps tied to the above.** Nothing covers: alternate recommendation wording/wrapping (pins point 1), offset/limit preservation through the retry (glob+context are covered, offset is not), and behavior when the installed rg lacks PCRE2 support.

Nice discipline overall on the negative cases — indented_echoed_error_line and the missing-path tests are exactly the traps this kind of string matching usually falls into.