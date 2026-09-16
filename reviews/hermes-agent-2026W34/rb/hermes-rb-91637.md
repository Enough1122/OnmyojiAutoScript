> AI code review — automated review for reference; please use your judgment.

The intent is right and the URL-preservation test is a thoughtful touch. Two real gaps:

- apps/desktop/src/store/suggestion-providers/skill.ts:222 — issue — `\s\/[\w-]+` requires whitespace *before* the slash, so a command at position 0 of the draft ("/vault summarize this") is never stripped and still triggers the prose suggestion — why it matters — beginning-of-message is the single most common way a slash command is authored, so the reported symptom survives in exactly that shape; every test case conveniently starts with prose — suggestion — use `(?:^|\\s)\/[\\w-]+` (replace with a single space either way), and add a leading-position case to the tests.

- apps/desktop/src/store/suggestion-providers/skill.test.ts:137 — issue — `hitsAfterSanitize` re-implements the production regex inline instead of exercising the real code path — why it matters — these tests pin a *copy* of the behavior; if the sanitizer in skill.ts changes (e.g., for item 1), the tests stay green while the bug ships — suggestion — export the sanitizer from skill.ts (e.g., `stripSlashTokens(text)`) and have both the provider and the tests call it.

- apps/desktop/src/store/suggestion-providers/skill.ts:223 — nit — `[\w-]` is ASCII-only; a skill whose name contains non-Latin characters won't be stripped and will keep self-triggering suggestions — probably acceptable today, worth a one-line comment or `[^\s\/]+` if you'd rather fail toward stripping.

No blocking issues found — item 1 should land before merge since it's the primary invocation shape.

— reviewer-b (automated review)
