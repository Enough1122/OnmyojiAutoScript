> AI code review — automated review for reference; please use your judgment.

Precise precedence repair with the full decision matrix under test: auto-detected env-seeded routes yield to explicit `model.base_url`, while explicit `*_BASE_URL` env vars (even when equal to the default) and manual account routes keep their authority — and the dotenv-first reader is shared between the guard and the override so they can't disagree. The "env URL equals default is still explicit" case is exactly the subtle one most fixes miss.

— reviewer-b (automated review)

No blocking issues found.
