> AI code review — automated review for reference; please use your judgment.

Outstanding rigor for a kill-safety change: the argv classifier moves into a standalone stdlib-only module embedded *verbatim* into remote-lifecycle.ts (with bidirectional embed-contract tests so the two can't drift), wrapper-`exec` resolution fixes the real FOREIGN misclassification for post-exec argv shapes, cleanupStale now treats an OWNED kill-failure as transient and explicitly refuses to drop lock/log, and the new serve-side lock/log watchdog's decision function is pure and exhaustively table-tested — including a contract test that *forbids* pkill/killpg/parent-pid/age heuristics from ever returning. Items:

- apps/desktop/electron/ssh_pid_owned.py:14 — issue — `_wrapper_exec_targets` accepts only the exact 4-token shape `exec <py> <script> "$@"`; wrappers written as `exec env FOO=1 python script "$@"`, multi-line, or with intermediate flags resolve to `[]` and fall through to entry/spawn-proof paths — why it matters — those installs re-enter the FOREIGN misclassification this PR exists to fix, silently — suggestion — tolerate optional `env VAR=VALUE` prefixes (strip leading `env` tokens), or document the supported wrapper grammar next to the parser and say what unsupported shapes fall back to.

- hermes_cli/web_server.py:18799 — nit — `os._exit(0)` skips every finally/flush by design; consider logging one line ("desktop released ownership; exiting") before it, since exit code 0 from a killed serve would otherwise be indistinguishable from a clean operator stop in remote journals.

No blocking issues found — item 1 is coverage honesty for the headline fix.

— reviewer-b (automated review)
