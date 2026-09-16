> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix applied at *all three* surfaces where the ghost cap could re-enter: preset defaults, normalization (`_coerce_int_or_none` replacing the 4096 coercion so missing/null = uncapped while explicit values pass through), and the dashboard payload models whose 4096 field-defaults would have silently re-capped every save even after the config side was fixed — that last one is the subtle part most fixes miss. Tests pin missing/null/capped/default-preset cases including the flattened view dashboards consume.
