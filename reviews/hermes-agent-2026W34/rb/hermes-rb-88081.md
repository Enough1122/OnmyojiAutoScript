> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct root-cause distinction: the voice-linked *text channel* exemption keyed on `_voice_text_channels` ids can't see a message typed directly into a voice/stage channel's own built-in chat — different channel id, and Discord rejects auto-threading there outright (400/50024). Adding the channel-*type* check (`isinstance` against VoiceChannel/StageChannel) alongside the id set fixes both the mention gate and the doomed auto-thread attempt, with the failure mode and Discord error code documented. Tests cover the exact reported shape (bound text channel 456, typing in voice chat 789) asserting no thread spawn plus normal dispatch, and the mock layer gained the two channel types everywhere needed.
