> AI code review — automated review for reference; please use your judgment.

1. hermes_cli/stderr_timestamp.py:47 — the 78-to-0 mapping applies unconditionally, but _command_exit_code serves the generic stderr-timestamp wrapper, not just the launchd plist. Why it matters: any other consumer of this wrapper (manual runs, other supervisors, scripts checking exit status) now sees 'success' for a fatal configuration error, which masks exactly the class of failure this module exists to make visible. The module already tracks EXTERNAL_GATEWAY_SUPERVISOR_ENV elsewhere — suggestion: only translate when the current supervisor really is launchd, leaving 78 intact everywhere else.

2. hermes_cli/stderr_timestamp.py:49 — the import sits in a bare 'except Exception: pass'. Why it matters: if gateway.restart ever fails to import here (packaging issue, circular import during early startup), the mapping silently vanishes and the restart loop this PR fixes comes straight back, with no trace of why. Suggestion: emit a single warning line to the timestamped stderr in the handler — costless, and it keeps the failure mode observable.

3. hermes_cli/stderr_timestamp.py:52 — after mapping, an operator watching the process sees a clean exit while the real problem (unpaired WhatsApp channel) lives only in the log text. Suggestion: print one explicit line before exiting, e.g. 'gateway stopped: fatal config (exit 78 mapped to 0 so launchd KeepAlive stops)', so on-call diagnosis does not require knowing to grep the error log.

4. tests/hermes_cli/test_stderr_timestamp.py:50 — the new test pins the happy mapping end-to-end, but there is no companion assertion that non-78 codes still pass through unchanged through main(), nor (if item 1's gating lands) that a non-launchd context preserves 78. Both are cheap subprocess cases mirroring the existing style.

Good root-cause documentation: the comment explains why launchd specifically forces this translation (no RestartPreventExitStatus) and cross-references the s6 finish-script's 78->125 convention so the two supervisors stay comparable.
