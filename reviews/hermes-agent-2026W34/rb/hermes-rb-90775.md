> AI code review — automated review for reference; please use your judgment.

Review of "feat(api): allow runs without local session persistence". Well-executed privacy/control surface: `store: false` threads through _create_agent (session_db=None + pre-run `_persist_disabled`), the JSON snapshot and request-debug dump chokepoints both gate on it, delegate_tool makes the opt-out TRANSITIVE for children (nice catch — lazy state.db opening would otherwise have leaked), and the e2e test asserts state.db, session_*.json, and request_dump_*.json all stay absent. Suggestions:

1. gateway/platforms/api_server.py:6723 (other writers?) — transcript gating now covers SessionDB, snapshots, and debug dumps, but please sweep for other transcript-adjacent side effects a turn can trigger (memory/learning extraction hooks, session_search indexing, post-run summarizers) and either gate them on `_persist_disabled` or state explicitly in docs that they still fire for store=false runs — "caller-managed transcript" users will assume nothing durable lands anywhere.

2. gateway/platforms/api_server.py:6780 (override semantics change) — `allow_session_override=store` means a client reusing an existing session id with store=false now IGNORES that session's /model override and gets stricter 400s on route/provider mixes that previously resolved via the override — correct for ephemeral runs, but it's a subtle breaking edge for integrators that mix interactive and store=false calls on one session id; call it out in the API changelog.

3. gateway/platforms/api_server.py:6725 (restart continuity) — with store=false, previous_response_id resolves against in-memory runs only; after a server restart the reference vanishes — make sure that path returns a clean 404-style error rather than silently starting a fresh conversation, and say so in the capabilities/docs description.

No blocking issues found.
