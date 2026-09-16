> AI code review — automated review for reference; please use your judgment.

1. hermes_cli/kanban_db.py:_review_completion_rejection_reason — the accepted approval vocabulary is a closed frozenset (approved/approve/pass/passed…). Why it matters: a worker that reports `"review_result": "approved by 2 of 3 reviewers"` normalizes to something outside the set and is rejected as NONAPPROVAL even though the intent was approval — the safe direction, but a worker-facing trap. Suggestion: publish the accepted values in the kanban_complete tool schema/description (where the error already points for the partial-axis case), so models emit recognized tokens instead of prose.

2. The decompose half fixes a real lost-update: final root ownership now resolves from the DB row inside the write transaction (explicit assignment wins; orchestrator fallback only when unassigned), and both tests drive the mutation through the actual LLM-call window rather than mocking around it.
