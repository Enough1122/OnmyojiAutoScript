> AI code review — automated review for reference; please use your judgment.

Both restorations fix real production pain, and each ships with regression tests. Two review items, one of them security-adjacent:

1. cron/lifecycle_guard.py — `strip_inert_heredoc_bodies` before the referenced-script walk fixes the CSS-path false positive (verified by test), but it also removes the guard's visibility into **everything inside any quoted heredoc**. A job like ```python3 << 'PY'``` whose body invokes `hermes gateway restart` via subprocess previously surfaced in the walk (noisily, alongside false positives); now it's invisible to the referenced-script arm. If inert-body stripping is meant only for *quoted* delimiters whose content never reaches a shell, fine — but confirm the strip doesn't also drop **unquoted** heredoc bodies, and document the accepted detection gap ("lifecycle commands executed from within heredoc-fed interpreters are out of scope") so the security posture is explicit rather than accidental.
2. plugins/model-providers/openrouter/~137 — `"openrouter.ai" in base_url` is a substring check: `https://evil-openrouter.ai.attacker.com/v1` contains the needle and would receive the sticky `session_id`. Parse the hostname instead (`hostname == "openrouter.ai" or endswith(".openrouter.ai")`). session_id isn't a secret, but deliberately routing correlation identifiers to look-alike hosts is an easy fix here.
3. The empty-`base_url` case still sends `session_id` (tested) — correct default since unset means the official API. (positive)
4. Consider noting in the commit/PR why these hotfixes were missing from main (cherry-pick drift?) — if there's a class of production-only fixes, a quick audit for siblings would prevent the next surprise. (nit)

No blocking issues found beyond confirming item 1's accepted scope.
