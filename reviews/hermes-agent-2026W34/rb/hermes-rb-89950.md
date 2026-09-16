> AI code review — automated review for reference; please use your judgment.

Excellent design doc: it names the shaping constraint up front ("profile A's turns must never observe profile B's state"), explains *mechanism* rather than just policy (contextvars over os.environ, why a plain module global arms fail-closed, the empty-deployment-secret precedence rule), includes an isolation matrix separating per-profile from process-global, and closes with explicit non-goals ("a profile is a configuration, not a person"). Landing this referenced rationale alongside Workstream A is exactly how secret-scoping changes should be reviewed later. Nothing to flag.

— reviewer-b (automated review)

No blocking issues found.
