> AI code review — automated review for reference; please use your judgment.

1. `.gitignore:100–105` — the new patterns are unanchored (`log.txt`, `sqlite_leak_fix.png`, `default.tar.gz`), so they ignore files with those names at **every depth**, not just repo root — why it matters: `log.txt` in particular is a plausible name for a test fixture or plugin sample data; when someone adds one later, git will silently refuse to track it and the failure mode ("why won't my file commit?") wastes an hour — suggestion: anchor them (`/log.txt`, `/sqlite_leak_fix.png`, `/default.tar.gz`) since the stated intent is "repo-root build/debug artifacts".

2. `AGENTS.md:505–516` — converting the Dev Commands fenced bash block into a numbered plain-text list loses syntax highlighting and one-shot copy/paste of the whole sequence, with no apparent gain over the original — why it matters: AGENTS.md is contributor-facing; the fenced block was the more useful rendering — suggestion: keep the fence and just prepend the "run from `ui-tui/`" note as a comment or lead-in line.

3. `acp_adapter/server.py:~227` — `logger.warning` added to the `HERMES_VERSION` import fallback runs at **module import time**, before logging configuration exists in most entry paths, so it emits via the stdlib last-resort handler straight to stderr — why it matters: in packaging modes where `hermes_cli` is legitimately absent from the ACP sidecar this becomes recurring stderr noise rather than a diagnosable signal — suggestion: keep the message but route it through the same once-per-process/debug-level pattern used by other import fallbacks in this file, or attach the reason (`exc_info=True`).

4. Nit (`.gitignore:103`): `*.png.bak` is likewise unanchored; if it's meant for editor swap files next to the deleted screenshot, scope it (`/*.png.bak`) for symmetry with item 1.

Overall: worthwhile housekeeping — dropping committed binaries plus documenting the deliberate `shell=True` exception in `secret_sources/base.py` are genuine improvements; no blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
