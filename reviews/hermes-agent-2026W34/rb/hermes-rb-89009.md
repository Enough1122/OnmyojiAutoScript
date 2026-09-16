> AI code review — automated review for reference; please use your judgment.

Correct root-cause fix: `setsid` detaches the session but leaves the updater in the gateway's cgroup, so KillMode=mixed turns any concurrent restart into a SIGKILL mid-build — a transient user unit with its own cgroup is the right primitive, `--collect` prevents unit litter, and the user-manager probe with graceful setsid/start_new_session fallbacks keeps root-system-service installs working. The tests assert the actual spawned argv for both the systemd and fallback paths. Points:

1. gateway/slash_commands.py:~5990 — the probe uses **blocking** `subprocess.run(..., timeout=5)` inside this async handler: for up to 5 seconds the entire gateway event loop is stalled (all chats, all streams) while waiting on systemd-run. Use `asyncio.create_subprocess_exec`/`to_thread`, or shrink the probe timeout — a hung user manager shouldn't freeze every active session to decide how to spawn an update.
2. The probe unit name `hermes-update-probe-{pid}` is reused across sequential updates in the same process; with `--collect` the unit self-cleans so collisions are unlikely, but appending `int(time.time())` (as the real spawn already does) removes the question entirely. (nit)
3. No log line records *which* spawn path was taken (transient unit vs setsid vs bare). When someone reports "update died again", that's the first thing you'll want. One info line naming the path + unit name would do. (nit)
4. Fallback ordering (probe fail → setsid → bare start_new_session) preserves every prior environment, and both are regression-tested with real argv assertions. (positive)

No blocking issues found beyond item 1's loop stall.
