> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right call: `_repair_ogg_container` running earlier in the flow means an explicit Telegram `.ogg` output can already hold a valid Opus/Ogg payload even when this conversion branch skips itself, so keying `voice_compatible` off the *final* extension instead of "did this branch convert" fixes the false-negative that downgraded working voice notes. The new test pins the repaired-path outcome including the `[[audio_as_voice]]` media tag. One real concern:

1. tools/tts_tool.py:3455 — the extension-based flag trusts that the `.ogg` file is genuinely Opus-in-Ogg, but `_repair_ogg_container` can fail to fix a payload (unsupported input codec) while still returning the path; the result is then advertised as `voice_compatible: true` with `[[audio_as_voice]]` and Telegram renders a broken/unplayable voice bubble. If the repair helper can report success (return None / raise / a bool), gate the flag on that signal; otherwise do a cheap container sniff ("OggS" magic at offset 0) before setting it.
