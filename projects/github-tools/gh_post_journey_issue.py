"""Open a new GitHub issue on NousResearch/hermes-agent about:
   - Hermes Desktop has no GUI entry point for /journey (CLI-only slash command)
   - Same parity gap as several other "cli_only" desktop features.

Searched for prior art: nothing exactly matches "desktop journey entry point".
Closely related (same root cause: `cli_only=True` on CommandDef):
- #57472  Add /journey to gateway slash commands         (Telegram/Discord)
- #60442  /skills pending command is cli_only             (Desktop+Dashboard)
- #46409  Make /restart available in Desktop chat
- #51754  /reasoning /model /fast /voice /skills blocked
- #44063  Profile switcher in desktop GUI
- #53521  Plugin Management UI in Desktop
- #58653  Desktop sidebar session visibility

Plan: post a new issue scoped to Desktop only (gateway is a different surface),
with Related: links so maintainers can dedupe if they decide to roll it into #57472
or a tracking umbrella. Will NOT mark it a duplicate of #57472 — different
problem (gateway vs desktop), different user (CLI user vs GUI user).
"""
import json, urllib.request
from pathlib import Path

env = Path(r'C:\Users\admin\AppData\Local\hermes\.env').read_text(encoding='utf-8')
tok = next(line.split('=', 1)[1].strip()
           for line in env.splitlines()
           if line.startswith('GITHUB_TOKEN='))
hdrs = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {tok}',
    'User-Agent': 'Hermes-Agent (AI assistant on behalf of @Enough1122)',
    'Content-Type': 'application/json',
}

title = "[Feature]: Add a /journey entry point in Hermes Desktop (parity with CLI)"

body = r"""## Problem or Use Case

Hermes Desktop (`hermes desktop` / `hermes gui`, the native Electron app) is
marketed as the GUI surface for users who don't live in a terminal. But
`/journey` — the slash command that shows the learning timeline of accumulated
memories, skills, and progress — is reachable **only** from the CLI/TUI, not
from the Desktop chat input.

Steps to reproduce:

1. Launch Hermes Desktop (`hermes desktop` or `hermes gui`).
2. Open a chat in the Desktop UI.
3. Type `/journey` in the Desktop chat composer and press Enter.
4. Expected: a list of memories and skills, the same way `hermes journey` shows
   it in a terminal.
5. Actual: nothing happens — the slash command is silently dropped. The
   Desktop composer has no menu, sidebar item, or button for `/journey` either,
   so the feature is effectively invisible to anyone who never opens a
   terminal.

The Desktop user is told to "use a terminal" to see their own learning
progress — which contradicts the whole point of shipping a Desktop surface.
For non-CLI users (the explicit target audience of `hermes desktop`) this
hides one of Hermes's flagship capabilities behind a wall.

## Proposed Solution

Bring `/journey` to Hermes Desktop with the same parity the project already
chases for other CLI-only features:

1. **Composer-level**: typing `/journey` in the Desktop chat input dispatches
   the slash command, the same way the gateway worker already dispatches
   other slash commands. (The current gap is that `cli_only=True` on the
   `CommandDef` for `/journey` makes it invisible to non-CLI surfaces.)
2. **Sidebar / settings**: add a "Journey" entry to the Desktop sidebar
   (next to Skills, Tools, Cron, Plugins — see #53521) that opens a
   dedicated panel rendering the memory/skill timeline.
3. **Visual fix**: if the existing /journey ANSI-leak issue (#56533, closed)
   ever re-emerges in the chat bubble, make sure the Desktop chat view
   renders the timeline as styled HTML/markdown, not raw terminal output.

Implementation note: `cli_only=True` is the same `commands.py` flag at the
root of #60442 (`/skills pending`), #46409 (`/restart`), and #51754
(`/reasoning`, `/model`, `/fast`, `/voice`, `/skills`). A clean fix would
either (a) flip `cli_only=False` on `/journey` and ensure the
`tui_gateway/slash_worker.py` path handles it (the post-#56533 fix
already strips ANSI for chat bubbles), or (b) introduce a Desktop-native
panel for the same data. Either is fine; (a) is the smaller change.

## Alternatives Considered

- **Document the workaround in the Desktop help screen** — doesn't fix the
  discoverability problem; non-CLI users won't reach for `hermes journey`
  in a terminal.
- **Only expose `/journey list`** (read-only) in Desktop, defer
  edit/delete to CLI — acceptable as a first step, but the user should be
  able to at least *see* the timeline from the GUI, and edit/delete can
  follow in a second pass.
- **Build a brand new Desktop-side journey viewer** instead of reusing the
  slash command — more work, duplicates the rendering pipeline, and the
  underlying data lives in `state.db` / the memory provider, so a separate
  viewer has to be kept in sync with the CLI output.

## Environment

- Hermes Desktop (Electron), v0.18.0 (v2026.7.1)
- OS: Windows 10
- User profile: non-CLI / GUI-first

## Related

Same root cause (`cli_only=True` on `CommandDef`) and same Desktop parity
gap — surface for maintainers' dedupe pass:

- #57472 — Add /journey to gateway slash commands (Telegram/Discord variant
  of the same problem; gateway is a different surface so I'm not marking
  this a duplicate, but if you decide to roll them together I'd understand)
- #60442 — /skills pending command is cli_only — unavailable in desktop and
  dashboard
- #46409 — Make /restart available in Desktop chat
- #51754 — /reasoning, /model, /fast, /voice, /skills slash commands blocked
- #44063 — Profile switcher in desktop GUI
- #53521 — Add Plugin Management UI to Hermes Desktop
- #58653 — Desktop sidebar session visibility and project UX is confusing
  for new users
- #62159 — RFC: Code View pane + /review in Hermes Desktop
- #41222 — Feature Request: Integrate Kanban Board into Desktop App
- #62817 — Hermes Desktop has no reachable GUI path to add a custom
  OpenAI-compatible endpoint

_(This issue was drafted and filed by Hermes Agent, an AI assistant acting
on behalf of @Enough1122.)_
"""

data = json.dumps({
    'title': title,
    'body': body,
    'labels': [],
}).encode('utf-8')
req = urllib.request.Request(
    'https://api.github.com/repos/NousResearch/hermes-agent/issues',
    data=data, headers=hdrs, method='POST',
)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        resp = json.loads(r.read())
        print('OK')
        print('URL :', resp['html_url'])
        print('NUM :', resp['number'])
        print('ID  :', resp['id'])
        print('TIME:', resp['created_at'])
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.reason)
    print(e.read().decode()[:800])
