> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean feature slice: the new `hermes:composer-dictate` pub-sub follows the existing voice-toggle pattern exactly (same subscribe/dispatch shape, same `toggled === target` guard, deps wired correctly), the keybind ships unbound by default so no platform shortcut collisions, and all three locales get the settings-panel string. Reusing the mic icon's `dictate()` keeps record→transcribe→insert behavior identical to the button path — good call.

Nit (non-blocking): apps/desktop/src/i18n/zh.ts:270 — the zh label 「听写（按住说话）」 says "hold to speak," but the action is one-shot press→record→transcribe (as the code comments correctly describe); a user following the label will hold the chord expecting release-to-stop and instead get an immediate recording session. Consider 「听写（一键开始）」 or similar until/unless true hold-style push-to-talk exists, since real PTT would need keyup handling this event path doesn't have.

No blocking issues found.
