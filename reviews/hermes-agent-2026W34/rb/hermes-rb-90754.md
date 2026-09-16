> AI code review — automated review for reference; please use your judgment.

Review of "feat(tui): add required prompt dispatch hooks". Well-designed gate: pure frozen-decision resolver separate from invocation, required image turns accept ONLY the client-nominated handler id (fail-closed block when absent), optional turns defer generic allows so they can't mask a later image consumer, hook crashes degrade per-mode (allow when optional / block when required), and the respond path persists both messages with a history_version guard against lost updates. Test coverage spans unit, session lifecycle, and a spawned-child run of the real worker. Suggestions:

1. tui_gateway/prompt_dispatch_hooks.py:15 (hardcoded German UI text) — `REQUIRED_HANDLER_UNAVAILABLE_TEXT` is user-facing copy baked in German while the rest of the product ships five locales — route it through the same i18n mechanism the desktop uses, or at minimum make it English-default + translatable; as-is every non-German user hitting the fail-closed gate gets untranslated instructions during exactly the most confusing moment (their protected image was refused).

2. tui_gateway/server.py:10498 (usage attribution) — `_complete_prompt_dispatch_response` reports `_get_usage(agent)` in message.complete even though the agent made NO provider call this turn — clients reading usage will show stale totals attributed to a plugin-authored reply; either zero/omit usage for `prompt_dispatch_response` completions or mark the payload so renderers can skip it.

3. tui_gateway/server.py:10692 (version-miss drops the prompt) — if history_version changed between snapshot and completion, the RuntimeError fails the whole submitted turn and the user's text vanishes; since the decision already validated, one re-snapshot-and-retry (or re-dispatch into the queue) would be friendlier than dropping input on a benign concurrent write.

4. tui_gateway/prompt_dispatch_hooks.py:60 (reserved action) — plugin dicts with `action: "block"` are silently skipped (not in {allow, respond}); that's the right trust boundary, but hooks.md should say "block is host-reserved" so plugin authors don't ship a directive that does nothing.

No blocking issues found — item 1 is the one I'd fix before release since it's user-facing.
