> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

This attacks the whole leak class rather than one symptom, in the right order: a deterministic pre-flight gate (code-fence-aware, letter-after-`<` so `x < y`/`->` stay clean) hard-fails markdown-claimed HTML into a durable dead-letter record instead of sending; `payload_type` is plumbed end-to-end as an explicit contract so HTML senders declare themselves; the Telegram side honors the declaration by bypassing MarkdownV2 entirely; and the never-drop plain-text fallback now strips tags when a *declared* format is rejected instead of dropping the message. WARN-only template assertions can't crash delivery. Validator tests cover fences, inline code, arrows, comparisons, and post-fence leaks. Findings:

1. cron/scheduler.py:2590 — `deadletter.jsonl` is append-only with no rotation/pruning, and each record embeds the **full delivery content**, which for cron reports can be sensitive (metrics, private data). An unlucky job that persistently produces leaks grows this file forever inside `~/.hermes`. Add a size/count cap (drop-oldest) or at least a startup warning above a threshold, and consider recording a truncated content preview plus a hash instead of the whole body — the operator's goal is diagnosis, not a second copy of everything that almost leaked.

2. cron/scheduler.py:_extract_payload_type — invalid values are silently coerced to `text/markdown`, so a job author who writes `payload_type: text/md` gets markdown handling plus HTML-leak dead-lettering with zero signal about their typo (and possibly surprise dead-letters). Log a one-time warning naming the job and the rejected value; coercion stays the safe default.

3. Docs gap (behavioral surprise): any literal angle-bracket token in a report — `<model>`, `<your-api-key>`, `<host>` placeholders — now dead-letters the entire delivery under the default payload type. The validator is doing what it was asked to, but SKILL/docs for cron authors should say explicitly: wrap literal angle tokens in backticks (inline code is exempt) or declare `text/html`.
