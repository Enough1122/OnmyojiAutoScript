> AI code review — automated review; please use your judgment.

Strong engineering on a hot path: 4–5 sequential shells collapse to two, the per-call random hex sentinel makes header/body splitting collision-proof by construction, regular-file short-circuiting means FIFOs/devices are never opened (with a live mkfifo regression test), per-stage `*_rc` statuses in the header disambiguate "not found" vs "read failed" vs "sample failed" (each with its own degradation path back to the legacy single-purpose execs), binary detection now happens before the page exec so binaries cost one shell, and the trailing-newline probe is correctly gated to final pages only. The test suite is exemplary — wire-format parser pins plus live LocalEnvironment runs asserting exact exec counts.

1. `tools/file_operations.py` (`_page_text_file_cmd`) — the page script **requires `mktemp`** and exits 1 when it's absent, where the previous sequential pipeline worked on any environment with sed/wc — why it matters: an exotic minimal Git Bash/busybox deployment regresses from working reads to a bare "Failed to read file:" with no diagnosis — suggestion: fall back to streaming `sed | cut` directly (accepting the phantom-newline probe skip) when `mktemp` is unavailable, or at least emit a stable reason token (e.g. `mktemp_missing=1` in the error) so the failure is diagnosable.

2. `agent-side` (`read_file`, ~1727): ````ReadResult(error=f"Failed to read file: {page_result.stdout}")```` — when the page script aborts early (mktemp guard, unexpected shell failure) stdout is often *empty*, producing "Failed to read file: " with a dangling space and zero context — suggestion: include `stderr`/`exit_code` in the message like other call sites do.

3. Nit (`_probe_regular_file_cmd`): `size=$(wc -c < …)` inside the `[ -f ]` arm inherits the old FIFO-safety comment's intent, but on a race where the file is replaced between `[ -f ]` and redirect, `size_rc` correctly captures it — worth one docstring line noting the TOCTOU window is accepted and surfaced via `size_rc`.

— reviewer-a · automated agent review (Hermes week-review)
