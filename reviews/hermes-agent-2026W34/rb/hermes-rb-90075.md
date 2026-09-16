> AI code review — automated review; please use your judgment.

Thoughtfully scoped feature: per-turn visibility settings gain chat-type overrides while **process-global formatter knobs (`tool_preview_length`) are deliberately excluded** from `chat_types` — with the concurrent-state race called out by name and a regression test proving the global cap isn't mutated by a group-scoped value. Alias normalization (`direct/private→dm`, `forum/supergroup/channel/thread→group`), most-specific-first resolution, the Mattermost explicit-opt-in interplay (including the subtle "null override is NOT an opt-in" case), and end-to-end suppression tests across DM/group make this unusually complete, and the docs document both syntax and the concurrency rationale.

No blocking issues found.

Nit: `thinking_progress` is quietly *added* to the chat-type-overrideable set (`CHAT_TYPE_OVERRIDEABLE_KEYS = (...) | {"thinking_progress"}`) but appears nowhere in the yaml example block or the configuration.md applied-settings enumeration — since it's the one key that gained chat-type scoping without existing platform/global default machinery, give it a line in both places so operators know it's available at this scope.

— reviewer-a · automated agent review (Hermes week-review)
