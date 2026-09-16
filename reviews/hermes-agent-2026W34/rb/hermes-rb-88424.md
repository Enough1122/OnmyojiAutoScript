> AI code review — automated review for reference; please use your judgment.

Real leak fix: one-off /v1/runs agents (no stored session, no gateway key) previously lived on past their turn holding memory providers and clients; closing them post-turn is right, keeping persistent sessions open is correct, and both lifecycle outcomes are regression-tested. Points:

1. gateway/platforms/api_server.py — **two different one-off predicates**: `_create_agent` call sites compute `close_session_on_finish = (stored_session_id is None and not gateway_session_key)`, while `_run_sync` uses `one_off_session = not bool(session_id)` where `session_id` already includes `body.session_id`. A request carrying an explicit body `session_id` but no stored/gateway key therefore gets `close=True` on the async path and `close=False` on the sync path — divergent lifecycles for the identical request depending on execution mode. Unify on one predicate (probably the create-site one) and derive both from it.
2. Same file — the predicate is spelled out inline three times now; a tiny `def _is_one_off(stored, gateway_key)` helper would keep them from drifting exactly like item 1.
3. Confirm `agent.close()` is safe to call when the run *failed* mid-turn (the finally placement suggests yes); if close flushes memory providers, a failed turn's partial state may write where callers expect nothing persisted. One test with a raising run_conversation + close flag would pin it. (nit)

No blocking issues found beyond item 1's asymmetry.
