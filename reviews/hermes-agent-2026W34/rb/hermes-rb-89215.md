> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct incentive-aligned fix for #89213: the deterministic-empty skip exists purely to avoid repeat *charges*, so a streak with `None` cost (local/self-hosted, unpriced model) or even an explicitly $0 one has nothing to save and failing open keeps recoverable turns recoverable — while the motivating paid-route behavior is unchanged and now explicitly pinned to a priced streak in the old test. The four new unit tests cover unknown/zero/known cost plus the important negative control that failing open doesn't inflate the retry budget, and the end-to-end test proves the exact reported shape (two local empties then a success on attempt 3).
