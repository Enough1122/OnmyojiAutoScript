> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): stop electron-builder publish-detection crash and broken launcher icon". Both halves are well-diagnosed real bugs: (1) `CI=1` from the npm lifecycle makes electron-builder implicitly resolve a publish target, which reads `apps/desktop/.git/config` that doesn't exist — pinning `--publish never` is correct since no CI drives this script; (2) the venv re-exec detection correctly catches the argv0 fast-path returning the raw `hermes` SCRIPT whose `#!/usr/bin/env python3` shebang resolves outside the venv (the exact missing-deps taskbar-icon crash), while properly whitelisting console-scripts inside the venv and self-contained binaries via the sys.prefix containment check. Suggestions:

1. Scope note — two unrelated fixes in one PR again (builder publish crash + Linux desktop-entry launcher); each is small, but they touch different subsystems and would bisect independently if split.

2. hermes_cli/linux_desktop_entry.py:_needs_venv_reexec (nit) — a script whose shebang points at THIS venv's python passes the whitelist but breaks if the venv is later deleted while the desktop entry survives; acceptable trade-off, worth one comment acknowledging it.

3. nit — the builder-side fix assumes local builds never publish; if a maintainer ever runs this script from CI expecting a release, the pinned "never" will silently skip publishing — a comment pointing at where official releases happen would prevent confusion.
