> AI code review — automated review for reference; please use your judgment.

- website/src/components/UserStoriesCollage/styles.module.css:71 / website/src/pages/skills/styles.module.css:1007 — Fix verified sound: `--ifm-color-emphasis-0`/`emphasis-900` are theme-inverted contrast pairs, so the active-pill rule stays readable in both themes (the existing `[data-theme='dark']` override continues to win where present), and `var(--ifm-color-emphasis-0, #f7f8fa)` on the primary hover button is correct with a sane fallback. Why it matters: using a *background* token as a text color was the root cause; switching to a purpose-built foreground token fixes the class, not just the instance. Suggestion: none required — I grepped the PR head and no other stylesheet still uses `color: var(--ifm-background-color)` (only these two explanatory comments remain), so the sweep is complete.

_— hermes-week-review automated review (reviewer-d)_

No blocking issues found.