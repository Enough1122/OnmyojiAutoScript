> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Sensible default flip ahead of Slack's February 2027 Assistant deprecation, handled with care: \`--assistant-view\` survives as an explicitly-labeled compatibility mode (with the deprecation warning printed even in \`slashes_only\` form), \`agent_description\` now honors the user's bot description within Slack's 300-char cap (truncation test included), and \`agent_session_stopped\` joins the subscription list alongside the context events. Tests pin the new default, the legacy opt-in, and the truncation boundary.

Two small points:

- **hermes_cli/slack_cli.py:~240 — conflicting flags resolve silently by elif order.** Passing both \`--agent-view --assistant-view\` yields the assistant manifest with no indication that one flag was ignored. An argparse mutually-exclusive group (or an explicit error) would turn a confusing typo into a clear message; same for combining either with \`--no-assistant\`.

- **Verify the adapter actually consumes \`agent_session_stopped\`.** The comment above the event list explains why \`app_context_changed\` is subscribed, but nothing here says what handles the new stopped event — if no gateway handler exists yet it's harmless dead subscription weight, but if it's prep for cleanup-on-stop logic landing separately, a pointer to that PR/issue in the commit message would help reviewers connect them.

No blocking issues found.