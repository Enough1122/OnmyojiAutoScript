import urllib.request, json
TOK = open(r'C:\Users\admin\AppData\Local\hermes\.env','r',encoding='utf-8').read()
gh = [l.split('=',1)[1].strip() for l in TOK.splitlines() if l.startswith('GITHUB_TOKEN=')][0]
hdrs = {
    'User-Agent': 'Hermes-Agent (AI assistant on behalf of @Enough1122)',
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {gh}',
}

title = '[Feature Request] Interrupt current TTS playback when a new reply starts'

body = """## Problem

When `voice.auto_tts: true` is enabled in `config.yaml`, every assistant reply is enqueued for TTS playback. If the user sends a new message before the previous reply finishes speaking, the new reply **waits for the old one to finish** instead of interrupting it.

This is annoying when:
- A long reply is still playing but the user already has the answer
- A new short reply (e.g. "OK", "好的") comes in but the user has to wait
- The user wants to **stop the audio** without muting the whole system

## Expected behavior

The currently-playing TTS should **stop immediately** when:
1. A new assistant reply starts generating (interrupt)
2. The user clicks a "Stop" / "Mute" button in the title bar
3. (Optional) The user sends a new message

## Possible solutions

- **Option A (minimal)**: Stop the current audio when a new reply is enqueued
- **Option B (better UX)**: Add a global keyboard shortcut (e.g. `Ctrl+.`) to stop TTS
- **Option C (best UX)**: Add a small "🔇" toggle in the title bar that mutes future replies + stops the current one

Option A is the simplest and probably covers 90% of use cases.

## Environment

- Hermes Desktop (Electron), `voice.auto_tts: true`, `tts.provider: edge`
- Windows 11
- Reproducible 100% of the time

## Note from submitter

I'm filing this as an **issue only** (not a PR). The fix likely lives in the desktop app's audio queue component, but I haven't dug into the source. Happy to help test if a maintainer picks this up.

_(Issue drafted and filed by Hermes Agent, an AI assistant acting on behalf of @Enough1122.)_
"""

labels = ['type/feature', 'comp/desktop']

data = json.dumps({'title': title, 'body': body, 'labels': labels}).encode('utf-8')
req = urllib.request.Request(
    'https://api.github.com/repos/NousResearch/hermes-agent/issues',
    data=data, headers={**hdrs, 'Content-Type': 'application/json'}, method='POST',
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())
        print('✓ Issue 已创建')
        print(f"  编号: #{resp['number']}")
        print(f"  标题: {resp['title']}")
        print(f"  URL:  {resp['html_url']}")
        print(f"  标签: {[l['name'] for l in resp.get('labels',[])]}")
except urllib.error.HTTPError as e:
    print(f'✗ HTTP {e.code} {e.reason}')
    print(e.read().decode()[:600])
