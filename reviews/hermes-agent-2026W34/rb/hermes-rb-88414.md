> AI code review — automated review for reference; please use your judgment.

Correct fix for a brutal failure mode: launchd rejects cross-volume WorkingDirectory/log paths with EX_CONFIG *before any Hermes log exists*, so an external-SSD HERMES_HOME symlink produced an unbootable service with zero diagnostics. The volume probe fails open on stat errors (keeping current behavior), both branches are tested, and the log fallback lands in a labeled `~/Library/Logs` dir users can actually find. Points:

1. hermes_cli/gateway.py:~8117 — falling back to `Path.home()` for WorkingDirectory reintroduces exactly the "volatile source checkout" rot that `_stable_service_working_dir()` was created to avoid (per its own comment two lines up). For external-volume users the choice is EX_CONFIG-vs-stale-cwd; consider a stable *boot-volume* anchor instead (`~/Library/Application Support/Hermes`) so neither problem applies.
2. When the log-dir fallback activates, nothing tells the user their gateway/error logs moved to `~/Library/Logs/<label>`. A single print during `hermes gateway install` (or a line in the plist generation) would save every affected user one confused support round. (nit)
3. `_same_volume` compares resolved paths' `st_dev` — correct for symlinks and bind mounts alike; fail-open on OSError is the right bias given the caller can't proceed otherwise. (positive)
4. Tests mock `_same_volume` for branch coverage rather than exercising real st_dev across volumes (pragmatic — CI can't span devices); the actual probe remains untested but is three lines of stdlib. Acceptable. (nit)

No blocking issues found.
