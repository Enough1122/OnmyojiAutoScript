> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Sensible fix for #91264: both new stops (judge transport failure, explicit worker failed flag) prevent the loop from grinding out meaningless turns, and the judge-transport stop correctly fires before the WAIT-as-CONTINUE coercion so an unreachable judge can never be misread as a continue verdict. Points:

- **No tests for either new branch.** This changes goal-loop lifecycle (hermes_cli/goals.py:~2257 and ~2305), yet nothing exercises it: fake run_turn returning {"failed": True} should stop with outcome=stopped; a judge_goal transport failure should stop even when its verdict field would have said done; and a legacy string-returning run_turn should keep looping unchanged. All three are cheap with monkeypatched callables and would pin the contract this PR introduces.

- **goals.py:~2305 — any single worker failure now terminates the loop, including transient ones.** A one-off provider 429/timeout sets failed=True and the whole goal stops, where previously the next turn might have recovered. If #91264's intent is "stop wasting turns on hopeless failures," consider a small consecutive-failure threshold (stop after 2-3) or document why first-failure-stop is the chosen trade-off.

- **Callable contract is implicit.** cli.py:_run_turn now returns a dict, but the loop's parameter (and any docstring) still reads like str-only; the isinstance backward-compat branch suggests other implementations exist (tests? alternate frontends?). Worth annotating run_turn: Callable[[str], Union[str, dict]] at the loop signature and noting which in-repo callers still return strings — otherwise that branch is untestable dead code.

- **goals.py:~2310 — cosmetic:** when failure_reason is absent the log/reason reads "worker failed: None"; a fallback like failure_reason or "unknown" keeps incident logs greppable.

- **Scope check on the first turn:** these guards only cover turns executed inside the loop; the caller-supplied first_response turn predates them. If a failed initial turn can also wedge the loop (#91264's scenario), confirm that path is handled where first_response originates.

Nit: goals.py:2298-2300 mixes single-quoted keys ('response') with the file's dominant double-quote style.