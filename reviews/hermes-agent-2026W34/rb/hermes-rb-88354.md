> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct docs fix: bare `python` fails or resolves to Python 2 on most modern Linux distros (and inside minimal containers), so the skill's command examples would fail verbatim for a fresh user. Switching all seven invocations to `python3` matches PEP 394 reality and the rest of the repo's documented commands.
