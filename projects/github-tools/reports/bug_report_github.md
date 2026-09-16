# Title: [Bug] Windows desktop app flashes cmd console window intermittently after update

## Describe the bug
After updating the Hermes desktop app on Windows 10, cmd.exe console windows flash intermittently during normal use. The windows pop up briefly and immediately close, causing visual distraction. This happens not only during cron job execution but also during regular chat conversations.

## To Reproduce
1. Run Hermes desktop app on Windows 10 (latest version as of June 26, 2026)
2. Have a normal conversation with the agent
3. Observe cmd.exe windows flashing intermittently

The issue is especially noticeable when:
- The terminal tool executes commands (especially python scripts)
- Cron jobs run (e.g. every 30 min for stock analysis)
- Any background subprocess is spawned

## Expected behavior
Subprocess should be spawned without showing a console window. Previous version did not have this problem — it appears to be a regression from a recent update.

## Workaround found
Using `pythonw.exe` instead of `python.exe` in scripts eliminates the flashing for those specific calls, suggesting the root cause is missing `CREATE_NO_WINDOW` (0x08000000) flag when spawning console subprocesses on Windows.

## Environment
- OS: Windows 10
- Hermes desktop version: latest (updated June 26, 2026)
- Terminal backend: local (git-bash)
- Python: 3.12 (Microsoft Store) / 3.11 (Hermes venv)

## Suggested fix
In the terminal tool's subprocess creation code (likely in the Windows-specific process spawning path), add `subprocess.CREATE_NO_WINDOW` (0x08000000) to the creation flags when calling `subprocess.Popen()` or similar on Windows. This flag prevents the creation of a console window for the subprocess.