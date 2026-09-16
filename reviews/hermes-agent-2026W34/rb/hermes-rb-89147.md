> AI code review — automated review for reference; please use your judgment.

Clean alias work: every new spelling is wired at both layers (parser `aliases` and the dispatcher sets in `config_command`/`mcp_command`/`memory_command`), the new `tests/hermes_cli/test_subcommand_aliases.py` covers parse *and* dispatch for all eight spellings, and the flakiness fix in `tests/cron/test_parallel_pool.py` (sleep → `done_event.wait`) makes that barrier test deterministic instead of timing-luck.

No blocking issues found.

Nit: two scope nits worth a line in the PR body — (1) the cron-test determinism change is unrelated to aliases and would be easier to track as its own PR or at least a body bullet; (2) the alias matrix is asymmetric relative to the title (`config` gains list/ls but not `status`, `mcp` gains `status` only), so stating the intended per-command matrix in the body (or the docs' command reference) will save the next contributor a puzzled grep.

— Reviewed by Hermes AI reviewer (reviewer-f2)
