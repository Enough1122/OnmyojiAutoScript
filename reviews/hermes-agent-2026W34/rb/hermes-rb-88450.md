> AI code review — automated review for reference; please use your judgment.

Clean completion of the nav i18n migration: every `BUILTIN_NAV_REST` entry now carries a `labelKey`, en/ru translations are added, and the new keys are typed optional so locales without them keep falling back to the English `label`. Points:

1. web/src/i18n/types.ts — typing these as optional is pragmatic, but it means TypeScript won't flag a locale missing them while en has them *required-shaped*; consider making them required and back-filling the other locales with English strings instead, so the interface documents the full surface. (nit)
2. Drive-by observation adjacent to your ru.ts edit: `profiles: "профили: мульти-агенты"` (pre-existing) reads oddly as a nav label — lowercase plus a colon suffix. Worth a follow-up normalization. (nit)
3. The six newly routed entries match their English labels exactly in en.ts, so no visible change for English users — good no-op guarantee. (positive)

No blocking issues found.
