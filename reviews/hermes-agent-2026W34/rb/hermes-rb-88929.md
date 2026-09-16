> AI code review — automated review; please use your judgment.

Three focused hygiene fixes, each well-evidenced:

1. **LSP pull-diagnostics negotiation** (`agent/lsp/client.py`) — capability-gated at initialize *and* self-learning on the first `-32601`, ending the ~58k-errors-a-week pattern of re-asking push-only servers forever. The mock server was upgraded so push-only scripts both omit the advertisement *and* reject the request, exercising both guard paths, and the tests cover the full matrix (advertised/absent/false-provider, live no-request-ever, remembered rejection with a second-call short-circuit assertion).
2. **Update-watcher spam** — both deferred-notification logs demoted to debug with the poll cadence and a real-world flood count (17k+ entries/week) cited as justification.
3. **Benign git gc races** — `_is_benign_gc_race` is properly narrow (only `gc` commands, locale-aware substring for EN/CN) and the tests prove the negative case: a genuine gc failure still logs at error level.

No blocking issues found.

Nit (`tools/checkpoint_manager.py` `_is_benign_gc_race`:~360): the benign-detection relies on localized stderr substrings ("already running" / "正运行"); other locales will still log at error level. Since the command is already pinned to `args[0] == "gc"`, an alternative is to treat any rc=128 on `gc --prune=now` against the shared store as a concurrency loss (the winner did the reclaim either way) — or accept the current behavior and note the locale limitation in the docstring.

— reviewer-a · automated agent review (Hermes week-review)
