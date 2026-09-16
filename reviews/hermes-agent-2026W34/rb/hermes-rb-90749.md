> AI code review — automated review for reference; please use your judgment.

Right fix with the right safety net: the dead `prompt` parameter is dropped before it can TypeError against the strict SDK signature, `context_bias` resolves mistral-specific → global with per-token cleanup, and the refused-vocabulary retry reopens the file correctly while preserving language. The test set pins all five behaviors including "genuine outage costs no second call". Items:

- tools/transcription_tools.py:2400 — issue — `_is_context_bias_rejection` treats *any* "Status 400" as a vocabulary rejection — why it matters — an unrelated 400 (bad model name, corrupt audio, oversized file) now gets mislabeled "Mistral rejected the transcription vocabulary" and silently retried with the operator's configured bias dropped, so the failure is both misdiagnosed and de-configured — suggestion — require a vocabulary marker in the message (`"context" in message`) alongside the status check, or parse the response body's error field; keep the bare-400 fallback only when nothing else distinguishes it.

- tools/transcription_tools.py:2368 — nit — entries are stripped but otherwise unvalidated; the API rejects commas/whitespace, so a misconfigured multi-word term is guaranteed to burn the first request and the retry on every transcription — consider pre-splitting multi-word entries into tokens or warning once at resolve time so operators fix the config instead of paying the retry each call.

No blocking issues found.

— reviewer-b (automated review)
