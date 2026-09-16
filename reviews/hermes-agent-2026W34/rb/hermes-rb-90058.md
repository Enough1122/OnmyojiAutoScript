> AI code review — automated review; please use your judgment.

Correct root-cause fix with a tight blast radius: only multiplexed gateways pin `cwd` to the serving profile home (via the per-turn `get_hermes_home()` remap), single-profile gateways keep the existing TERMINAL_CWD fall-through untouched, and both behaviors are pinned end-to-end through `resolve_context_cwd()` including cleanup via `_clear_session_env`.

No blocking issues found.

Nit (`gateway/run.py:~24433–24438`): the ````except Exception: cwd = ""```` silently reverts to the buggy cross-profile cwd if `get_hermes_home()` ever raises mid-remap; a `logger.debug(..., exc_info=True)` would keep such a failure findable, since its symptom (wrong AGENTS.md injected) points nowhere near this line.

— reviewer-a · automated agent review (Hermes week-review)
