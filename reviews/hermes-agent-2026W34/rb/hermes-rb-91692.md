> AI code review — automated review for reference; please use your judgment.

The change is correctly scoped: only the `model.save_key` lane drops the `max_models=50` cap (picker paths that legitimately truncate are untouched), and the new test asserts the full 120-model catalog survives end-to-end through the method dispatch, including the tail element and dedupe sanity. The root cause reads plausibly — the cap was copy-pasted picker context applied to a post-auth refresh where truncation hides the provider you just authenticated.

No blocking issues found.

Nit (`tui_gateway/methods_complete.py:~549`): two cheap hardeners — (a) a one-line comment stating *why* this lane must not cap ("newly-authenticated providers must return their complete catalog"), since the bare omission of a keyword is easy to reintroduce in a cleanup; (b) a quick check that no consumer of the `model.save_key` response assumes the old ≤50-model shape (TUI renderers or older clients), and that `build_models_payload`'s default really is unbounded rather than carrying its own implicit limit the test's stub happens to mask.

— reviewer-a · automated agent review (Hermes week-review)
