> AI code review — automated review for reference; please use your judgment.

Substantial incident response (#91040) with the right instincts throughout: fail-closed supersession in `codex_runtime`, session-lifetime delegation caps that survive across turns, weekly-bucket breaker preferring response headers over the usage API, `/stop` now hard-interrupting the foreground agent *and* fanning out to background delegations, and insights de-duplicating parent/child token rows. Test coverage for the pure helpers is genuinely good. Items:

- agent/conversation_loop.py:2905 — issue — the ~90-line Codex weekly-breaker block lives inline in the API-retry path, and its outer handler is `except Exception: agent._interrupt_requested = True` with *no logging* — why it matters — any bug inside the breaker (bad config object, import failure of interrupt_compat) silently converts into an interrupted turn that looks identical to a legit trip; you'll debug ghosts for weeks — suggestion — extract into a `_check_codex_weekly_breaker(agent, …)` helper returning a decision, and log the offending exception (`logger.warning(..., exc_info=True)`) before failing closed.

- agent/conversation_loop.py:2949 — issue (verification) — after `_try_activate_fallback()` the code re-reads `agent.provider` to refuse Codex→Codex fallbacks; please confirm `_try_activate_fallback` mutates `provider` synchronously before this read — why it matters — if the attribute updates only after the next successful call, the refusal branch never fires and the breaker loops onto another Codex route, defeating its purpose; one unit test with a Codex-only fallback chain would pin it.

- agent/tool_guardrails.py:1060 — issue (verification/coverage) — `_EXPLICIT_CHECKPOINT_RE` and `_REVIEW_DELEGATE_RE` are central to the new checkpoint gating but their definitions/patterns aren't in the visible hunks and have no direct tests here — why it matters — false-positive checkpoints (a user casually writing "ok that's a checkpoint" grants another batch) and missed review-delegate detections both quietly re-open the runaway loop this PR closes — suggestion — show the patterns in the description and add table-driven tests: obvious grant, casual mention, non-English, review-vs-patch classification across phrasings.

- agent/insights.py:44 — issue — the fold drops children only when `parent_total >= children_total`; in exactly the runaway case targeted here (children dwarf the parent) the condition fails and both rows stay, so insights still double-counts the worst offenders — why it matters — the incident was "~2x inflated totals"; this fix removes inflation only when it's small — suggestion — either keep both rows but report a `folded`/`includes_children` annotation so consumers know, or clamp the displayed parent to `max(parent, children)` with a provenance note; today's middle ground silently keeps the bug for large children.

- cli.py:12851 — nit — `_deferred_followups` grows unbounded while a stuck thread stays alive, and parked messages vanish if the process exits before the flush; consider capping (e.g., last 20) and printing a notice on shutdown when the queue is non-empty so users know their text was held, not eaten.

No blocking issues found — items 1 and 2 are the ones I'd want answered before merge since they sit on the breaker's critical path.

— reviewer-b (automated review)
