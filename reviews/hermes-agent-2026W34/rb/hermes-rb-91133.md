> AI code review — automated review for reference; please use your judgment.

Solid solution to a genuinely gnarly parsing problem: the existing-models lookup (exact match first, longest-prefix candidates second, with the `:"-in-sub-path guard preventing `qwen3` from stealing `qwen3.5:4b.context_length`) resolves real ambiguity against live config state instead of guessing, the creation fallback (`rsplit` once, colon-in-leaf means the whole tail is a model tag) handles the common Ollama shapes, explicit quoting/backslash escaping gets a proper mini-parser including trailing-escape recovery, and all three operations (set/get/unset) share the splitter so they can't disagree. The eight regression tests cover update/create/collision/quoting/get+unset/e2e-resolution/catalog-nesting-preservation.

No blocking issues found.

Nit: two small follow-ups — (a) the ambiguity rule ("under ````custom_providers…models````, a dotted path's *last* segment is the leaf; quote the model id for anything fancier") deserves one line in the `config set` docs since it's now load-bearing behavior; (b) `hermes_cli/config.py` ends with four stray blank lines after the new tests were added elsewhere — trivial tidy-up.

— reviewer-a · automated agent review (Hermes week-review)
