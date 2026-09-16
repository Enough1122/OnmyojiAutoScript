> AI code review — automated review for reference; please use your judgment.

Right fix for a real observability gap: the runtime status file was the only thing monitor surfaces read and nothing cleared it on this path, so a previously-connected platform stayed "connected" forever after its adapter stopped building. Overwriting with `failed`/`adapter_unavailable` plus a human-readable message is correct; the comment explains why nothing else owns the cleanup. One nit:

- gateway/run.py:12380 — nit — if `_update_platform_runtime_status` itself can throw (disk full on the status JSON write), this line would replace one failure path with another inside the startup loop; wrapping it best-effort (`try/except: logger.debug`) matches how the rest of the file treats status writes.

No blocking issues found.

— reviewer-b (automated review)
