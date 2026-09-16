> AI code review — automated review for reference; please use your judgment.

Clean authority model with the right enforcement depth: the model-facing schema stops advertising `provider`, the registered handler refuses to forward it even when leaked args contain one, the inner helper ignores disagreeing values, and a matching per-call value stays a silent no-op — each layer individually tested (schema / tool / handler / helper), which is exactly how a config-authority migration should be pinned. Points:

1. Behavior change worth a changelog line: agents can no longer choose a TTS vendor per call ("say this one in an xAI voice"). The #90109 rationale (leaked platform hints rerouting speech) justifies it, but existing prompts/skills that passed `provider=` will now get warnings on every use until updated — worth telling skill authors explicitly.
2. tools/tts_tool.py:~3176 — when `tts_config` is effectively empty, `configured_provider` resolves to whatever `_get_provider` defaults to (possibly ""); a per-call "xai" then warns about disagreeing with "" and lands on default resolution — the warning text would read oddly ("`tts.provider` is ''"). Consider suppressing the warning when no TTS config exists at all, since there's nothing to disagree *with*. (nit)
3. The ignored-override WARNING fires per call; a stale session whose cached tool schema still advertises `provider` could emit it repeatedly within one conversation. If log volume matters, downgrade repeats to once-per-session like other once-warn patterns in this codebase. (nit)
4. Docstring for the retained param accurately describes the new contract — good internal-caller hygiene. (positive)

No blocking issues found.
