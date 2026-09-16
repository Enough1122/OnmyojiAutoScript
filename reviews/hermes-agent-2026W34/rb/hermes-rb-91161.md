> AI code review — automated review for reference; please use your judgment.

Thoughtful leak-regression coverage: the readiness-probe test wraps real `sqlite3` connections while deliberately **preserving** the "context manager does not close" semantics, so the test fails precisely if the probe ever stops calling `.close()`/`contextlib.closing()`; the MCP test drives 50 real tool invocations through the public server surface rather than poking internals; and the EventBridge test proves the long-lived polling connection is reaped on `stop()` with proper event timeouts instead of sleeps. The `disk_usage` stub also de-flakes the pre-existing healthy-readiness test.

No blocking issues found.

Nit (`tests/gateway/test_readiness.py:~36`): `monkeypatch.setattr(readiness.sqlite3, "connect", ...)` patches the shared `sqlite3` module object rather than a readiness-local binding, so any code touching sqlite3 on another thread mid-test sees the tracker too; harmless today (serial suite), but patching a module-level `readiness._connect` indirection (or documenting why global is safe) would keep the blast radius obvious.

— reviewer-a · automated agent review (Hermes week-review)
