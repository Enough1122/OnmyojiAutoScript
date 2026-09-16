> AI code review — automated review for reference; please use your judgment.

Correct and well-tested: the function's own name/docstring promised one-shot semantics while the implementation only latched on the warning branch, silently re-running platform-default resolution + stat + possible read on every `get_heres_home()` call from 30+ import-time sites. Engaging the latch on first check is right, and the "profile activated mid-process is out of scope either way" scoping note preempts the obvious objection. The 51-call counting test with its self-explaining failure message ("if this is 100…") is exactly how a perf-regression test should be written. No concerns:

- Warning branch behavior unchanged for the non-default-profile case (pinned by test).
- Latch-before-check ordering means zero repeat cost even when nothing warns.
- Failure-message quality on both assertions is exemplary.

No blocking issues found.
