> AI code review — automated review for reference; please use your judgment.

Well-bounded feature: `client_platform` is allowlisted server-side ("openwebui" or nothing), an unrecognized value is deliberately inert rather than an error so callers can send it speculatively, the None path is byte-compatible with pre-change behavior, and the tests cover pass-through, 400-on-non-string, and the untouched-default contract. The openwebui hint itself correctly drops api_server's "non-image files aren't intercepted" caveat, with a documented real-world failure (PPTX leaked as a raw host path) justifying it. Points:

1. gateway/platforms/api_server.py:~2966 — `"openwebui" if client_platform == "openwebui" else "api_server"` now flows into `agent.platform`, which persists into session rows and telemetry grouping. Confirm nothing validates `platform` against a fixed enum downstream (session DB writers, dashboards, metric labels) — a new value appearing there should be expected, not surprising. If telemetry aggregates by platform, note that openwebui traffic splits out of api_server counts from this release onward. (nit)
2. Same line — as integrations multiply, promote the literal to a module-level frozenset (`_RUNS_CLIENT_PLATFORMS = {"openwebui"}`) so adding the next Function is a one-word change instead of another inline comparison. (nit)
3. prompt_builder.py:~1076 — the hint hardcodes integration behavior ("DOES intercept and import MEDIA: tags for any file type") that lives in an external Open WebUI Function, not in this repo. When that Function evolves, this text rots silently. Consider a doc comment pointing at where the Function's contract is maintained. (nit)
4. The type check (400 on non-string) before the allowlist fallback is right — it distinguishes malformed input from merely-unrecognized identity. (positive)

No blocking issues found.
