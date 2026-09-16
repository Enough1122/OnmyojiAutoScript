> AI code review — automated review; please use your judgment.

Careful fail-fast design: the `is not True` arm check (with its MagicMock-config rationale), unconditional failure recording shared by both the log-and-continue and assert paths, the Relay-only exemption distinguishing by-design zero adapters from failure, active-profile coverage via `adapters`/`_failed_platforms` including the queued-for-retry case, remedy text embedded in the abort message, and an unusually complete test matrix (default-off byte-compat, truthy-non-bool non-arming, full config round-trips including nested-key precedence and YAML string coercion).

1. `gateway/run.py:~14979` (`_start_secondary_profile_adapters`) — `self._profile_startup_failures = {}` **resets the dict after the primary profile's adapters have already started**, discarding any failures `_start_one_profile_adapters` recorded for the *active* profile during the primary startup loop — why it matters: the assertion then judges the active profile only via `self.adapters`/`_failed_platforms`, so a platform that failed creation (recorded pre-reset, adapter absent but not in `_failed_platforms`) can pass the gate with its evidence erased — suggestion: don't reset here (the field starts empty in ````__init__````); or merge into the existing dict rather than replacing it.

2. Nit: the new operator-facing flag has no entry in `config_defaults.py`, the gateway settings docs, or any website page — an opt-in abort switch that users can't discover except by reading source undercuts its purpose; add a row beside `multiplex_profile_allowlist`.

3. Nit (`:~15178–15184`): `_profile_relay_served` (like the failures dict) is never pruned on in-process gateway restarts; benign today given single-startup lifecycle, worth one comment stating the assumption.

— reviewer-a · automated agent review (Hermes week-review)
