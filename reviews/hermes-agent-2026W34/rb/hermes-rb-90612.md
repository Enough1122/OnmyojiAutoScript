> AI code review — automated review; please use your judgment.

Exactly right, and unusually well-guarded: the split form is claimed as an output-cap error **only when the measured prompt still leaves room** (`window − prompt ≥ 1`), so genuine input overflows stay on the compression path where they belong; the extracted budget (`window − measured prompt`) ignores the requested completion size, which is correct since that's the real remaining headroom; and the test matrix covers both server wordings, the fits-the-window invariant, the oversized-prompt negative case, and the no-split untouched case.

No blocking issues found.

Nit: the `window − split[0] ≥ 1` computation now lives twice (`parse_available_output_tokens_from_error` and `is_output_cap_error`, each with its own copy of the `maximum context length is (\d+)` lookup) — extracting one `_split_leaves_context_room(error_lower)` helper would keep the two predicates provably in lockstep; same for optionally extending `_COMPLETION_SPLIT_RE` if other servers surface ````"(N prompt tokens; M for the completion)"```` wordings in the wild.

— reviewer-a · automated agent review (Hermes week-review)
