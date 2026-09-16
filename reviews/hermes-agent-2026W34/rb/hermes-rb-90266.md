> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: DIFF_ENVELOPE_RE only matches a SINGLE diff block spanning the entire message (anchored ^ and $). A message with prose before/after the fence, or two stacked diff blocks, silently falls back to the generic estimate — correct-but-coarse, and worth one comment on the regex saying so, since the next person fixing a height bug will naturally try to extend it to multi-block first. The width choice (bodyWidth - 2 for the code indent) and suppressing assistant paragraph-gap padding for valid diffs are both right; the malformed-content fallback test is a thoughtful guard.

— Reviewed by Hermes AI reviewer (reviewer-f)
