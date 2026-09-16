> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct routing-hygiene fix: the recipient's own `@` token (name, handle, and friendly-name forms) is stripped before `prompt.submit` so remote bots don't treat routing syntax as message content, cleaning is per-target during fan-out (each bot only loses *its* token), and the `|| text` fallback prevents an all-tokens message from being delivered empty. The test pins the reported shape including the trailing colon. Findings:

1. apps/desktop/src/plugins/hermes-bots/plugin.js:4127 — the final `cleaned.replace(/\s+/g, ' ').trim()` collapses **all** whitespace in the delivered payload, not just the seams left by token removal. A user who @mentions a remote bot with a multi-line body — pasted code, logs, YAML — has every newline flattened into spaces before the remote agent ever sees it, silently corrupting exactly the payloads people route across machines. Replace with the captured prefix (`$1`) and only normalize spaces adjacent to the removal spans, leaving the rest of the text byte-identical.

2. apps/desktop/src/plugins/hermes-bots/plugin.js:4120 — the pattern relies on a JS word boundary after the form (`@<form>\\b`), which fails when a mention form ends in a non-ASCII word character: for a bot named or friendly-named in CJK/emoji, `@机器人:` never matches (no \b transition after a non-word char) and those users keep seeing their own routing token echoed back. Suggest an explicit lookahead instead — e.g. `(?![@\\w])` or `(?=[\\s.,:!?)\\-]|$)` — which also lets you drop the bolted-on `[:,-]?`.
