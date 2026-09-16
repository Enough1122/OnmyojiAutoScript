> AI code review — automated review; please use your judgment.

Review of "feat(gateway): session_is_busy public API + pre_gateway_dispatch agent_busy context". Useful surface: the getattr-defensive `session_is_busy` works for bare `object.__new__` runners, the kwarg plumbing is wrapped in the existing try/except, and coverage is broad. Concerns:

1. tests/test_session_is_busy.py:247 (test promises an API that doesn't exist) — `test_receives_agent_busy_after_in_kwargs` claims the hook "can also observe agent_busy_after", but the implementation never passes such a kwarg: the after-value is computed post-hook and only written to a DEBUG log — either ship `agent_busy_after` in the invoke_hook kwargs (arguably more useful than before alone) or rename the test; as written it documents a contract plugins will rely on and not find.

2. gateway/run.py:16576 (backward-compat risk) — two new kwargs now flow into every pre_gateway_dispatch invocation; if `invoke_hook` filters kwargs by the handler's signature this is invisible, but if it forwards blindly, an EXISTING plugin with a strict signature raises TypeError on every inbound message — and because the caller catches Exception and proceeds with `_hook_results = []`, that plugin would be silently disabled rather than failing loudly — please confirm invoke_hook's tolerance (or add a signature-inspection test) and note it in hermes_cli/plugins.py.

3. gateway/run.py:6820 (documented-but-divergent predicates) — `session_is_busy` (raw key membership, includes pending sentinels) can disagree with `_is_session_running` (peeked SessionState, requires turn.agent); the test file explicitly says the mismatch "is expected", yet the public docstring doesn't tell plugin authors when/how they diverge — put that guidance on the method itself, since that's where external callers will look first.

4. tests/test_session_is_busy.py vs tests/gateway/test_pre_gateway_dispatch.py — both files add near-identical busy/idle/session_key hook tests with duplicated `_clear_auth_env`/`_make_event`/`_make_runner` fixtures that will drift independently — consolidate into one location (or shared helpers) so regression guards stay in sync.

5. tests/test_session_is_busy.py:307 (nit) — file lacks a trailing newline (`\ No newline at end of file`).

No blocking issues found, but items 1-2 deserve resolution before this becomes plugin-facing API.
