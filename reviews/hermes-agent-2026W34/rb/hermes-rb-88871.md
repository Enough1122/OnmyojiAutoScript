> AI code review — automated review; please use your judgment.

Precise root-cause fix with an unusually good regression test. The bug: `_persist_live_session_system_prompt` runs on the RPC dispatcher thread (model.switch / config.set), where the `_SESSION_CWD` contextvar isn't set, so the rebuilt system prompt recorded the process `TERMINAL_CWD` instead of the session's working directory — and because later turns only rebuild when `_cached_system_prompt` is None, the poisoned line persisted indefinitely. Binding the session context before the rebuild and clearing it in `finally` addresses exactly that, coexisting correctly with the existing `profile_home` override. The test drives the real function on a bare thread (the dispatcher shape) and asserts both the cached and persisted strings contain the session cwd while a planted wrong `TERMINAL_CWD` is ignored.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
