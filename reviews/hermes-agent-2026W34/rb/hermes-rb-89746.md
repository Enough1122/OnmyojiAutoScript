> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct precedence repair: `display.background_process_notifications: off` is an operator kill switch and shouldn't be re-enabled per-call by a model-chosen `notify_on_complete=True` — the old `and not agent_notify` conjunction let exactly that happen. Keeping the wait-loop intact preserves exit logging and watcher cleanup while silencing delivery, and the regression test is well-constructed: it sets a *routable* dm chat_type so any real delivery attempt would be observable through the mocked adapter, then asserts neither `send` nor `handle_message` fired.
