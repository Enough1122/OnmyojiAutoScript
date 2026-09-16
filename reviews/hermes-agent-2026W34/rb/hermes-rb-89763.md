> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean extension with the right three-state semantics: `None` preserves the historical defaults, a list overrides them, and an explicit empty list deliberately disables default skills (`final_verifier_skills or None`) — that distinction is easy to get wrong and here it's correct. Custom bodies still receive the swarm `context_suffix`, the four overrides are independent per role (pinned by the verifier-only test), and the seven-test matrix including backward compatibility covers every branch.
