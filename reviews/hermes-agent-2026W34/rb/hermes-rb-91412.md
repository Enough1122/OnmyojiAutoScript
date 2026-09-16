> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Important guard, correctly built: resolving both sides (`.resolve()`) catches symlinked homes, `is_relative_to` covers both the exact-home and any-parent cases, the check runs *before* any `docker run` (the test asserts no container is ever created), and the retry_hint tells the user precisely which knob to move. Findings:

1. tools/environments/docker.py:917 — the protection only covers the *auto* cwd mount; an explicit `docker_volumes` entry like `["/home/user:/host-home"]` (or literally mounting `~`) reaches the same corruption — a writable container view of the live state.db — and sails straight past this check. Ironically the new retry_hint steers users toward exactly that escape hatch ("or disable ...docker_mount_cwd_to_workspace"), after which nothing stops them adding the home as a manual volume. Suggestion: apply the same containment test to the host path of each configured volume (refuse, or at minimum log a loud warning) so the invariant "containers never see HERMES_HOME writable" holds regardless of which mounting knob carried it.

2. tools/environments/docker.py:931 — the guard fires before `_ensure_docker_available()`, so on a host with no Docker and an unsafe cwd the operator first learns about the mount policy rather than the missing binary. Harmless ordering quirk, but if deliberate, a comment would save the next reader a double-take; otherwise swap the two for a more actionable first error.

No blocking issues found.
