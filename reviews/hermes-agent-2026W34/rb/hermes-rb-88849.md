> AI code review — automated review for reference; please use your judgment.

Right fix in the right place: `--build-only` returned before the launch-path sandbox repair, so headless update flows that exec the artifact directly (and gate on those exact setuid bits) got an unlaunchable build. Best-effort with the launch path as second chance and a linux-only test pinning the call is exactly enough.

— reviewer-b (automated review)

No blocking issues found.
