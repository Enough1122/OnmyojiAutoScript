> AI code review — automated review for reference; please use your judgment.

Right call switching to the portal-overlay pattern: the sidebar's `relative z-2` container trapping/clipping an in-place Select is exactly the failure the ModelPickerDialog already solved, and reusing that shape keeps the two pickers consistent. Esc-to-close, backdrop-click, `role="dialog"` + `aria-modal` + labelledby are all present. Points:

1. apps/desktop/../ReasoningPickerDialog.tsx — accessibility gap: focus isn't moved into the dialog on open and Tab is not trapped, so keyboard users land back in sidebar content behind the overlay while it visually covers them. On mount, focus the first ListItem (or the close button) and restore focus to the trigger on close; a minimal Tab-cycle trap would complete it.
2. The header shows `current: {currentEffort}` as the raw value ("xhigh") rather than its label from EFFORT_OPTIONS — small polish to display the same friendly text the list uses. (nit)
3. Selecting an option calls `onSelect` then `onClose()` immediately — if `onSelect`'s save later fails (the picker's `saving` state lives in the parent), the dialog is already gone with only whatever error surfacing the parent does. Consider closing after the promise resolves, or accepting the tradeoff explicitly. (nit)
4. The docstring explaining *why* the portal exists (z-trap specifics) is exactly right — future refactor insurance. (positive)

No blocking issues found.
