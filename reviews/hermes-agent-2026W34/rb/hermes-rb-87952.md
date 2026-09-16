> AI code review — automated review for reference; please use your judgment.

Review of "feat(desktop): add per-block word-wrap toggle to code blocks". Nice self-contained UX addition: hover-revealed Switch + label (useId-wired), the toggle state expressed as a `data-wrap` attribute the stylesheet reacts to (with the !important targets and WHY each override is needed documented inline), CopyButton regrouped with focus-within so keyboard users still reach both controls, and tests covering the flip. Suggestions:

1. apps/desktop/src/i18n/types.ts:2587 (recurring locale gap) — new keys land in en/types/zh only; ja, zh-hant, ar are absent again — same pattern flagged on #90757/#91317. If Translations is enforced at build time this fails CI; if not, those locales silently render English. Either complete the set or establish a CI check that every locale file satisfies Translations.

2. nit — wrap state is component-local and resets when a message unmounts (session switch, virtualization); fine for an ephemeral affordance, but if users report having to re-toggle long-log blocks, persisting keyed by message+block index would be the follow-up.
