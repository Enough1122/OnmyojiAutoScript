> AI code review — automated review; please use your judgment.

Review of "fix(agent): log unavailable fallback skips at warning level". Right promotion: a skipped fallback means the chain is being walked with every candidate already marked unavailable — operationally significant when the user is about to see a rate-limit failure, and invisible at debug. The recursion into `_try_activate_fallback` preserves walk order across the remaining candidates. No blocking issues found.
