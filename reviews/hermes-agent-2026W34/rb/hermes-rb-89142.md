> AI code review — automated review for reference; please use your judgment.

1. **PR title vs content** — the title says `add hermes update --no-restart`, but after the force-push the diff is exclusively the `hermes doctor` optional-package install-hint change (the earlier ~93KB revision containing the updater work is gone from this branch). **Why it matters:** merged as-is, release notes and git history will advertise a feature this PR does not contain, and anyone subscribing for `--no-restart` will silently lose track of it. **Suggestion:** retitle to e.g. `fix(doctor): actionable pip install hints for optional packages` and open a fresh PR for the updater flag.

2. **hermes_cli/doctor.py:1110-1131 (required vs optional hint symmetry)** — optional packages now carry an explicit `pip_spec` because import-name ≠ distribution-name (`discord`→`discord.py`, `telegram`→`python-telegram-bot`), but the *required* loop still prints its hint as `(install cmd) {module}` from the bare import name — correct only while every required import name happens to equal its pip name. **Why it matters:** the first time a required dependency with a diverging dist name (think `yaml`/`pyyaml`) joins that list, doctor regresses to advising an install that installs nothing useful. **Suggestion:** give `required_packages` the same 3-tuple shape so both loops share one convention.

3. **tests/hermes_cli/test_doctor_command_install.py:135-152** — good use of `sys.modules["discord"] = None` to force the ImportError deterministically, and the line-filter approach correctly tolerates other optional packages being absent in CI. Not covered: a missing *required* package's hint (item 2's convention), which needs the same trick applied to a core module late in the run. **Suggestion:** add one required-missing case if item 2 is adopted, asserting the spelled-out spec appears.

Nit: `_python_install_cmd()` is re-evaluated inside each warning string; hoisting it once above the loops reads marginally cleaner and keeps future multi-line command output consistent across all hints.

— Reviewed by Hermes AI reviewer (reviewer-f2)
