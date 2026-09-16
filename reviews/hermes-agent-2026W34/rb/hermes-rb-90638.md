> AI code review — automated review; please use your judgment.

Right fix at the right layer: both network git probes (`ls-remote` and the local fetch) share one `_git_probe_timeout()`, the 30s default is justified by the documented latency profile, the `HERMES_UPDATE_GIT_TIMEOUT` override rejects non-positive/garbage values back to the default, and four tests pin default, override, all invalid spellings, and actual propagation into `subprocess.run`. Since the check runs on a daemon thread, the generous ceiling costs nothing on fast links.

No blocking issues found.

Nit (`tests/hermes_cli/test_banner_git_state.py:~132–137`): `test_git_probe_timeout_default` does `os.environ.pop(...)` inside `patch.dict(os.environ, {}, clear=False)` — patch.dict won't restore a key removed directly, so if the developer's shell exports that variable it stays deleted for the rest of the test session; `monkeypatch.delenv(..., raising=False)` (used elsewhere in this suite) restores properly.

— reviewer-a · automated agent review (Hermes week-review)
