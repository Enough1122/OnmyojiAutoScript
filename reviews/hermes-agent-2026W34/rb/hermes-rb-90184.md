> AI code review — automated review for reference; please use your judgment.

Review of "test: isolate platform-specific fixtures". All three are genuine hermeticity fixes, not cosmetic: the credential-pool fixture stops auto-discovered ~/.claude OAuth entries from silently turning one-entry rotation scenarios into two-entry pools; the systemd abstract-socket skip correctly moves from "AF_UNIX exists" (true on macOS, where the abstract namespace is not) to a Linux check; and pinning `platform.system()` in the voice tests removes real dependence on the developer's OS for WSL2/PowerShell branching. No blocking issues found.

One nit: the `platform.system` pinning pattern now repeats across three voice-mode tests — a tiny `monkeypatch_platform("Linux")` helper in the test module (or conftest) would keep future platform-dependent tests from forgetting the pin.
