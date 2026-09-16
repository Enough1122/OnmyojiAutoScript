> AI code review — automated review for reference; please use your judgment.

Correct diagnosis: `done=True` is the memory tool's *stop-retrying* contract from #42405, so feeding it into the same-tool halt counter converts a graceful degradation into a turn abort that eats the user's reply — classifying it as non-failure in both consumers is the right call, and the paired tests pin both sites including the at-capacity case staying a failure. Points:

1. agent/display.py:`_detect_tool_failure` vs agent/tool_guardrails.py:`classify_tool_failure` — these two functions are now byte-for-byte twins maintained by "keep in lockstep" comments, and this PR is itself the proof of cost: the same fix applied twice, with a third consumer guaranteed to forget someday. Extract `classify_memory_result(data) -> tuple[bool, str]` into a shared module and have both call it; the lockstep comments and half this diff disappear.
2. Ordering: the `done=True` branch preempts the "exceed the limit" branch. That's correct for today's payloads (the terminal message never mentions limits), but if the memory tool ever emits `done=True` on an at-capacity refusal, the UI would show success where "[full]" was informative. One comment line stating the precedence assumption would prevent accidental reordering.
3. Tests pin classification but not consequence: the actual #42405 symptom is the halt controller aborting after N `done=True` results. A guardrail-level test feeding two consecutive terminal degradations through the counter and asserting the turn survives would close the loop between classifier and consumer. (nit)

No blocking issues found.
