> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: only the heading is de-bolded; a **bold** fragment inside a data CELL still passes through as `• header: **value**`. That converts fine through the normal MarkdownV2 pass today (the breakage was specifically the wrapper's own __…__ nesting), but if Telegram ever chokes on another nested shape, the per-field sanitizer is the place this class of fix lands next. The seven new tests — especially the prose/fence/plain-pipe/HR negative cases and the exact no-double-bold regression — are exactly what this helper needed.

— Reviewed by Hermes AI reviewer (reviewer-f)
