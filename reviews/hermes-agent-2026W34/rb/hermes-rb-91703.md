> AI code review — automated review for reference; please use your judgment.

The unit normalization is correct (`24h` folds to `Daily`, `1d`/`3d` map through the same minute math as their `m` equivalents, and cron/once branches are untouched upstream of the regex), and the test file's approach — loading the real bundled `plugin.js` in a `vm` and asserting every picker-emittable schedule round-trips to a non-raw label — is exactly the kind of contract test that prevents the next unit from falling through the cracks.

No blocking issues found.

Nit (`plugin.js:~8618`): `every 0h`/`every 0d` normalize to `minutes = 0`, which satisfies `minutes % 1440 === 0` and would render "Every 0 days"; if `composeSchedule` can't already guarantee a positive interval, rejecting `n === 0` in the regex path (or treating it as invalid input at the picker) closes that pre-existing edge too.

— reviewer-a · automated agent review (Hermes week-review)
