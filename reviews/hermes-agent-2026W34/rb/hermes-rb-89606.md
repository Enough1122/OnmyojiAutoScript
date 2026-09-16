> AI code review — automated review for reference; please use your judgment.

Review of "fix(cli): clear a typed draft over Ctrl+C/Ctrl+Q instead of interrupting mid-stream". Right priority inversion, implemented the same way as the TUI's #89171 fix — a pure `resolve_ctrl_c_composer_action` with the full truth table tested — so CLI and TUI now agree that a typed correction must never kill an in-flight turn. The docstring/comment updates document the new precedence honestly, and the 2-second force-exit latch survives intact inside the interrupt branch. Two small notes:

1. apps/desktop/../cli.py handle_ctrl_c — with a non-empty draft DURING a run, press #1 clears the draft and press #2 now INTERRUPTS the running agent (previously it would have exited); that ordering change is defensible but worth one line in release notes since muscle-memory users who relied on "double-tap to bail out entirely" will discover their session keeps running.

2. nit — the pure function is tested exhaustively, but neither handler's WIRING (buffer reset actually firing, attachment list clearing) has a test; one integration-style assertion per handler would close the gap between decision and effect.
