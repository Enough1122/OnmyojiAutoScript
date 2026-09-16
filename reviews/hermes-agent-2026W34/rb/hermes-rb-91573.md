> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Clear improvement: "[image not retained]" names itself as a storage artifact, so history renderers, exports, and later turns stop hunting for an image the store never kept. Both production sites (agent/tool_dispatch_helpers.py trajectory normalization and run_agent.py flush path) plus their tests are updated consistently.

Nit: the literal now lives in two modules (tool_dispatch_helpers.py:529, run_agent.py:2323); hoisting it into one shared constant (e.g. IMAGE_PLACEHOLDER_TEXT) would keep the wording from drifting apart on the next touch. Worth a quick repo-wide grep confirming nothing else still emits or pattern-matches the old "[screenshot]" literal — readers will encounter both spellings in historical transcripts regardless, so detection code should stay tolerant of either.

No blocking issues found.