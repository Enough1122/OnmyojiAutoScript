> AI code review — automated review for reference; please use your judgment.

Useful docs addition: the TTS/STT distinction was genuinely unclear ("OpenAI TTS" under a tip that also covers voice transcription), the provider table row slots into the existing comparison cleanly, and the YAML example includes the two things users always miss (language hint + gateway restart). Points:

1. website/docs/user-guide/features/tts.md:~455 — please verify `stt.use_gateway` is an actual key the STT config reader honors (vs Portal routing being implicit when provider=openai + Portal OAuth present). If routing is automatic, the snippet teaches a no-op key; if real, one link to the key's definition would let future readers confirm. Docs-only so non-blocking either way.
2. The example hardcodes `gpt-4o-mini-transcribe`; consider noting it's the current recommended model subject to change. (nit)
3. Minor: the intro paragraph still says "OpenAI Audio is available" while the table row says "Good–Best" quality — consistent enough, just noting the tier claim now matches the OpenAI Whisper API row exactly. (nit)

No blocking issues found.
