> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right UX call: an accidental single Ctrl+C at an empty prompt should never kill a long-lived CLI session, and the fix keeps the agent-path double-press (`_last_ctrl_c_time`) completely separate from the new idle timer so an interrupt followed moments later by an idle press can't accidentally arm a force-exit. Systematically zeroing `_last_idle_ctrl_c_time` on every non-exit branch (overlays cleared, buffer cleared, pickers cancelled) prevents a stale first press from combining with an unrelated later one — the subtle bug this kind of guard usually ships with.

Nit (non-blocking): no regression test pins the state machine — `handle_ctrl_c`'s branches are reachable with a mocked `event.app`, and the valuable assertions are exactly the non-obvious ones: single idle press sets the timer but not `_should_exit`; two presses <2s exit; a buffer-clear between presses resets the idle timer while leaving the agent-path timer alone. Without them, the next handler edit can silently regress either timer's independence.
