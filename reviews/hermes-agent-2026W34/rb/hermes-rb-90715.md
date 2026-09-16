> AI code review — automated review for reference; please use your judgment.

Correct containment fix for #90699: `_PROFILE_ID_RE` (`[a-z0-9][a-z0-9_-]{0,63}`) structurally forbids separators and dot-segments, validating the *normalized* name first means title-cased labels still work, and falling back to the launch profile matches existing unknown-profile semantics. The test asserting `get_profile_dir` is never reached for malicious input pins exactly the right property. Suggestions:

1. tui_gateway/server.py:1528 — rejection is completely silent: a probing client sending `../../etc` gets launch-profile behavior identical to an unknown profile, so there is no way to tell misconfiguration from intrusion attempts in the logs. Catch `ValueError` explicitly and `logger.warning("Rejected invalid RPC profile param: %r", name)` before returning None (keep other exceptions at the current silent level).
2. server.py:1531 — `get_profile_dir` re-normalizes internally, so the value validated and the value resolved can in principle differ by a future change to either helper. Binding once (`canonical = profiles_mod.normalize_profile_name(name)`, then validate and resolve `canonical`) makes the invariant local and obvious.
3. tests/test_tui_gateway_server.py — consider one more case: a reserved name (`"root"`, `"hermes"`) — those are rejected by a different branch of `validate_profile_name` than the regex, and asserting they also fall back to launch-profile keeps both rejection paths covered. (nit)

No blocking issues found.
