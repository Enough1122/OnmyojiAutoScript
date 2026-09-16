> AI code review — automated review for reference; please use your judgment.

1. hermes_cli/env_loader.py:488 — the fix protects exactly ONE launcher-owned variable by saving/restoring it around dotenv application. Why it matters: HERMES_DASHBOARD_SESSION_TOKEN is not the only launcher-minted value at risk — any future Desktop/service pairing variable will hit the same clobber-by-profile-dotenv bug and get its own bespoke patch like this one. Suggestion: define a single LAUNCHER_PROTECTED_ENV_VARS tuple (shared with whatever injects them) and restore every name present at entry; this PR then becomes data, not code.

2. Behavior note worth a release-notes line: an operator who deliberately sets HERMES_DASHBOARD_SESSION_TOKEN in a profile's .env can no longer rotate the dashboard credential when a launcher already injected one — the process value always wins. That is the right default for pairing integrity, but silent precedence changes around auth tokens deserve documentation.

Clean fix otherwise: the save happens before ANY load path (including external secrets and the terminal-config bridge), restoration sits after all writers, and the three web_server tests pin the full precedence matrix — explicit ssh token > environment > current import-time value.
