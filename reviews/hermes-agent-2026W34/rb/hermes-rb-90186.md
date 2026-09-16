> AI code review — automated review for reference; please use your judgment.

Review of "feat(approval): append-only JSONL audit log of approval decisions". Good audit hygiene: never-raises wrapper (approval stays safety-critical, logging isn't), redaction applied with force=True before anything hits disk, a useful record shape (ts/pattern/outcome/surface/session_key), and clear purpose (feeding the approvals-mining loop). Suggestions:

1. tools/approval.py:3727 (redaction-failure fallback leaks) — when `redact_sensitive_text` raises, the fallback writes `command[:200]` — i.e., the UNREDACTED command prefix, exactly where a secret would live — into the audit file; write a placeholder like `"[redaction unavailable] " + command[:80]` or drop the field entirely for that record.

2. tools/approval.py:3831 (audit coverage) — only `check_dangerous_command` logs; please confirm every approval surface (request_tool_approval, gateway/ACP approval flows, auto-approve paths) funnels through `_log_approval_event` — an audit log that silently misses whole surfaces is worse than none for compliance purposes.

3. nit (concurrency) — multiple gateway/CLI processes append to the same JSONL without coordination; sub-4KB O_APPEND writes are effectively atomic on local filesystems so this works today, but if records grow or network mounts appear, add a lockfile.
