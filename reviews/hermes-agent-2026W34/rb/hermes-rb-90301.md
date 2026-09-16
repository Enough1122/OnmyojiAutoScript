> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: when a choice omits `delta` entirely, the chunk is now silently skipped. A single debug log (\"choice without delta from %s\") would make non-compliant-provider triage possible from logs alone, matching how the finish_reason getattr path is already observable. The regression test itself is exactly right — it cites the finish_reason precedent and asserts the stream still completes with content and stop through the full agent call, not just the helper.

— Reviewed by Hermes AI reviewer (reviewer-f)
