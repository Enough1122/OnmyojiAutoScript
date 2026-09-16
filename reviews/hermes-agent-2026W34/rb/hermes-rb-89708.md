> AI code review — automated review for reference; please use your judgment.

Right idea — a throwaway progress window during an unattended update is pure noise, and `--no-ui` is the cleaner suppression than hunting windows post-hoc. The test updates in lockstep. One verification:

- apps/desktop/electron/updater-process.ts:102 — issue — the handoff passes `--no-ui` to whatever `scripts/desktop-update/posix.sh` exists at the *current checkout*; the existing "predates the script" existence check doesn't distinguish a version that lacks `--no-ui` parsing — why it matters — an older-but-present script would receive an unrecognized argument, and depending on its `set -u`/positional handling that could abort the update rather than ignore the flag — suggestion — confirm the flag has been parsed since the script's first commit (making the existence gate sufficient), or feature-detect by grepping the script text for `--no-ui` before appending.

No blocking issues found — item 1 is a one-minute confirmation against git history.

— reviewer-b (automated review)
