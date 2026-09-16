> AI code review — automated review; please use your judgment.

Clean fix for a real UX wart: excluding the live turn's group from the render budget (`unbudgetedTail`) means token flushes can no longer grow the tail weight, shift the visibility cut, shrink `scrollHeight`, and trick stick-to-bottom into thinking the user scrolled up. The change is minimal (one excluded index range in the walk), the old behavior for *completed* tails is explicitly pinned by a test, and the growing-tail stability case is covered at both 1 and 5000 weights.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
