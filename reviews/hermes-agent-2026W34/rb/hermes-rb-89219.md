> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct choke-point analysis: patching `hermes_cli.voice`'s binding never covered late-imports of `tools.voice_mode.play_audio_file`, and adding both that function *and* the `_play_int16_via_tempfile` tone path to the autouse guard closes the "bare `pytest tests/gateway` spoke out loud" hole at the one place every player funnels through. The opt-out marker story is handled carefully too — legit-audio tests get `@pytest.mark.real_audio_playback` with per-test explanations of *why* they need it, the macOS beep arm is documented rather than silently broken, and the new `HERMES_TTS_NO_PLAYBACK` kill switch gives headless contexts a process-wide guarantee independent of mocking. Findings below are minor:

1. tools/voice_mode.py:1636 — the kill switch compares strictly against `"1"`, while this codebase's other boolean envs (`HERMES_PHASE1_CAPABILITY_MODE` aside, e.g. buzz/gateway toggles) accept `true/on/yes`. A user setting `HERMES_TTS_NO_PLAYBACK=true` gets silence-free CI anyway only if the conftest guard runs; standalone tool invocations ignore their intent. Normalize with the same accepted-token set used elsewhere.
