> AI code review — automated review for reference; please use your judgment.

Correct alignment of recovery pointers with `session_search`'s actual contract: dropping `session_id` keeps the tool in discovery mode (passing it selected bounded READ and ignored the query), and the explicit `role_filter`/`detail` fixes the subtler half — discovery defaults exclude tool rows, so demoted tool output was unreachable even with a correct query. The integration test proves the exact failure end to end (archived tool row invisible by default, recoverable with the new pointer shape). One nit:

- agent/context_compressor.py:745 — nit — `_lean_recovery_stub`'s `session_id` parameter is now used only as a truthiness gate (the id itself never reaches the output); rename it to something like `has_session: bool` or drop it at the call sites so the signature stops implying the value is embedded.

No blocking issues found.

— reviewer-b (automated review)
