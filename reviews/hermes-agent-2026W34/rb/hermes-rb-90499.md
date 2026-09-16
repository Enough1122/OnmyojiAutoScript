> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Strong pair of fixes. The burst detector's thresholds are well-chosen (8 keys within a 32ms window is genuinely machine-speed; the 20ms human-typing test proves ordinary input never latches), and routing sustained streams into the existing 16ms frame-batched commit while keeping refs per-key is exactly the right shape. Replacing the \`self.current\` boolean with an outstanding-echoes list fixes a real class of bugs (A→B→A React coalescing, out-of-order echoes), the cross-read ESC+DEL pairing restores Alt+Backspace without touching the meta-letter resynthesis path, and the test suite covers both units and full rendered-input scenarios including rollback-during-parent-render.

Two small points:

- **ui-tui/src/components/textInput.tsx:~1512 (`advancePrintableBurst`) runs on \`Date.now()\`.** A backward NTP step mid-stream makes \`now - lastAt\` negative, classified as an idle gap (benign reset); a forward jump instantly latches \`rapid\` for what may be ordinary typing until the next idle gap. If this renderer context has \`perf_hooks\` available, a monotonic clock removes both edge cases; otherwise worth a comment acknowledging wall-clock sensitivity.

- **textInput.tsx:~975 — the 64-entry echo cap drops the *oldest* pending echoes.** Under a pathological parent that stops re-rendering entirely while local emissions continue, an evicted echo means a later identical parent value is reclassified from "expected echo" to "external reset," clearing queues and snapping the cursor. Given frame batching bounds emission rate, reaching 64 requires a wedged parent anyway — but since that wedge is precisely the failure mode being hardened, consider whether evict-newest (or treating overflow itself as an external-reset signal) is the safer policy.

No blocking issues found.