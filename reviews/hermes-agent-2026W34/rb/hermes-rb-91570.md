> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right fix: a 32-char floor was a free injection channel ("ignore previous instructions and ..." fits comfortably under it), and the rewritten tests pin every length from each external tool family, including empty strings and forged opening/closing tags. Docstring updated honestly (no forgeable already-wrapped fast-path). Two things worth confirming:

- **Structured (non-string) results still bypass the boundary.** \`_maybe_wrap_untrusted\` passes dicts through unchanged, so an MCP client that hands back a parsed JSON object rather than a serialized string reaches the model unframed — the new agentmail tests only exercise the adapter's json.dumps output. If upstream guarantees "callers always stringify before dispatch," capture that invariant in the docstring; otherwise consider wrapping dict content as pretty-printed JSON inside the same block.

- **Single choke point:** worth a quick sweep that no adapter layer (agentmail or otherwise) applies its own minimum-length or shape-based skip before results reach this function — the security property should live exactly here.

Nit: tests/agent/test_tool_dispatch_helpers.py:~140 — for content="" the \`f"\\n{content}\\n" in result\` assert reduces to checking "\n\n", which passes trivially; asserting the exact inner span between the header and footer would be tighter.

No blocking issues found.