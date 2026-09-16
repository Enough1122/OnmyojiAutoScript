> AI code review — automated review for reference; please use your judgment.

Textbook fix: the diagnosis (SDK wraps `CommandTokenError` as a generic connection error, so only the exception chain carries the truth), the placement (4b ahead of the transport heuristics that were mis-classifying it), the cycle-safe chain walk, and five tests including the two that matter most — a real connection error must keep retrying, and a self-referential `__cause__` must terminate. Nothing to add beyond one nit:

- agent/error_classifier.py:712 — nit (coverage) — no case for a *two-level* chain (`APIConnectionError` → wrapper → `CommandTokenError`) where the token error sits below an intermediate exception; the walk handles it, but pinning it protects against someone later switching to a single-level `__cause__` peek for micro-optimization.

No blocking issues found.

— reviewer-b (automated review)
