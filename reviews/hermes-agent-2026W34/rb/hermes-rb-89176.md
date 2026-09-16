> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Two real defects fixed at once: the NUL-wrapped tokens were invisible locally but stripped by the Chat API (leaking bare "GC1" into messages), and restore order didn't expand nested placeholder keys inside already-restored values. The printable `@@HERMES_GC_PH_{n}@@` token plus outer-first (reversed) restoration fixes both, and the nested-backticks-inside-bold test plus the gh-CLI sentence test pin the reported shapes including a negative on the new token leaking.

Nit (non-blocking): plugins/platforms/google_chat/adapter.py:2476 — the reversed single-pass restore assumes placeholder insertion order mirrors nesting depth (outer captured before inner). If a future regex captures an inner region before its outer, one pass leaves a stale token behind. Either add a comment stating that invariant, or loop the restore until stable with a small iteration cap so ordering assumptions can't silently regress.
