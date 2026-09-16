> AI code review — automated review for reference; please use your judgment.

Clean configurability extraction: default preserved exactly (hardcoded 2 → shipped default 2), the gate reads the agent attribute with a getattr fallback for agents built outside `init_agent`, malformed values degrade to the default, and the init-path tests cover configured/clamped/default/garbage. One design question and two nits:

1. agent/agent_init.py:~2038 — the floor clamp contradicts its own test comment. The test says "0 would mean 'never fall back' — clamped to 1", but `retry_count >= 1` is the *most aggressive* setting (fallback on first transport failure), not "never": a user who sets 0 expecting to disable eager fallback gets the exact opposite of what they asked, silently. Either give 0 a real meaning (`0 = disabled`, i.e. skip the transport-failure arm entirely) or document loudly that any value < 1 behaves as 1. As written, the clamp manufactures a footgun.
2. No upper bound: `transport_fallback_threshold: 100000` is a valid way to say "never", but nothing distinguishes intent from a typo. If you adopt the 0-disabled semantic from item 1, consider rejecting values above a sane ceiling instead of clamping.
3. tests:`test_fallback_gate_references_configured_threshold` — an `inspect.getsource` substring check pins that the gate *mentions* the attribute, not that it *uses* it (a second stale hardcoded `>= 2` branch elsewhere would still pass). A behavioral test — stub the API callable to raise two transport failures and assert fallback fired at N=1 / didn't at N=3 — would actually pin the gate. Understandable if the loop is too heavy to unit-drive; noting the gap. (nit)
4. config_defaults.py — good comment placement next to `api_max_retries`; consider cross-referencing that this interacts with `api_max_retries` (retries happen *before* the fallback arm fires, so effective latency ≈ retries × backoff × threshold). (nit)

No blocking issues found.
