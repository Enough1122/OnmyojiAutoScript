> AI code review — automated review for reference; please use your judgment.

1. ui-tui/src/components/modelPicker.tsx:384 — inside the auth-handoff chain, a failure of the post-success loadOptions(true) refresh lands in the same .catch that reports wizard failures, so a transient RPC hiccup displays as 'error: <refresh failure>' right where the user expects auth feedback. Why it matters: the user just completed OAuth successfully; telling them authentication errored sends them back into the wizard unnecessarily. Suggestion: separate the steps (auth errors -> authError; refresh errors -> setErr) or prefix the latter as 'refresh failed'.

2. ui-tui/src/components/modelPicker.tsx:205 — useInput is frozen during authRunning, but useOverlayKeys({ disabled: listStage, ... }) is not, so Escape/back remains live while the child wizard owns the terminal. If Ink suspension swallows keys this is dead code; if it doesn't (or timing races), the overlay can unmount mid-handoff and orphan the await chain's setState calls onto an unmounted component. Suggestion: gate overlay keys on authRunning too.

3. ui-tui/src/lib/modelAuthHandoff.ts — nice seam: launcher/suspend injection makes the terminal-ownership dance testable without Ink, and both tests pin the exact suspend->launch->resume ordering plus failure passthrough. The picker-level flow itself has no coverage (no Ink harness in this suite) — even one component test asserting inputs are ignored while authRunning would protect the trickiest invariant here.

The loadOptions refactor to async/await with .finally(setLoading) also removes the duplicated cleanup from the old promise chain — cleaner than what it replaces.
