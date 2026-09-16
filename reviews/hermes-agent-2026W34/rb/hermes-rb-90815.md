> AI code review — automated review for reference; please use your judgment.

1. tests/test_tui_gateway_server.py:_enter_deletable_cwd — the helper relies on unlinking a process's own CWD, which is POSIX-only ('Windows refuses', as the docstring says), but neither test carries a skipif guard. Why it matters: on a Windows runner monkeypatch.chdir succeeds and gone.rmdir() raises PermissionError, failing the suite for an environment where the bug cannot even exist. Suggestion: add @pytest.mark.skipif(os.name == 'nt', reason='POSIX-only mechanics').

2. tui_gateway/server.py:_safe_cwd — the fallback str(_hermes_home) can itself be the deleted directory in the PR's flagship scenario: hermes-dashboard.service launched with WorkingDirectory=<profile home>, then 'hermes profile remove' deletes that home. Both os.getcwd() AND _hermes_home are then dangling, and sessions get created with a nonexistent cwd, moving the failure downstream. Suggestion: verify existence and cascade (Path.home() or tempfile.gettempdir() as last resort), or at least log which fallback fired.

3. tui_gateway/server.py:2612 — this fixes the two visible casualties, but the same docstring observes that posixpath.abspath consults the CWD unconditionally, meaning every other dispatch-path call site doing abspath / relative resolution over a possibly-dangling CWD is one grep away from the same -32603. Suggestion: sweep tui_gateway/server.py for remaining bare os.getcwd()/abspath uses reachable from RPC handlers and route them through _safe_cwd(), or note the sweep as follow-up.

4. Nit: contributors/emails/simon@bluebeast.co rides along in an unrelated bugfix PR — fine to keep, but attribution files ideally land via the commit that uses them.

Genuinely excellent regression tests: reproducing the production failure by really deleting the chdir'd directory (instead of mocking getcwd to raise) proves the whole chain including the abspath interaction, and the docstrings record the exact operational sequence that caused it.
