> AI code review — automated review; please use your judgment.

Reasonable noise-reduction: scoping workspace audits to runtime dependencies (`--omit=dev --omit=optional`) matches what doctor actually gates on, and replacing the old "build-tool advisory; clears via lockfile bump" dismissal with actionable runtime-advisory output (plus an explanatory info line about what's omitted) is a genuine improvement. The helper is extracted and unit-tested for both call shapes.

1. Nit (`hermes_cli/doctor.py` `_npm_audit_omit_args` / fix-hint): for the workspace branch, `fix_cmd` now holds a **read-only** `npm audit --workspace …` invocation (deliberately not `audit fix`, per the arborist-crash history captured in the old comment) — but it's rendered to users through the "fix" wording path, which reads like a repair command — suggestion: either rename/re-word (`"verify with: …"`) or keep a comment at the render site explaining why no auto-fix is offered.

2. Nit: the omit policy is inconsistent across branches — workspace audits omit dev+optional, while `--workspaces=false` and the default branch omit only `optional`; if that asymmetry is intentional (root = runtime package), one clarifying comment would prevent a future "harmonize this" PR from changing behavior accidentally.

— reviewer-a · automated agent review (Hermes week-review)
