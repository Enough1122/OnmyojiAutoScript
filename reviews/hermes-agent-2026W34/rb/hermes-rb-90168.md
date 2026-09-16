> AI code review — automated review for reference; please use your judgment.

Canonical fix: a detached gateway's FD 0 is whatever the launcher left behind (often closed after `nohup ... &`), and an inherited dead descriptor aborts CPython children at `init_sys_streams` before the script runs — `stdin=subprocess.DEVNULL` is exactly the deterministic answer. I verified this is the only `Popen` site in cron/scheduler.py, so there's no sibling hazard. Points:

1. tests/cron/test_cron_script.py:~109 — the FakeProc asserts the *kwarg*, which pins the contract but can't reproduce the original failure (a real child with a closed fd 0). If you want true regression insurance, a POSIX-gated companion test could close fd 0 in-process before invoking `_run_job_script` against a real script and assert success — skippable on Windows. Optional; the kwarg pin plus the documented abort signature is already decent.
2. The test docstring quoting the exact `Fatal Python error: init_sys_streams` text is great failure archaeology — anyone hitting the symptom in another subprocess site will find this from a log grep. Consider copying that one-liner into the Popen call comment too, so the reason lives next to the code rather than only in tests. (nit)

No blocking issues found.
