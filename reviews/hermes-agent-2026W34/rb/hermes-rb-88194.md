> AI code review - automated review for reference; please use your judgment.

Reviewed the diff (SKILL.md, manifest, and the bundled sh/pwsh scripts; the 100KB bulk is the twin 72-command implementations). Documentation quality is exemplary: frontmatter fits the house rules, the MCP-vs-skill split is stated crisply up front ("record-CRUD only vs full admin surface"), and the Pitfalls section reads like it was written from scars - plain `and` vs `~and`, the create-vs-update payload wrapper difference, silently-dropped unknown field names, Enterprise-gated endpoints with the free-plan workaround (read base IDs out of the URL), and the nc-is-netcat naming trap. The manifest honestly scopes the OAuth server to record-level and flags the per-base xc-mcp-token alternative as full control over its base.

- The sh and pwsh scripts duplicate a 72-command surface; as with prior dual-language skills, a "keep in sync with the other" comment at the top of each would prevent silent drift.

- Nit: verify `related_skills: [airtable]` resolves to an existing skill tree entry.