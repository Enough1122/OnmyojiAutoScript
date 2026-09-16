> AI code review — automated review for reference; please use your judgment.

Right fix: `path.exists()` itself can raise on flaky storage (NFS/IO errors), and both loaders now treat that as "pairing data unavailable" instead of crashing whatever slash command touched it. The dual-loader test patching `Path.exists` pins both sites cleanly.

- gateway/pairing.py:477 — issue — a *persistent* non-permission `OSError` (failing mount, disk I/O error) now returns `{}` silently on every call, which reproduces the exact symptom #10270 documented — the user looks unauthorized with no diagnostic anywhere in the logs — why it matters — the PermissionError branch got the loud, actionable warning precisely because silent-empty is undiagnosable; generic OSErrors deserve at least one `logger.warning("pairing file %s unreadable: %s", path, e)` so operators can tell "no approvals yet" from "storage is broken".

No blocking issues found — item 1 is a two-line follow-up that would save someone a very bad afternoon.

— reviewer-b (automated review)
