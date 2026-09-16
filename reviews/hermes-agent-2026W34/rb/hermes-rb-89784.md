> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Elegant resolution of the docs-vs-reality gap: `runpy.run_path(..., init_globals={...})` delivers exactly the three documented helpers into user globals without polluting them with `runpy`/`hermes_tools`, preserves traceback line numbers against the untouched source, keeps explicit `from hermes_tools import …` working, fixes `sys.argv` to `[script]` (asserted by test), and the remote path stays injection-safe since every argv element is `shlex.quote`d. The real-subprocess file-transport test plus the alongside-explicit-imports case cover both transports meaningfully. Findings below are minor:

1. tools/code_execution_tool.py:_USER_SCRIPT_RUNNER — the helper set is enumerated twice inside one string (the `from hermes_tools import …` clause *and* the `init_globals={…}` mapping). Adding a fourth documented helper means editing two spots in an embedded string; build it from a single `_DOCUMENTED_HELPERS = ("json_parse", "shell_quote", "retry")` tuple (`f"from hermes_tools import {','.join(...)};…init_globals={{{','.join(f\"'{n}':{n}\" for n in ...)}}}"`) so the contract has one source of truth.
