> AI code review — automated review for reference; please use your judgment.

Correct fix: failing a task at the 300s floor while its subprocess is still inside a legitimate 900s route window makes the watchdog lie about long-running profiles, and `max(floor, route+grace)` preserves the old behavior for agents without a configured timeout. Points:

1. plugins/platforms/a2a/adapter.py:_orphan_timeout_for (~472) — correctness hinges on `rec.get("agent_slug", "")` matching the actual record key in the tasks registry. If the stored field is named differently (`agent`, nested under routing), every lookup quietly degrades to "" and the floor timeout applies again — the exact bug this fixes, now invisible. Please pin the record shape with a unit test that builds a real registry entry (route timeout 900) and asserts the watchdog leaves it alive past 300s but fails it after 960s.
2. This PR ships no tests at all beyond touching the call site; given item 1, even one focused test would carry most of the review weight.
3. adapter.py:~497 — the log line dropped the applied timeout ("marked failed" vs the old "(timeout %ds)"). With per-agent thresholds, operators now can't tell from logs whether 300 or 960 was used; include the computed value. (nit)
4. `_ORPHAN_GRACE = 60` hardcodes slack for subprocess teardown/latency; consistent with sibling constants and fine as a default. (nit)

No blocking issues found.
