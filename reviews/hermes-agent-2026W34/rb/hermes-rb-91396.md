> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right fix at the right layer: summaries replacing conversation turns must stay in the turn language or nuance/dialect is lost downstream, and an explicit never-translate directive with a sensible mixed-language rule ("dominant") is exactly what moves summarizer behavior in practice. Applied consistently to both the sync and async generators.

Nit (non-blocking): trajectory_compressor.py:618 / trajectory_compressor.py:689 — the directive is now a duplicated literal in two f-string prompts; when someone later tunes the wording they will inevitably edit one copy and not the other (this PR itself had to paste it twice). Hoist it into a module constant (e.g. `_LANGUAGE_PRESERVATION_DIRECTIVE`) interpolated into both templates, and ideally add a two-line test asserting both generated prompts contain it.
