> AI code review — automated review for reference; please use your judgment.

Review of "fix(kanban): enforce shared dispatch pause at claim and spawn". Solid fail-safe design: sentinel-based pause checked at claim, dispatch tick, AND the final spawn edge (closing the claim→spawn race), OSError fails closed, paused claims are returned to their source lane without counting a failure (`_release_paused_claim` marks the run `reclaimed` and emits a `dispatch_paused` event), and the tests cover ready/review claims, mid-claim pause arrival, resume, and unreadable-path fail-closed. Suggestions:

1. hermes_cli/kanban_db.py:598 (silent fail-closed) — `except OSError: return True` means a transient filesystem hiccup (NFS/permission blip) silently pauses ALL kanban dispatch across every board with zero signal — correct to fail closed, but please log once per tick (or per state change) when the lookup errors, so operators can distinguish "someone set a pause" from "the check itself broke".

2. hermes_cli/kanban_db.py:4646 (ambiguous None) — `claim_task`/`claim_review_task` now return None both for "already claimed/not ready" and "dispatch paused"; callers (and future plugin authors) can't tell which — either update the docstrings to name the pause case or add a debug log line when the pause suppresses a claim attempt.

3. hermes_cli/kanban_db.py:9367 (unused reason payload) — the sentinel file carries `{"reason": ...}` but nothing reads it: `DispatchPausedError` reports only the path, and the early-return in `dispatch_once` logs nothing — parsing and surfacing the reason (in the exception text and/or a log line) would make pauses much easier to triage.

4. hermes_cli/kanban_db.py:9894 (nit) — `dispatch_is_paused()` stats the filesystem once per claim attempt inside the spawn loop; harmless today, but if boards grow this could hoist to one check per `dispatch_once` tick with the final-edge check retaining race safety.

No blocking issues found.
