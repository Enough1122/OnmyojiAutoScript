> AI code review — automated review for reference; please use your judgment.

Correct mirror-image guard: the server-flagged fallback existed to make backend pins unreachable-proof, but it read a cached `pinned: true` that an unconfirmed local unpin hadn't rewritten yet; excluding pending unpins (by lineage root *and* session id) closes #89700 without weakening the cold-cache case. The docstrings on both sides explain the stale-flag mechanics precisely.

- apps/desktop/src/store/session-pin-sync.ts:52 — issue (verification) — the suppression lasts as long as the unconfirmed entry reads `false`; please confirm a *failed* PATCH (network error) eventually clears or ages out the entry so a genuinely pinned session isn't hidden from Pinned indefinitely after one unlucky offline unpin — why it matters — this is the inverse bug of #89700 and shares its "never sticks" symptom from the user's point of view.

No blocking issues found.

— reviewer-b (automated review)
