> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct root cause on a nasty edit-corruption class: `line_indent.startswith(old_indent)` is vacuously true when `old_indent` is empty, so every replacement line took the prefix-swap path and came out double-indented whenever the LLM's old_string started at column 0. The dedicated empty-base branch (preserve each line's own indentation; anchor only true column-0 lines to the file's base) fixes both the CRLF and LF variants, and the tests assert exact per-line indentation arrays rather than eyeballable output — plus a regression case proving non-empty-base swaps still work. Findings below are minor:

1. tools/fuzzy_match.py:_reindent_replacement — the new branch's `line.lstrip(" \t")` strips **tabs** from continuation lines too, then re-prefixes the file's space-based indent: a file mixing tab-indented bodies gets its tabs silently converted to spaces inside the replaced region. If that's intended normalization, fine; otherwise restrict the strip to spaces (or preserve leading whitespace verbatim and only anchor pure-column-0 lines).
