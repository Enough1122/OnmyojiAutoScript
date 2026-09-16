> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Nice packaging (skill + tests + catalog/sidebar wiring), but the core safety story has one serious mismatch and a few bugs:

- **sandbox.py:118-168 (`run_in_local_sandbox`) — the no-Docker fallback provides no actual isolation, while SKILL.md claims it does.** It runs `subprocess.run(command, shell=True)` on the host with the full inherited environment (`env = dict(os.environ)`), unrestricted network and filesystem — only `cwd` differs. Yet the skill description says it "prevents unverified code from mutating the host environment." Running `rm -rf ~` "in the sandbox" destroys the host. Why it matters: users will route genuinely untrusted code here believing it's contained. Suggestion: either refuse to execute without Docker unless an explicit opt-out flag is set, or rename/document the fallback honestly ("workspace-separated host execution — NOT a security boundary") in both SKILL.md and the JSON output (`engine: local_isolated` should carry an `isolated: false` field).

- **sandbox.py:79-82 + 195-218 (`execute_script_file`) — the script's host directory is bind-mounted read-write into the container.** Untrusted code gets `:rw` access to every sibling file (and can delete/rename the script itself); `run` with `--mount` has the same shape with only a Pitfalls mention of root. Suggestion: default mounts to `:ro` and add an explicit writable-mount flag; document the blast radius.

- **sandbox.py:225-237 (`prune_sandboxes`) — prune can never match anything.** Containers are created as `hermes_sandbox_<ts>_<pid>` but no `--label hermes_sandbox` is ever applied, so `container prune --filter label=hermes_sandbox` is a silent no-op. Fix: add the label in `run_in_docker`'s `docker_cmd` (and ideally a regression test asserting the flag is present).

- **sandbox.py:198-208 (`execute_script_file`) — shell-string interpolation breaks on ordinary filenames/args.** `f"python3 {file_name} {arg_str}"` mishandles `my report.py` or args containing spaces/glob chars; the unknown-extension branch additionally requires an exec bit + shebang inside the image. Suggestion: `shlex.join([...])` (py3.8+) instead of f-string concatenation, and pass args through the CLI too (the `args` param is currently unreachable dead code).

- **sandbox.py:57-85, 255-262 — container hardening gaps for a skill aimed at *untrusted* code.** No `--user`, `--cap-drop ALL`, `--security-opt no-new-privileges`, `--pids-limit`, or read-only rootfs, and the CLI happily offers `--network host` next to a description promising air-gapped execution. Suggestion: bake the defensive flags in as defaults, drop `host` from `--network` choices (or gate it behind a warning), and expose memory/cpu limits as flags rather than constants.

- **sandbox.py:127-145 — local-mode timeout orphans grandchildren.** `subprocess.run(..., timeout=)` kills only the direct shell child; anything it spawned detached (`(cmd &)`) keeps running after "timeout," and the `finally` rmtree then races live writers (`ignore_errors=True` hides the failure). Suggestion: `start_new_session=True` + `os.killpg` on timeout (POSIX), or Job Objects on Windows.

- **tests/skills/test_sandbox_runner_skill.py:26-56 — coverage gaps.** Nothing exercises the Docker path (even mocked), prune behavior, exec-file quoting, or mount handling; also the local tests invoke bare `python3`, which doesn't exist on many Windows setups — consider `sys.executable` for portability.

No blocking issues found beyond the first bullet — I'd treat the fallback-isolation claim as a release blocker for a skill whose whole purpose is containing untrusted code.
