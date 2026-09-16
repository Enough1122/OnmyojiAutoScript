> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct ownership semantics for scheduled jobs: they are never `delegate_task` children, so inherited lineage (via the asyncio task's copied context when a session had a child active at spawn time) is purely a leak — and the failure it produced (`scrub_kanban_env` marking every terminal subprocess, killing `hermes kanban` at DB init) was an intermittent false alarm that must have been miserable to debug. The token-based reset/restore pair fits the long try/finally shape, the asymmetric env handling is justified in-line (the marker only ever belongs in *copied* child envs, so popping from the live environ is corrective), and the tests prove all three layers: both signals cleared and restored for a real outer child, end-to-end run_job with a lineage probe asserting `subprocess_env is None` passthrough, and the leaked-env-marker variant.
