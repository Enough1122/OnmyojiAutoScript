> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Thoughtfully scoped anti-evasion work: the anchor-vs-last hash split means alternating \\"full payload ↔ unchanged envelope\\" sequences can't reset the streak (each pattern is tested, including the look-alike envelope missing one field being rejected), the \`merge\` normalization is deliberately confined to \`todo\` with \`todos\` present (order-significance and other-tool scoping both pinned by tests), and the unchanged-contract requires three exact fields from an explicit narrow allowlist whose docstring explains why it must stay narrow. The stub-interplay test (jittered args sharing the normalized signature still stub against the *first* call's id) shows the composition was thought through.

Two small notes:

- **agent/tool_guardrails.py:~841 — the contract is trust-the-emitter.** If a future \`read_file\`/\`skill_view\` regression ever stamps \\"status: unchanged\\" while content actually differs, the stall guard will now stay silent through what used to be caught as changed results. Worth a comment at the emitters stating they form a contract with \`tool_guardrails\`, or a debug-level counter when an unchanged envelope follows a *different-length* anchor payload — cheap signal that the emitter's dedup logic itself is stalled.

- **~309 — the \\"todo\\\" special case hardcodes the tool name as a bare string** inside the otherwise-generic signature helper; lifting it next to \`STALL_GUARD_UNCHANGED_RESULT_TOOLS\` as e.g. \`STALL_GUARD_ARG_NORMALIZERS = {\"todo\": ...}\` keeps both jitter policies discoverable in one place.

No blocking issues found.