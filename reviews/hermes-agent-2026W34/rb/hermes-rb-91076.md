> AI code review — automated review for reference; please use your judgment.

Clean one-line-class fix with exactly the right tests (managed-only, user-only, neither). One thing to confirm:

- hermes_cli/mcp_startup.py:24 — issue (verification) — the gate now answers on `apply_managed_overlay(raw_config)`, but the actual MCP *connect* path builds its server set through its own config assembly; if the overlay merges `mcp_servers` shallowly (managed replacing user's map) while connect-time merges deeply (union), the gate and reality can disagree in both directions — a user+managed split where the gate says True but connect sees none, or vice versa — suggestion — assert once that gate-side and connect-side produce identical server sets for a config carrying `mcp_servers` in *both* scopes; it pins the merge contract instead of trusting "shared helper" forever.

No blocking issues found.

— reviewer-b (automated review)
