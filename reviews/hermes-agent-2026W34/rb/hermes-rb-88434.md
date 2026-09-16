> AI code review — automated review for reference; please use your judgment.

Correct minimal diagnosis: `.get("final_response", "")` only defaults when the *key is absent* — cancelled turns set it to `None` explicitly, which sailed past the default and crashed downstream string handling. `or ""` covers both shapes.

1. acp_adapter/server.py:~2005 — worth a quick grep for sibling `.get("final_response", ...)` consumers in this file/adapter that would hit the same None on a cancelled turn; if this was the only one, fine.
2. No regression test pins the cancelled-turn → None → "" path; a one-liner driving run_conversation's cancelled shape through this handler would prevent reintroduction. (nit)

No blocking issues found.
