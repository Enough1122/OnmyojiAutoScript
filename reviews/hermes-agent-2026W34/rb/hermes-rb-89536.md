> AI code review — automated review for reference; please use your judgment.

Right fix for a real operational incident (141 MB gateway.error.log from a Socket Mode reconnect flap): sharing `logging.max_size_mb`/`backup_count` with the rest of Hermes logging avoids a second config surface, recomputing on each open honors admin changes without restart, unbuffered writes make flush-as-no-op correct, and rotation races from concurrent processes are explicitly tolerated. Points:

1. hermes_cli/stderr_timestamp.py:_RotatingWriter.write (~135) — a single line larger than `max_bytes` still lands whole (check requires `tell() > 0` and only rotates *before* writing), so one pathological line can exceed the cap. That's the right tradeoff vs truncating diagnostics, but document it: "oversize lines may exceed the cap by their own length." The test's ≤2 MB assertion already encodes the slack. (nit)
2. Same class — `delete()` closes the handle but deletes nothing (rotated backups intentionally survive); the name will mislead someone into calling it for cleanup. Rename to `close()`. (nit)
3. `_rotation_config()` imports the private `_read_logging_config` from hermes_logging; a rename there silently reverts this writer to hardcoded 5 MiB/3 with no signal. Either expose a public accessor or log once at debug when the import fails. Currently the except swallows without trace. (nit)
4. Tests monkeypatch `_DEFAULT_*` constants rather than exercising `_rotation_config()`'s override path (`logging.max_size_mb` set in config.yaml) — the actual feature advertised ("same keys as agent.log") is untested. One test seeding the config would close it. (nit)
5. Rotation shift loop correctly goes highest→lowest so no backup is clobbered mid-shift. (positive)

No blocking issues found.
