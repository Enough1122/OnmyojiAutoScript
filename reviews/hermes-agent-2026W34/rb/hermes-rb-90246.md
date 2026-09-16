> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: _parse_task_xml_launcher reads only the FIRST Exec action. Fine for Hermes-generated tasks, but a user-edited task that chains actions would be judged by its first entry alone — worth half a sentence in the docstring stating that assumption. The rest is exemplary migration work: encoding-agnostic regex parsing with unescape, case/quote-insensitive launcher matching, None-means-unknown discipline so callers never alarm on query failure, status/start/install all surfacing the state, and the post-update refresh actually healing legacy installs with an actionable admin-required fallback — each branch pinned by tests including the pure cross-platform parser ones.

— Reviewed by Hermes AI reviewer (reviewer-f)
