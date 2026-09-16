> AI code review — automated review for reference; please use your judgment.

Accurate docs fix in both locales: the old blanket "env always wins" statement was wrong for `require_mention`/`free_response_channels` (config-first when the key is set, env only as fallback), and the new wording even explains *why* a fresh install's written defaults shadow a conflicting `.env` entry. Consistent EN/zh-Hans and correctly linked to the general precedence doc.

— reviewer-b (automated review)

No blocking issues found.
