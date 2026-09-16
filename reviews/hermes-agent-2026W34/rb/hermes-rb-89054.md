> AI code review — automated review for reference; please use your judgment.

Review of "fix(i18n): translate French /status diagnostics". Clean completion of the French status surface, with proper French typographic conventions (space before colons and percent signs), and — the valuable part — a regression test asserting NO `gateway.status.*` value still equals its English source, which turns "silent fallback to English copy" into a CI-visible failure. Two nits:

- the new test pins only the `gateway.status.` namespace; when other surfaces get their French pass, either extend the prefix list or fold this into #89056's general source-equality audit so coverage grows automatically.
- `tokens` wording ("Jetons facturés depuis la création") reads slightly formal vs the rest of the file's tone; native-speaker sign-off would settle it — not blocking.
