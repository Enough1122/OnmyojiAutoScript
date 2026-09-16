> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Neat small feature: /find-skill reuses the proven /learn prompt pipeline instead of inventing a new one, registers properly in the command table (args_hint, busy_policy, busy_handler), and degrades with a clear message when no input loop exists.

- **Gateway parity:** commands.py and cli.py are wired, but gateway/slash_commands.py is not - so /find-skill works in the interactive CLI yet is unknown to messaging-platform users whose /skills counterpart exists there. If that asymmetry is intentional (CLI-only for now), a note in the PR description would prevent the inevitable "works on Telegram?" reports; otherwise mirror the handler behind the existing gateway slash dispatch.

- **No tests.** The handler has exactly two behaviors worth pinning: the query text reaches build_learn_prompt's output, and the empty-query fallback string is used when no argument is given. Both are one-line asserts against a stubbed _pending_input queue.

- Nit: the conditional prompt reads slightly oddly because the ternary binds only the concatenation - hoisting the f-string onto its own line would make intent obvious at a glance.

No blocking issues found.