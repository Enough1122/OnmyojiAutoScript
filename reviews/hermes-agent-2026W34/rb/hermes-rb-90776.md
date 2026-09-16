> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): confirm before closing the main window". Nice decomposition: the decision logic lives in a pure `window-close-policy.ts` with a tight truth-table test (darwin/handoff/quit bypass, prompt dedup via 'hold'), the failed-dialog path correctly leaves the window open instead of quitting, and the `finally` resets the prompt latch. Suggestions:

1. apps/desktop/electron/main.ts:11949 (i18n) — the dialog strings ("Keep Hermes running?", button labels, body text) are hardcoded English while the rest of the desktop shell is fully localized through @/i18n (five locales) — main-process code can't import the renderer i18n directly, but the locale preference could be passed at window creation or read from config here; at minimum file a follow-up so non-English users don't get an untranslated quit prompt.

2. apps/desktop/electron/main.ts:15014 (latch lifecycle) — `nativeQuitInProgress` is set in before-quit and never cleared; if the backend teardown path ever aborts the quit (teardown failure without a retrying app.quit()), the flag stays latched and every subsequent manual close silently bypasses the confirmation forever — worth verifying the teardown .finally() always either completes the quit or resets this flag.

3. apps/desktop/electron/window-close-policy.test.ts:24 (response contract) — `closeActionForResponse` maps anything non-0/1 to 'cancel', which safely covers Electron's documented -1 error return; consider asserting response values come only from the buttons array length (an out-of-range positive like 7 currently cancels too — fine, but pin it with one more assert so the fallback intent is explicit).

4. apps/desktop/electron/main.ts:11946 (nit, UX semantics) — Esc/cancelId lands on "Cancel" (window stays open, neither minimized nor quit); combined with defaultId 0 = "Minimize", keyboard users get minimize-on-Enter and keep-open-on-Esc — sensible defaults, just confirming they're deliberate since "Quit Hermes" is then reachable only by arrow/tab selection.

No blocking issues found.
