> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Useful docs addition: the allowlist semantics of an explicit platform_toolsets, the mcp-<server> naming convention (toolset vs tool-call prefix), and the genuinely sneaky bit - hermes tools --summary merging base and per-profile config so a profile can display as enabled while its sessions lack the tools. Symptom-then-fix structure is exactly right for a troubleshooting reference.

Nit: the same caveat would help readers in the main website config docs where platform_toolsets is introduced (this lives only inside the hermes-agent skill's references); one cross-link sentence there pointing here would cover users who never open the skill file.