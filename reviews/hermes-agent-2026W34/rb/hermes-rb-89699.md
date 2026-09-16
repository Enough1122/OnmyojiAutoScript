> AI code review — automated review for reference; please use your judgment.

Exemplary durable-policy design: fail-closed parsing of typed policy events, single-winner linearization between reservations and constraints (proven by a barrier race test asserting exactly one winner), crash-stuck reservations that wedge *closed* until a bounded, reason-required, audit-provenanced operator recovery, cursor-bound policy repairs that never rewrite history (with the immutability itself asserted), delegated-child spoof rejection at the CLI layer, and refusal-audit idempotency. Every subtle branch — including "a malformed recovery event is itself fail-closed" and "fresh valid constraint after repair still blocks before LLM" — has a test. Items:

- hermes_cli/kanban.py:3205 — nit — the trailing `raise ValueError(f"unknown constraint action {action!r}")` in `_cmd_constraint` is unreachable (argparse `required=True` constrains the subcommand); harmless defensive code, but a comment marking it as such would stop a reader hunting for the fourth path.

- docs — nit (follow-up) — this adds a genuinely new operational surface (`constraint set/supersede/recover/repair-policy`, staleness bounds, delegated-child restrictions); a short runbook section in the kanban docs ("when a decomposer crashes mid-run") would make the recovery path discoverable at 2am instead of requiring a source dive.

No blocking issues found.

— reviewer-b (automated review)
