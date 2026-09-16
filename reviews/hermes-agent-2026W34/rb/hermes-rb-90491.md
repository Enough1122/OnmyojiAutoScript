> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Clean opt-in: default behavior is byte-identical (both paths tested), the skip mode preserves \`tool_name\`/\`tool_input\`/\`tool_status\` so memory extraction keeps the *shape* of activity while shedding multi-KB result text, and the module docstring documents the new variable alongside its siblings.

Nits: the PR carries an unrelated \`contributors/emails/Backroads4Me@...\` file that belongs to a CLA/contribution-bot commit rather than this change — worth splitting out or noting so history stays attributable; and the modified \`tool_output\` ternary now runs well past typical line length — hoisting \`skip = _skip_tool_outputs()\` above the loop would read better and avoid re-evaluating the env flag per part.

No blocking issues found.