> AI code review — automated review for reference; please use your judgment.

Review of "fix(approval): identify pending approval requests". Small, sensible change: `submit_pending` now stores a copy with a guaranteed `approval_id` (uuid4 hex, upstream-supplied ids respected via setdefault). The copy also fixes a subtle aliasing hazard — callers previously had their dict stored by reference, so post-submit mutations would silently rewrite pending state. Suggestions:

1. tools/approval.py:2715 (verify import) — the hunk adds a `uuid.uuid4().hex` call without showing the import; if `uuid` isn't already imported in this module the first submit raises NameError at runtime (the new test would catch it in CI, but confirm locally that the suite actually ran this file).

2. tests/tools/test_pending_approval_identity.py:9 (pin the isolation win) — the tests cover id generation and upstream-id passthrough, but not the copy semantics that motivated `entry = dict(approval)`; one assertion that mutating the caller's dict after submit does NOT change `_pending` would lock the improvement against a future "simplification" back to storing the reference.

3. tools/approval.py:2712 (shallow-copy caveat) — nested values (lists/dicts inside the approval payload) are still shared with the caller; harmless for current flat payloads, but a one-line docstring note ("shallow copy; treat payload values as read-only") prevents surprises if payloads grow structure.

4. tools/approval.py:2713 (identity contract) — nothing yet consumes `approval_id` in this diff; consider documenting who generates vs. consumes the id (and whether it must be unique across sessions) so downstream adopters don't have to reverse-engineer the invariant from this test.

No blocking issues found.
