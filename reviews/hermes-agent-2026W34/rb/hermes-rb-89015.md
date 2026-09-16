> AI code review — automated review for reference; please use your judgment.

Good extraction: a pure, exported `turnDoneNotificationBody` with explicit precedence (trimmed reply → i18n fallback → constant), never the session title, plus a legacy-Studio comparison test proving the title-in-chain behavior is deliberately *not* replicated. Filling the previously-empty `turnDoneBody` in all five locales also fixes the invisible-notification-body case for every language at once. Points:

1. apps/desktop/src/lib/turn-done-notification-body.ts:~16 — `source.slice(0, TURN_DONE_BODY_MAX)` can split a surrogate pair / emoji cluster exactly at the boundary, producing a broken character in the toast. `Array.from(source).slice(0, N).join("")` (or Intl.Segmenter) avoids it for negligible cost. (nit)
2. Note the visible behavior change for reviewers: previously an empty reply produced an empty-bodied notification; now every locale shows "Message complete."-style text. Improvement, but it's user-visible copy arriving via this PR — worth a line in the description.
3. The doc comment's #88488 rationale is precisely what stops someone from re-adding `session.title` to the chain later — exactly the kind of comment this repo benefits from. (positive)

No blocking issues found.
