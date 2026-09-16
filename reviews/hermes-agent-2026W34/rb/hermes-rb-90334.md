> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Precise diagnosis of a nasty stuck-skeleton bug (#90229): the reset broke exactly the invariant every self-heal path was gated on (`state.cwd === cwd`), while changing neither of the load-effect's dependencies — so nothing could ever re-arm, `rootLoading` stayed true, and even the Refresh button was disabled. The fix keys the re-arm on the **cleared** store (`cwd: ''`) rather than any mismatch, which correctly refuses to steal the atom from another live consumer with a different cwd, and the convergence argument (loadRoot writes its cwd before its first await, so the effect goes quiet after one pass) is stated and then proven by the three tests, including the two-consumer no-ping-pong case.

Nit (non-blocking): apps/desktop/src/app/right-sidebar/files/use-project-tree.ts:444 — the effect encodes knowledge of `resetProjectTreeState`'s implementation detail (that a reset leaves `cwd === ''`). If the store ever switches to a generation counter or null-owner representation, this silently stops firing again. A tiny exported predicate from the store module (e.g. `isProjectTreeStoreUnowned(state)`) would keep the reset contract in one place.
