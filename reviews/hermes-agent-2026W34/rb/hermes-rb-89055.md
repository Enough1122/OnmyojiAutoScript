> AI code review — automated review for reference; please use your judgment.

Review of "docs(i18n): document translation contributions". Thorough contributor guidance: the four-surface table with each source of truth prevents the classic cross-surface edit mistake, the placeholder/Markdown-preservation rules cover the actual breakage modes (multiplicity included), the YAML "\n"-escape gotcha is real and rarely documented, and "describe partial coverage honestly — a fallback to English is safe" sets exactly the right expectations. Pointing translators at runtime verification (`agent.i18n.t()`) rather than eyeballing YAML is the detail most CONTRIBUTING guides miss. One nit:

- CONTRIBUTING.md — consider cross-referencing #89056's locale source-equality audit script here as the tool for finding untranslated strings once it lands.
