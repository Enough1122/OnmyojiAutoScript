> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Straightforward and correct post-cutover endpoint update, applied consistently to both the desktop catalog (mcp-directory.ts) and the optional-MCP manifest; the manifest's existing \`transport.type: http\` now actually matches the streamable-HTTP authv2 endpoint, where the previous sse URL was already mismatched with that declared type.

Nit: nothing keeps the two files in sync mechanically — a tiny test asserting the atlassian entry's URL appears identically in both MCP_DIRECTORY and optional-mcps/atlassian/manifest.yaml would prevent the next cutover from updating one and not the other. A repo-wide grep for lingering \`mcp.atlassian.com/v1/sse\` references (docs, comments) is also worth 30 seconds.

No blocking issues found.