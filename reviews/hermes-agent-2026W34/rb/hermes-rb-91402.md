> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Both halves are welcome: `initial_query` removes a real friction step (`/ms foo` lands filtered and still editable), and exposing `search_labels` fixes genuine false-positive filtering against decorated display strings (the kimi/zendesk example is a great motivating case). The extended-key pop/push around `curses.wrapper()` explains the stray `9;5u` leakage precisely, and the guard stack (TTY check + lazy-import probe + never-raise) keeps it inert outside real terminals. Tests cover seeding, empty-query no-op, non-TTY silence, and import-failure fallback. Findings:

1. hermes_cli/curses_ui.py:489 — the *restore* branch re-probes `_extended_key_modes_active()` rather than remembering whether this invocation actually popped. If the probe flips between pop and push (e.g. `cli` becomes unimportable mid-session, stdout's TTY status changes under redirection tricks), the terminal is left with Kitty/modifyOtherKeys popped while the surrounding prompt_toolkit loop believes they're pushed — the exact class of desync this fix exists to prevent. Capture a local `popped = True` after a successful pop and make the finally-block restore unconditionally on that flag.

2. Scope — two unrelated fixes ride together (search pre-fill API vs. terminal-mode leak plumbing). Both are good; splitting them into separate commits (or PRs) would let the terminal fix land independently since it also benefits every other curses surface.

3. hermes_cli/curses_ui.py:952 — a caller-supplied `search_labels` whose length mismatches `items` silently disables search entirely (documented, tested), but nothing tells the caller. Since misalignment would otherwise corrupt index mapping, prefer a one-line warning log over pure silence so integration bugs surface during development instead of shipping as mysteriously dead filtering.
