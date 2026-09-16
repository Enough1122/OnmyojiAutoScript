> AI code review — automated review for reference; please use your judgment.

The desktop rescan fix itself is small and sensible, but two structural things need attention first:

- agent/model_metadata.py:1183 (bundled change) — issue — this PR titled "reload known disk plugin paths" silently carries an *unrelated* backend pricing change (per-1m/per-1k unit conversion in `_extract_pricing`) — why it matters — reviewers and bisection now can't treat the two independently; if the pricing math regresses cost reporting you'll be reverting a desktop plugin fix to get there — suggestion — split the model_metadata hunk into its own PR (or add a paragraph to the description explaining why it rides along).

- apps/desktop/src/contrib/runtime-loader.ts:392 — issue — for a *known* path the rescan now unconditionally calls `desktop.watchPreviewFile(file)` again and overwrites `record.watchId`, never releasing the previous watch — why it matters — every manual "Reload desktop plugins" leaks one preview watcher per plugin; on a long-running desktop session these accumulate (callbacks firing N times, memory growth) — suggestion — skip the re-watch when `record.watchId` is already set, or explicitly unwatch the old id before storing the new one.

- agent/model_metadata.py:1190 — issue — `"request"` is included in the token-unit conversion loop alongside prompt/completion/cache keys — why it matters — if `request` is a flat per-request fee (as litellm-style payloads often ship), dividing it by 1M/1k turns dollars-per-request into a nonsense number instead of converting units — suggestion — confirm its semantics; most likely it belongs outside the conversion (or needs its own unit field).

- agent/model_metadata.py:1188 — issue — conversion uses `str(float(pricing[key]) / N)`: (a) a malformed/non-numeric value raises `ValueError` out of pricing extraction for the whole model, and (b) `str(float)` yields exponent forms (`1.5e-07`) and binary-float artifacts where the rest of the codebase prices via `Decimal` — why it matters — one bad provider payload breaks metadata for that model, and downstream Decimal parsing of e-notation is inconsistent — suggestion — wrap per-key conversion in try/except (skip key on failure, log) and format via `Decimal(value) / N` with `normalize()`.

- tests — issue (coverage) — neither new behavior has a test: no rescan-refresh case for #91503 (existing record → `loadDiskPlugin` called again, single watcher retained) and no unit-conversion cases (`unit` absent = untouched, `per_1m_tokens`, `per_1k_tokens`, malformed value) — why it matters — both are exactly the kind of silent regressions that survive CI — suggestion — add one test file per concern.

No blocking issues found on the desktop logic itself pending the watcher-leak answer, but please address items 1 and 3 before merge.

— reviewer-b (automated review)
