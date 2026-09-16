> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): skip agent-generated audio when auto-TTS already sent". Right dedup for a real double-voice scenario (streaming auto-TTS + agent self-generating audio via execute_code): `skip_audio` is correctly scoped to the already-sent path only, the extension set is broader than the prose (.m4a/.flac/.aac included), and `is_voice` entries are caught too. Suggestions:

1. gateway/run.py:_deliver_media_from_response (silent withholding) — a dropped audio file was EXPLICITLY attached by the agent via a MEDIA: directive, but the user receives no indication anything was withheld (only a server-side info log) — consider appending a one-line notice to the delivered text ("(audio attachment withheld: voice reply already sent)") so users understand why the agent's audio didn't arrive.

2. nit (comment drift) — the docstring names four extensions but `_AUDIO_EXTS` ships seven; keep them in sync or point the docstring at the set as the source of truth.
