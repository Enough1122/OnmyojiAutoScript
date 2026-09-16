> AI code review — automated review for reference; please use your judgment.

Review of "fix(plugins): fail closed on non-interactive tool-override consent". Correct closure of an indistinguishable deadlock: redirected stdout swallowed the prompt while stdin waited forever, and the docstring had promised deny-on-non-interactive without implementing it. Checking BOTH stdin and stdout isatty (catching the PowerShell wrapper case where stdin is a tty but the prompt was invisible), persisting an explicit deny with a remediation command, and leaving explicit --allow-tool-override/--no-tool-override flags as the bypass are all right, with tests covering each stdio shape. Two nits:

1. hermes_cli/plugins_cmd.py:1673 — the "denied (fail closed)" explanation is printed via `console.print` to the very redirected stdout that motivated the guard, so the operator never sees it there either; mirror the reason through `logger.warning` (or stderr) so CI logs and wrapper captures record WHY the grant didn't happen.

2. nit — persisting `allow_tool_override: false` means one CI run permanently records an explicit deny; combined with the already-granted shortcut, a later interactive enable will skip the prompt unless the operator passes the flag. That's defensible idempotency, but say so in the hint text ("this also records a persistent deny") so the behavior isn't surprising.
