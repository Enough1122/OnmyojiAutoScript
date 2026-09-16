> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right classification fix: web_search / web_extract put a nullable error field *per result item*, so both the earlier top-level "error" key check and the downstream substring heuristic misread every successful call as a failure. Judging by results[] items and returning an explicit (False, "") stops the fall-through cleanly, and partial failures still surface the offending item message.

Two points:

- **No tests accompany the new branches.** Both directions deserve pinning: a successful multi-result payload whose items carry a null per-item error must classify as success (the regression being fixed), and one item with a non-null error must classify as failed with the trimmed message. Without them, reordering the surrounding checks silently reintroduces the false positive.

- **agent/display.py ~1373 — confirm the early return is actually reached for real payloads.** The branch just above fires on a top-level "error" key even when its value is null; if real web_extract success envelopes include such a key, that generic check triggers before the scoped one runs. If so, exempt these two tools from the generic branch as well (or tighten it to truthy-error-only).

Nit: the tool-name set is inline; this file already uses module-level tool-set constants elsewhere — lifting it up keeps failure-classification exceptions discoverable in one place.

No blocking issues found.