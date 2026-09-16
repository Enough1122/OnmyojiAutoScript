> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct completion of the SecretRef half-support: process environment still takes precedence, the `~/.hermes/.env` lookup fills the startup-order gap (the exact case where a user's credentials live in .env but nothing exported them before config expansion ran), the unresolved-reference warning now fires only when *both* sources miss so legit dotenv-backed configs stop logging noise, and the docstrings were updated to match. The test pins both the resolved value and the absence of the spurious warning, with a nicely explained monkeypatch targeting `load_config.__globals__` to survive module reloads.
