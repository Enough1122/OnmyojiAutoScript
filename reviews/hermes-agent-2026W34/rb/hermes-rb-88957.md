> AI code review — automated review for reference; please use your judgment.

Right fix for a real regression class: extended-key protocols report Ctrl+J as a *modified printable* (`[106;5u`, `[27;5;106~`) instead of the legacy LF byte, so enabling those protocols silently ate the documented Ctrl+J newline binding. The new `isCtrlJNewline` predicate is exactly right — strict ctrl-only with every other modifier excluded (tested), placed before the `k.return` branch so it can't submit, and driven through the real parser in tests rather than mocked shapes. Points:

1. ui-tui/src/components/textInput.tsx:`isCtrlJNewline` (~246) — `input.toLowerCase() === 'j'` also matches when a non-extended path delivers name `j` with ctrl (legacy byte already handled elsewhere?). If the legacy LF handler runs *earlier*, fine; otherwise confirm no double-insert when both the byte path and this predicate fire for the same press. The test suite doesn't cover that interleaving. (nit)
2. Adding `TMUX` to `shouldPreserveCtrlJNewline` first-in-line is correct (tmux collapses Ctrl+J to LF), and on macOS-under-tmux the outcome coincides with the existing darwin bare-LF rule — no behavioral fork introduced. (positive)
3. Consider exporting `ReturnDecisionKey` alongside the predicate so tests and future callers stop re-declaring structural types. Very minor. (nit)

No blocking issues found.
