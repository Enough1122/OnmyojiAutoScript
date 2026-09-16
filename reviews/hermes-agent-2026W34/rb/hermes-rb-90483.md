> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Good containment primitive: the \`external_correspondents\` allowlist drives a single \`_external_agent_isolation_kwargs\` contract (no memory, no context files, no persona), toolsets are denied before any adapter override can widen them, and case-insensitive/string-config handling plus operator-vs-correspondent asymmetry are all pinned by tests. The docs set expectations well (allowlist/pairing still applies first).

The main thing I'd verify before merge:

- **gateway/run.py — enforcement is spread across three call sites, not centralized.** Isolation kwargs are applied at interactive agent creation (~5635), the background-task \`run_sync\` (~22293), and one path blanks history/channel prompts (~27862). If any *other* AIAgent construction or history-assembly pipeline exists in the gateway (profile-wrapped \`_run_agent\` variants, proactive/scheduled turns, plugin-injected events), a correspondent reaching Hermes through it silently gets full memory/persona/context again. Suggest either routing every construction through one factory that consults \`_external_agent_isolation_kwargs\`, or adding an explicit comment/test enumerating covered vs uncovered surfaces so the gap is a documented decision rather than an accident.

Smaller points:

- **website docs cover only email**, but the mechanism reads \`platforms.<any-key>.extra.external_correspondents\` and works wherever \`user_id\` is a stable address (SMS gateways, webhook…). Either generalize the doc section or note it's email-scoped by design.
- **~3502 (`_is_external_correspondent`) re-parses config and rebuilds the lowered set on every call**, and it's called several times per message across helpers; harmless at this size but trivially cacheable per (config object, source) if it ever lands in a hot loop.

No blocking issues found.