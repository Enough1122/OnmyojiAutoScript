> AI code review — automated review for reference; please use your judgment.

Right fix for #89831 with good coverage of both transport layers (adapter `voice_note` kwarg incl. group routing, and the standalone `_send_signal` HTTP path threading the `is_voice` tuple that was previously ignored). One correctness edge:

- tools/send_message_tool.py:1827 — issue — the flag is batch-level: `if any(path in voice_paths ...)` marks the *entire* RPC `voiceNote: True` even when the batch mixes a voice note with a regular image/document — why it matters — depending on signal-cli semantics the whole batch renders as tap-to-play bubbles (an image shown as a broken voice bubble) or the flag is applied to files that shouldn't be — suggestion — either split voice attachments into their own send RPC, or set the flag only when every attachment in the batch is a voice file.

No blocking issues found.

— reviewer-b (automated review)
