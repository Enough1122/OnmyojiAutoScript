> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): scope skill discovery to the calling session's project". Correct diagnosis and thorough fix: both completion RPCs carry session/cwd, the backend pins `_SESSION_CWD` for the scan via a context manager (also applied to skill INVOCATION and the is-skill dispatch guard, so repo skills are invokable, not just listable), cache keys are workspace-scoped, and tests pin the three properties that matter — project scoping, no override leak after the request, and restore-on-handler-raise. Suggestions:

1. tui_gateway/methods_complete.py:337 (client-trusted cwd) — `complete.slash`/`commands.catalog` take the cwd from CLIENT params while other handlers use the session record's pinned cwd; a buggy or hostile renderer can therefore scan any directory it names — since a session already exists at this point, prefer the server-side session cwd as authority (fall back to params only for pre-session contexts).

2. process-wide skill cache (residual thrash) — your own comment notes one session's scan previously poisoned the cache for everyone; scoping fixes CORRECTNESS (each request rescans under the right cwd), but if `scan_skill_commands` retains any shared memoization, two sessions in different projects now simply thrash it — consider keying that cache by the resolved project root so repeat completions stay cheap.

3. apps/desktop/src/app/chat/composer/hooks/use-slash-completions.ts:80 (nit, key collision) — cache keys join raw values with `|` (`${cwd}|${sessionId}`); a cwd containing "|" can collide with a different (cwd, sessionId) pair — `JSON.stringify([cwd, sessionId])` is collision-proof for the same cost.
