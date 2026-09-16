> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right call for a salvage tool: a legacy row violating the *current* schema (NULL in a now-NOT NULL column) is exactly the kind of thing recovery should quarantine, not die on — one bad optional row no longer aborts the canonical data behind it. Implementation is tidy: `IntegrityError` is caught *before* the fail-loud `BaseException` branch, rolls back cleanly, records the precise reason in `skipped_rowid_ranges`, tracks `destination_rejected_rows`, and doesn't inflate `copied_rows`; the regression test exercises a genuinely rebuilt legacy table end-to-end including report shape and output contents.

Nit (non-blocking): hermes_cli/session_recovery.py:690 — rejection details live only inside the per-table report structure, so a user who runs recovery and gets a healthy-looking exit can silently lose rows versus the source (this is still data non-recovery, just deliberate). Consider surfacing a summary warning ("N rows rejected by destination constraints across K tables — see report") at CLI completion whenever the counter is non-zero, so operators consciously decide whether to hand-patch the dropped rows.
