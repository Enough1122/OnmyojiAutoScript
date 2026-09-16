> AI code review — automated review for reference; please use your judgment.

Right fix, right size: the truncated display title was lossy for exactly the field clients most need verbatim, `raw_input` restores fidelity without changing the title UX, and the test pins both halves (truncation marker present, full command carried). One nit:

- acp_adapter/tools.py:1124 — nit — only `terminal` got `raw_input`; if the ACP protocol consumers rely on it for structured replay, sibling tool kinds (`edit`, `read_file`) may warrant the same treatment eventually — worth a follow-up thought rather than a change here.

No blocking issues found.

— reviewer-b (automated review)
