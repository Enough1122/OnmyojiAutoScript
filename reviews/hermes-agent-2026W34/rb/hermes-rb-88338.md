> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct diagnosis of a silent wake-word death (#88245): the blanket `.upper()` worked only because the *bundled* English model's BPE vocabulary happens to carry uppercase pieces; community lowercase models emit an unknown piece, sherpa skips it, `text2token` returns empty, and the keywords file gets a blank line. Case-adaptive fallback (upper → as-configured → lower) keeps bundled-model users byte-identical while rescuing everyone else, an untokenizable phrase is dropped with an error log rather than poisoning the file, and total failure raises loudly. Tests pin the attempted-variant order, the fallback content, the skip-not-blank behavior, and the all-fail raise.

Nit (non-blocking): tools/wake_word.py:727 — inside `for p in phrases:`, the body reassigns `phrases = [q for q in phrases if q != p]` while the loop keeps iterating the *original* list object. It happens to be correct (each rebuild is cumulative, and `tokens` only appends for survivors so index alignment holds), but mutation-during-iteration via name rebinding is genuinely hard to verify by eye — as evidenced by needing this paragraph. Collect survivors into a `kept`/`kept_tokens` pair and assign once after the loop.
