> AI code review — automated review for reference; please use your judgment.

- package.json / package-lock.json — Clean, coherent bump: `@playwright/test`, `playwright`, and `playwright-core` all move 1.58.2 → 1.62.1 together with matching integrity hashes, and the new `engines: node >=20` floor is a non-event for this repo (root and apps/desktop already require `node >=22.22.0`, and .nvmrc pins 26). Nothing further needed.

_— hermes-week-review automated review (reviewer-d)_

No blocking issues found.