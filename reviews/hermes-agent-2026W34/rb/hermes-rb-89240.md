> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Proper fix for a nasty split-brain install: exporting `HERMES_HOME` right after the default assignment makes every installer child (`skills_sync.py`, setup wizard) resolve the requested home, and baking `export HERMES_HOME="${HERMES_HOME:-<install-home>}"` into all six launcher templates keeps runtime invocations pointed there while still letting a caller's explicit env win. Correcting the skills-sync log lines to print the real path removes the misleading success messages that made the bug invisible. The contract tests are the highlight — asserting export-after-assignment ordering, that every launcher heredoc carries the baked default (with a self-updating ≥6 count), and that the hardcoded `~/.hermes` messages can never return.
