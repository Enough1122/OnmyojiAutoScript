AI code review note for PR 89328:

Good two-layer defense: cloning now strips every gateway runtime identity file (pid/lock/state/takeover/planned-stop - the lock and marker files are good catches beyond the original trio), so a desktop "clone from default" can no longer inherit a live PID, and the --replace path independently verifies the PID record's HERMES_HOME before signaling, refusing with an actionable message when the pid file points at another profile. Tests cover both clone modes and assert the config itself still copies.

Two small notes:
- The comparison errors are swallowed (`except Exception: pass`) and the replace proceeds - fine as best-effort for legacy pid records, but worth a debug log inside that handler so a future helper rename does not silently disable the guard.
- Manual `cp -r` of a profile directory bypasses create_profile entirely; the replace guard is what saves that case, which is exactly why having both layers (not just the strip) is the right call.

No blocking issues found.