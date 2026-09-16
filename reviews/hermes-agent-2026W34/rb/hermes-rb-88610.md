> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix for a real disambiguation bug: collapsing `…-4.8` and `…-4.8-thinking` (or `-fast`) into one label made base and variant models indistinguishable in menus and the status pill. Carrying the variant tag into the name fixes it at the source, and the `tag !== 'Fast'` guard neatly prevents the double-Fast ("Fast · Fast Med") when the variant already encodes speed — while keeping the param-driven Fast for plain ids. Tests pin the reporter's exact case plus the never-collapse invariant as an explicit assertion rather than a string equality.
