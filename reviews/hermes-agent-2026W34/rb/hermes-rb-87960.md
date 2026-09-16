> AI code review — automated review for reference; please use your judgment.

Review of "feat(desktop): relocate wake/TTS toggles from composer to titlebar". Clean relocation: composer decluttered (the old always-visible ear and its five visibility-state tests correctly replaced by absence assertions), titlebar gains wake/auto-speak wired directly to their stores with haptics, and the incidental TitlebarIcon→Codicon migration in touched code reduces icon-system duplication. Suggestions:

1. apps/desktop/src/app/shell/titlebar-controls.tsx (lost context-awareness) — the old ConversationPill rendered the ear DISABLED with "paused during voice chat" while a voice conversation held the mic; the new titlebar toggle reads only `$wakeWord` and has no notion of an active voice conversation holding the mic — verify the wake listener itself pauses during voice chat at the service layer, or surface the paused state here too, otherwise users can re-enable wake mid-call and wonder why it misbehaves.

2. nit — new titlebar tooltips need their `titlebar.*` i18n keys confirmed across all locales (the diff touches component code; label strings weren't visible).
