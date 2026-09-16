> AI code review — automated review for reference; please use your judgment.

Review of "fix(relay): graceful degrade when nemo_relay is not provisioned". Right log-hygiene fix with unusually good tests: the degrade notice is announced exactly ONCE per process across N profile initialisations (pinned by test), unknown init failures keep their WARNING+traceback (also pinned), and the tests assert the ABSENCE of traceback frames rather than just presence of the info line. `_reset_for_tests` clears the new set. Suggestions:

1. agent/relay_runtime.py:34 (ImportError catch breadth) — ImportError/ModuleNotFoundError also cover CIRCULAR imports and genuine packaging corruption inside the binding, which would now masquerade as "simply not provisioned" and drop to a one-line INFO — consider narrowing on `getattr(exc, 'name', '')` matching the expected relay module so a broken-but-present install still gets its traceback.

2. agent/relay_runtime.py:28 (nit, unbounded set) — `_ANNOUNCED_REASONS` keys on the full exception message; a vendor wheel whose import error embeds varying paths could grow the set across a long-lived gateway — cap it or key on exception type + module name only.

3. docs nit — the INFO line says tool intercepts/managed execution are disabled; a pointer to the extra that PROVISIONS the binding (`pip install hermes-agent[relay]` or equivalent) would turn the notice directly actionable for admins.
