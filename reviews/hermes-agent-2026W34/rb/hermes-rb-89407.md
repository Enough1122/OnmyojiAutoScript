> AI code review — automated review for reference; please use your judgment.

Well-engineered quota-preservation feature: the gateway stamps only genuinely non-final sends via one shared helper, the Weixin adapter's suppression is strictly gated on `is True` (junk-value matrix tested), the stream consumer gains a separate `commentary_metadata` lane so finals keep clean metadata, and — the subtle part most implementations miss — a *suppressed* commentary send never enters `_delivered_commentary_texts`, so it can't accidentally suppress the final reply whose text matches (that exact scenario has its own test). Docs in both locales spell out what stays deliverable. Items:

- gateway/platforms/weixin.py:1922 — nit — suppressing long-running heartbeats means hours of silence on an opted-in adapter; consider having the suppression path bump a counter surfaced in status output (`progress_suppressed: N`) so "is it still alive?" remains answerable without re-enabling progress.

- gateway/run.py:5347 — nit — `_interim_assistant_cb` now wraps every interim send in `_transient_progress_metadata(...)`; the helper allocates a fresh dict per call — fine at this frequency, just noting it's on the streaming hot path.

No blocking issues found.

— reviewer-b (automated review)
