> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct loosening of an over-strict validator: platform toolsets legitimately reference registered plugin toolsets (`known_plugin_toolsets`) and configured MCP servers by name, plus the `no_mcp` sentinel — none of which `validate_toolset` knows about, so operators got spurious migration warnings for working configs. The defensive `isinstance` guards around the raw config shapes are appreciated, and threading the extras through as an explicit keyword keeps the validation helper honest for callers without config context.

Nit (non-blocking): tests/hermes_cli/test_toolset_validation.py:49 — the new test only asserts the happy path (warnings == []). Add one line proving the gate still bites while extras are active, e.g. `{"webhook": ["beca-webhook", "bogus"]}` yields exactly the bogus warning — otherwise a future refactor that flips `name in extra_valid or is_valid_toolset(name)` into unconditional acceptance would pass CI silently.
