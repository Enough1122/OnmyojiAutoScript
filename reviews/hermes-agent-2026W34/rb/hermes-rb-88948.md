> AI code review — automated review; please use your judgment.

Important hygiene fix: this test previously invoked `stream_tts_to_speaker` unpatched, so on a machine with a configured TTS provider it would genuinely synthesize speech (network call + speakers) during unit tests. Patching `tools.tts_tool.text_to_speech_tool` closes that while preserving the assertions that matter (`done_evt` set, text displayed), and ````call_count <= 1```` documents the expected at-most-one synthesis without over-constraining buffering behavior.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
