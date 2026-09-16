> AI code review — automated review for reference; please use your judgment.

High-quality example docs: both pipelines explain *why* their shape is necessary (headerless PCM → ffmpeg containerization; SSE transcript → tail/sed/jq; Opus voice notes returning empty transcripts unless normalized to mono 24 kHz WAV), which makes them teaching examples rather than copy-paste blobs. One verification:

- website/docs/user-guide/features/tts.md:622 — issue — `env_passthrough` is newly documented for **STT** command providers with "Same key as on the TTS side" — please confirm the STT provider implementation actually reads that key (the TTS side's support is referenced but not shown) — why it matters — if STT command execution doesn't yet honor `env_passthrough`, this example ships a config whose `$SPEKO_API_KEY` silently expands to empty and every request 401s — suggestion — either point to the STT-side code path that consumes it or add it in this PR alongside the docs.

No blocking issues found — item 1 decides whether the STT example works at all.

— reviewer-b (automated review)
