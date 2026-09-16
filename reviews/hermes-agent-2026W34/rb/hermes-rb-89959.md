> AI code review — automated review for reference; please use your judgment.

Right hardening in the right place: `get_profile_dir` was joining request-derived text into the profiles root with only lowercase/strip normalization, and `profile_exists("..")` could confirm an out-of-tree directory. Failing closed with a ValueError, validating *before* any filesystem touch in `profile_exists`, and replacing the join-with-iterdir-compare (killing the injection shape rather than patching it) are all correct — with tests covering the traversal matrix both ways. Items:

- hermes_cli/profiles.py:399 — issue (verification) — `profile_exists` changed behavior for malformed names: previously a clean `False`, now a raised `ValueError` — why it matters — any caller that probes user/config-supplied names as a boolean check ("if profile_exists(x):") will start crashing on weird-but-harmless input — suggestion — grep all `profile_exists(` call sites and confirm each either pre-validates or handles ValueError; add one such caller-level test if a gateway/CLI path takes raw input.

- hermes_cli/profiles.py:404 — nit — `entry.name == canon` is exact-match, but on case-insensitive filesystems a legacy on-disk directory with non-lowercase spelling would make an otherwise-valid profile report missing after this change; consider falling back to a casefold comparison if such legacy dirs can exist.

No blocking issues found — item 1 is a call-site audit.

— reviewer-b (automated review)
