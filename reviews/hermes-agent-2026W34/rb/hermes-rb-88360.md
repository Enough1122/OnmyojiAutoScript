> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right unification at the right layer: a single `resolve_agent_isolation` contract (explicit flags > env vars > default) consumed identically by ACP, API server, gateway foreground/background, and CLI background closes the "--safe-mode only worked on some surfaces" gap. Two details stand out: composing with the per-platform `skip_context_files` latency opt-out via OR (context skipping composes; memory follows isolation alone) matches each knob's actual purpose, and adding `skip_memory` to `_agent_config_signature` is essential — without it, cached agents would keep serving memory-injected prompts after isolation flipped. Findings below are minor:

1. agent/isolation.py:resolve_agent_isolation — the function always returns two equal booleans and its docstring says so; a `tuple[bool, bool]` return invites future callers to imagine they can diverge. Either return a single `isolated: bool` and let call sites pass it to both kwargs, or return a tiny frozen dataclass (`IsolationFlags(skip_context_files, skip_memory)`) if you anticipate the flags genuinely splitting later.
