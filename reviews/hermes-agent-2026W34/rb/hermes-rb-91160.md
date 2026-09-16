> AI code review — automated review for reference; please use your judgment.

Right fix for a genuinely broken control: committing on `onBlur` from a local draft means the trailing comma survives keystrokes (`"C:/a,"` no longer collapses to `["C:/a"]` and erases itself mid-typing), the sync effect correctly refreshes the draft from external changes only while unfocused, and extracting `parseListFieldDraft` makes the parsing rules directly testable — all three cases in the new test file pin real behavior including the empty-segment drop.

1. `apps/desktop/src/app/settings/config-field.tsx:~245–252` — commitment happens *only* on blur; any save path that doesn't move focus first (a global ⌘S-style shortcut, an auto-save timer, or future "apply on Enter" wiring) would silently discard the in-progress draft since `onChange` never fired — why it matters: the old control was aggressive-but-never-lossy on save; the new one trades that for possible lossiness in exactly the moment users hit save — suggestion: also commit on Enter (`onKeyDown`) and/or have the settings page flush focused fields before persisting; at minimum confirm no focusless save path exists today.

2. Nit: the draft lifecycle itself (type → stays draft → commits on blur → external updates ignored while focused) has no test — `parseListFieldDraft` is covered, but the timing behavior this PR exists for isn't; a small @testing-library render/fireEvent.blur test would guard against someone reverting to controlled-commit later.

— reviewer-a · automated agent review (Hermes week-review)
