> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-scoped escape hatch: extracting `_ws_keepalive_policy(host)` turns an inline ternary into a testable decision function, loopback keeps its unconditional ping-off (false-disconnect history preserved in comments), public/tunnel binds keep the 20/20 half-open detection by default, and the new `HERMES_DASHBOARD_WS_PING_OFF` env covers exactly the reported deployment shape — bind 0.0.0.0 for a docker-bridge proxy while serving only local clients, where the ping's false-positive risk exists without any tunnel to detect. Tests pin all three regimes including the full truthy/falsey env-value matrix via the repo's shared `env_var_enabled` helper.
