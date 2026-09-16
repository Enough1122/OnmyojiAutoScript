> AI code review — automated review for reference; please use your judgment.

The fix is right and minimal: an unexpected `confirm()` rejection must behave like cancellation for a destructive wipe guard, and the new `.catch` does exactly that. Same structural note as its sibling PR:

1. apps/desktop/src/app/settings/config-settings.test.ts:12 — the suite again **inlines a copy** of the production logic instead of exercising `config-settings.tsx`. If the component's guard ever grows extra behavior (logging, notification on rejection), these tests keep passing against the frozen copy. Extracting a tiny `applyWhenConfirmed(confirmFn, apply)` helper used by the component would make the copied tests real ones — and given this is now the *second* confirm-rejection guard fixed the same way (see #90670's preview routing), one shared utility would prevent the third.
2. config-settings.tsx:234 — silent catch is acceptable here (rejection ≈ dialog dismissed), but a `console.debug` would distinguish "user backed out" from "confirm infrastructure broke" when someone reports that the wipe silently doesn't happen. (nit)
3. The three-state test set (true/false/reject) is the right matrix — carried over to the shared helper from item 1, it'd be testing the real thing. (nit)

No blocking issues found.
