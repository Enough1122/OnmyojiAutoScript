> AI code review — automated review; please use your judgment.

Good platform-parity fix: Windows profile deletion previously left both persistence mechanisms (Scheduled Task + Startup folder) and any running gateway behind. The new branch reuses the canonical `gateway_windows.uninstall()` under profile-scoped `HERMES_HOME` (the test asserts the scope is entered *and* restored), and `_stop_gateway_process` now resolves the PID through the verified runtime record (`get_running_pid` with lock fallback) instead of hand-parsing `gateway.pid` — covering task-spawned Windows gateways that legitimately have no PID file — while routing termination through `terminate_pid` for the Windows-safe primitive. Both behaviors have focused tests, including a liveness-sequence mock for the lock fallback.

No blocking issues found.

Nit (`hermes_cli/profiles.py` `_cleanup_gateway_service`:~1795): the surrounding `except Exception` prints ⚠ but continues to process teardown; on Windows a failed `uninstall()` means the task/Startup entry survives deletion silently beyond that one line — consider at least naming the failed phase in the warning (\"service cleanup\", \"windows uninstall\") so users know what to check manually.

— reviewer-a · automated agent review (Hermes week-review)
