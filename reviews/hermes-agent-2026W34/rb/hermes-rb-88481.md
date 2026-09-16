> AI code review — automated review for reference; please use your judgment.

This is the **third identical copy** of the `IterationBudget.used` lock fix now open (#88480, #88479, and this one — same diff, same test file). The change itself is correct: the `used` property was the only unguarded accessor on the lock-protected counter. Items:

- PR hygiene — issue — three open duplicates of one patch guarantee merge conflicts between them and triple changelog entries — suggestion — keep exactly one (ideally retitled without the doubled `fix: fix(...)` prefix), close the other two referencing it.

No blocking issues found on the code.

— reviewer-b (automated review)
