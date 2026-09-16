> AI code review — automated review for reference; please use your judgment.

Clever and correct: the update child restarting its parent dashboard loses every in-memory registry, so recovering success from the durable `update.log` completion marker (strictly full-line, 32-hex, and required to postdate the latest *start* marker so a stale success can't mask a newer failure) is the right mechanism. The synthetic `exit_code = 0` + appended marker keeps the dashboard UI honest across the restart, and the end-to-end test drives the real endpoint against tmp logs. One nit:

- hermes_cli/web_server.py:5407 — nit — recovery fires whenever no live process/result exists, including a first-ever status poll before any update ran on a machine where `update.log` exists from months ago; harmless (the dashboard shows a completed historical run), but worth one comment noting the marker is trusted as written only by the updater itself.

No blocking issues found.

— reviewer-b (automated review)
