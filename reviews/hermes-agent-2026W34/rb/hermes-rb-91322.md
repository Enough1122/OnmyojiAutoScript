> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): allow guarded sibling profile restart". The layered approach (broadened regex + new shlex tokenizer for detection; a deliberately narrow 5-token exemption that proves both gateway identities from state files before clearing the marker) is well conceived and fail-closed. Suggestions before merge:

1. cron/lifecycle_guard.py:126 (evasion gap) — the tokenizer strips only `--profile`/`-p`; any OTHER accepted global between `hermes` and the subcommand (`hermes <other-global-flag> gateway restart`) leaves `filtered[:2] == [<flag>, "gateway"]` and evades BOTH the regex and the tokenizer — please cross-check the CLI pre-parser's full set of recognized pre-subcommand globals and skip those too (or match `gateway restart` anywhere after dropping option-like tokens), otherwise the canonical foot-gun remains reachable through a decorated spelling.

2. tools/terminal_tool.py:2637 (portability) — the rewritten child command uses the POSIX `VAR=value cmd` prefix (`_HERMES_GATEWAY=0 ...`) — verify `env.execute(...)` for `env_type="local"` always routes through a POSIX shell; under a native Windows shell that line is invalid syntax and the newly allowed restart fails with a confusing error — passing the env var via execute kwargs (if supported) would be shell-agnostic.

3. tools/terminal_tool.py:2660 (TOCTOU/trust) — identity proof reads mutable `gateway_state.json` files and the exec happens afterwards; a swapped/re-written state file between proof and execution redirects the restart — acceptable for the local threat model, but worth one comment documenting that these files are trusted, plus (ideally) a post-exec sanity log naming proven pids.

4. tools/terminal_tool.py:3035 (coupling) — the exemption skips the entire `contains_gateway_lifecycle_command_or_referenced_script` scan; that is sound only because the accepted shape (exactly `hermes --profile NAME gateway restart`) cannot carry chains or script references — add a pointed comment (or an assertion) tying the scanner-skip to that invariant so a future widening (allowing `stop`, extra flags, absolute paths) forces a conscious revisit.

5. tests/hermes_cli/test_gateway_restart_loop.py:285 (coverage) — no case pins the behavior for an absolute-path binary (`/usr/local/bin/hermes --profile hermes-fo gateway restart`): today it is blocked (shape mismatch) even though it is arguably legitimate — either widen the accepted shape or add the test documenting intentional strictness.

Nice detail keeping `stop` out of the exemption and covering quoted-selector spellings (`'-p'`, `'--profile=…'`, `'gateway'`) on both the detect and block sides.
