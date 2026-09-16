> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

The PTY direction is right for tmux dimension bugs, but this implementation needs another pass — several behaviors from the old path were dropped and the new one has lifecycle problems:

1. hermes_cli/main.py:_launch_tui (~line 2683-2790) — the PTY branch loses two pieces of the old flow: `_print_tui_exit_summary(...)` for exit codes {0, 130} no longer runs on the happy path, and the `finally: os.unlink(active_session_file)` cleanup is no longer reached on success — a completed TUI session leaves a stale active-session file behind, which changes what the next launch resumes into. Restore both on the PTY path (summary after `proc.wait()`, unlink in a `finally` around the whole thing).

2. hermes_cli/main.py:_poll_tmux_size — the poller thread has **no stop condition**: after `proc.wait()` returns and `_launch_tui` proceeds, the daemon thread keeps shelling out to `tmux list-panes` twice a second until process exit. Add an event/flag checked each loop (cleared after wait) so teardown is prompt.

3. hermes_cli/main.py:_poll_tmux_size — the monotonic "max size seen" rule means the TUI can never *shrink*: once any poll observes a larger pane, smaller resizes are ignored forever. Combined with the unconditional `resize-window -x max(cols,120) -y max(rows,40)` at startup (which overrides a deliberately smaller user pane), users on small terminals get a layout they can't reduce. At minimum drop the forced startup resize and forward both grow *and* shrink; keep a floor only if tmux itself requires one.

4. hermes_cli/main.py:_forward_sigwinch — installing a global no-op SIGWINCH handler clobbers whatever handler the host process had, process-wide, for the lifetime of the TUI child. Since it intentionally does nothing, simply don't install it (the comment already says the poller handles resize).

Minor: duplicated imports (`os`, `subprocess`, `signal` re-imported inside the branch), and every failure mode in the poller is swallowed silently — one debug log on first failure would save future debugging.
