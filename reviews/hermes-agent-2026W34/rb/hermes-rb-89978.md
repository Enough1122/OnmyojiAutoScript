> AI code review — automated review for reference; please use your judgment.

Right reconciliation point and correct polarity: reconciling inside `_live_session_payload` under `history_lock` means every reconnect/activate consumer sees a truthful projection, and leaving a *missing* thread untouched avoids clobbering the brief window where `running` is set before worker registration — that asymmetry is documented in the docstring, which is what makes it safe. The dead-thread test pins both the payload shape (`running: false`, no `inflight`) and the session mutation. One nit:

- tui_gateway/server.py:8841 — nit — `is_alive()` raising is treated as "leave everything pinned"; a comment naming that choice (fail-safe toward busy rather than idle) would clarify it isn't an oversight.

No blocking issues found.

— reviewer-b (automated review)
