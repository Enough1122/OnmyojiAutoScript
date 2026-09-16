> AI code review — automated review for reference; please use your judgment.

Clean deprecation cleanup: the three retired MiMo V2 entries leave the context-length table, and the vision-capable attribution moves to `mimo-v2.5` with a corrected rationale.

1. Behavior note for release notes: users whose config.yaml still pins `mimo-v2-pro`/`v2-omni`/`v2-flash` lose exact context-length lookup (falls back to the conservative default with a one-time warning) and will get provider-side errors at call time. A changelog line telling them to switch to `mimo-v2.5` saves those support rounds.
2. The new vision claim ("mimo-v2.5 is vision-capable, native omni-modal") is load-bearing for image routing — worth verifying against xAI/Xiaomi's current model card before merge, since the previous justification lived on a now-deleted model. (nit)

No blocking issues found.
