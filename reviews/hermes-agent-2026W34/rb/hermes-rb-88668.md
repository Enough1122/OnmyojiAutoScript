> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Precise type-aware fix: a callable `api_key` (`key_cmd`-minted per-request bearer) previously hit `.strip()` and died; now callables pass through untouched, strings keep their normalization, and blank strings still fall through to the env fallback. The tests assert the full contract rather than just the crash — most importantly that resolution hands the *same function object* to the client **without invoking it**, since minting must stay deferred to request time.
