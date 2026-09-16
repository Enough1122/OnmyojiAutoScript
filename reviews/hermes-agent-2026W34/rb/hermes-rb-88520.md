> AI code review — automated review for reference; please use your judgment.

Review of "feat(cron): out-of-band paging allowlist for chat deliveries". Well-designed kill switch for notification floods: the control lives OUTSIDE job records (hand-edits and misconfiguration can't page), is checked at SEND time, re-reads both config and allowlist on every check so edits apply without restart, fails CLOSED when the control file is unreadable, never touches non-chat transports, sanitizes withheld-payload paths including the dot-only id edge, and audits every suppression to a durable log plus saved payload. Default-disabled and tested against its stated contracts. Two nits:

1. cron/delivery_gate.py:suppress_and_audit — it RE-RUNS `delivery_gate_check` instead of accepting the caller's reason; a config flip between the caller's check and this one records an audit line whose reason contradicts the actual suppression decision — pass the already-computed (allowed, reason) through.

2. cron/delivery_gate.py:CHAT_PLATFORMS (nit, maintenance) — the hardcoded set means a newly added chat platform is silently NEVER gated (fail-open for the unlisted); consider sourcing it from the adapter registry or at least logging when an unknown-but-chat-shaped platform appears.

3. nit — `delivery-gate.log` grows unbounded; the output payloads have retention conventions elsewhere, so a matching rotate/cap for the audit log would keep parity.
