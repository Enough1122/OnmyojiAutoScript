> AI code review — automated review for reference; please use your judgment.

Review of "feat(desktop): double-click a composer reference chip to edit it in place". Well-factored feature: the dialog engine cleanly separates attach mode from chip-edit mode, `applyChipEdit` returning false when the chip vanished mid-edit keeps the dialog open with the typed value preserved (tested), a no-stack guard prevents double-dialogs, and undo is banked before rewriting an atomic contenteditable=false chip — the only way to correct one mid-draft, as the docstring explains. Tests cover success, vanished-chip recovery, and stacking. Suggestions:

1. use-composer-url-dialog.ts submitUrl (undo ordering) — `recordChipEditUndo()` fires BEFORE `applyChipEdit`, so a FAILED edit (chip already gone) still banks an undo entry for a change that never happened, polluting the undo stack; either move the banking after a successful apply or pop the entry when applyChipEdit returns false.

2. nit — `beginChipEdit` silently ignores the second double-click while a dialog is open; a haptic or brief flash on the existing dialog would tell the user why nothing happened.
