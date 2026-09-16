> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Solid locale addition overall: full pl.ts (3.2k lines), catalog/alias/picker wiring, normalization covering pl-PL / pl_pl / polish / polski, and tests that pin resolution from config, the alias table, and even document honestly that some sections are still English pending follow-up.

- **apps/desktop/src/i18n/languages.ts:4-5 - the `Locale` type is now defined twice.** Instead of adding 'pl' to the canonical union in types.ts, this shadows it: `export type Locale = OriginalLocale | 'pl'`. Any module importing `Locale` from './types' (components, helpers, persisters) keeps a two-valued type that rejects 'pl', while i18n internals accept it - a divergent-types hazard that TypeScript will happily let compile until someone compares them. Please move 'pl' into the canonical Locale in types.ts and delete the shim; the `satisfies` on LOCALE_OPTIONS will then verify everything for free.

- **languages.ts ~39 - an escaping artifact landed in a comment:** `"japanese\"/"traditional\""` now renders with literal backslashes. Trivial fix, but worth catching before merge since it sits directly above the new option.

- Nit: languages.ts lost its trailing newline at EOF again; and given three of six locales are partial, a tiny CI check asserting per-locale key coverage (or an explicit documented coverage percentage per locale) would stop silent drift as keys evolve.

No blocking issues found.