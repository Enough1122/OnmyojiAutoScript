> AI code review — automated review for reference; please use your judgment.

Right diagnosis and right pattern: node-gyp needs a C++ toolchain that was never checked, so failures surfaced as a wall of make output deep in npm install; best-effort auto-install with per-distro commands plus explicit manual instructions matches the existing installer style, and the macOS CLT path correctly notes git-without-CLT as the gap it covers. Points:

1. scripts/install.sh — this diff only *defines* `check_cxx_compiler`; the hunk never wires it into the main flow. Please confirm a call site exists before `install_node_deps` (and that `HAS_CXX_COMPILER=false` actually gates something — warn-and-continue vs abort), otherwise this is dead code. One line in the PR description pointing at the invocation would settle it.
2. The macOS branch blocks up to **15 minutes** waiting for the CLT dialog. For an unattended/CI-style run that's a hang; consider honoring a skip env (`HERMES_SKIP_CLT_WAIT=1`) or capping shorter with a "re-run after installing" message instead. (nit)
3. Android gets manual instructions only — `pkg install clang` is trivially automatable like the Linux cases, if Termux installs are supported enough to bother. (nit)
4. `$sudo_cmd env DEBIAN_FRONTEND=noninteractive ...` handles the empty-sudo case correctly by expanding to bare `env ...`? When `sudo_cmd=""`, `$sudo_cmd env ...` word-splits to just `env DEBIAN_FRONTEND=... apt-get ...` — works, but only because apt-get tolerates running via env without root failing loudly into `|| true`. Intentional or lucky; a comment would clarify. (nit)

No blocking issues found beyond confirming item 1's call site.
