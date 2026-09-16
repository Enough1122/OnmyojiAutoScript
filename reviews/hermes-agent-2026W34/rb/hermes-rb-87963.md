> AI code review — automated review for reference; please use your judgment.

Review of "fix: preserve intent and bind task-scoped worker approvals" (sampled: compressor summary-prefix generations, synthetic-turn registration, prompt-builder continuity guidance, approval-relay structure; full diff is 114KB across 18 files with 31 tests). The human-authored vs runtime-generated user-role distinction in the compaction handoff closes a real prompt-injection/intent-drift surface (runtime scaffolding occupying the user slot could otherwise read as the active task), and the byte-pinned `_HISTORICAL_SUMMARY_PREFIXES` tuple approach keeps old persisted summaries resumable while new builds get the sharper contract. The verification-stop continuation prefix is correctly registered as a synthetic user turn so provenance classification sees it. Suggestions:

1. agent/context_compressor.py:_HISTORICAL_SUMMARY_PREFIXES (scaling pattern) — every wording tweak now appends another ~30-line verbatim generation, and this diff already doubles the tuple; consider moving to a compact `summary_generation: N` marker embedded at write time (with the prose kept only for N=1..N legacy matching) before the tuple grows again.

2. hermes_cli/kanban_approval.py (binding scope) — the task-scoped worker approval binding should be tested for the cross-task case (an approval captured for task A replayed against task B must be rejected) — if that case exists among the relay tests, ignore; sampled scope did not confirm it.

3. nit — CONVERSATION_CONTINUITY_GUIDANCE asks for checkpoints "before the first tool call"; for very short tasks that could add noise — the guidance already says concise, but a conditional (only when multi-step is likely) would be even better.
