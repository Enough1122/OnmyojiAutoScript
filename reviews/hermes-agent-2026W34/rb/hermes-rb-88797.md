AI code review note for PR 88797:

Clean i18n completion: adds the six missing zh strings for HUD and terminal keybind actions that the Translations type requires, with accurate translations (切换 HUD 模式 / 新建终端 / 上一个终端 etc.). Scope is exactly the missing keys - no drive-by edits.

Nit: en.ts also defines `'view.terminalSelection'`-adjacent entries like `'view.flipPanes'`, `'view.findInPage'`, `'view.findNext'`, `'view.findPrevious'` and the profile-switch block; worth a quick diff of en vs zh key sets (a tiny test asserting key-set parity per locale would catch this class permanently) to confirm nothing else is missing rather than just these six.

No blocking issues found.