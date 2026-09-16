> AI code review — automated review for reference; please use your judgment.

Review of "feat(egress): let bot profiles reuse an opt-in shared proxy". The owner-resolution design (opt-in flag read only from the default profile, profile-local proxy wins, override always reset in `finally`) is sound and well tested. Findings:

1. tools/environments/docker.py:1207 — the provider-key collision check switched from name-based (`{m.real_env_name for m in load_mappings()}`) to value-equality against proxy tokens — a `docker_env` entry that injects a REAL provider key under its canonical name (e.g. `OPENROUTER_API_KEY: sk-real-...`) no longer collides, because its value differs from the proxy token; that is exactly the live-secret-into-sandbox leak the deleted comment warned about — recommend unioning the old name-based set (computed from the resolved owner's mappings) with the new value-derived set so both shapes are caught.

2. tools/environments/docker.py:1253 — merge precedence now gates on `_enforce_egress`, but this diff removes the only in-scope assignment of that name (the old per-site `_enforce_egress_merge` recomputation) — if `_enforce_egress` isn't bound earlier in `__init__` (e.g. from `_egress_enforce_on_docker()`), every egress+docker_env flow hits NameError at runtime and the collision tests can't see it because they raise before this line — please confirm the binding exists on all paths or add one.

3. tools/environments/docker.py:494 — the improved "Start it from the default profile" hint fires only when `status.pid/status.listening` fail after `configured` passes — there is no test for the shared-opt-in-but-daemon-down path, which is the most likely misconfiguration for Bot Mode users — worth adding a case asserting both the raised message and the enforce=False silent-return branch.

4. tools/environments/docker.py:402 — `_resolve_egress_proxy_owner()` temporarily flips the process-global HERMES_HOME override and performs up to two extra config loads per sandbox creation — correct under today's serial provisioning, but non-reentrant; add a brief comment or lock if container setup ever goes concurrent, so a parallel thread doesn't observe the owner scope mid-flight.

5. tests/test_iron_proxy.py:664 — the suite covers reuse, isolation-without-opt-in, and profile-local preference, but not the documented isolation promise that egress management commands (stop/reload/setup) issued from a named profile never touch the shared default daemon — a guard test pinning that behavior would protect the feature's core contract.

Docs (egress-internals.md, iron-proxy.md) accurately describe the new semantics — good. Nothing else blocking beyond items 1-2, which deserve a look before merge given the security framing.
