> AI code review — automated review for reference; please use your judgment.

Good fix and an unusually rigorous test strategy — extracting the *real* `linux_gate` body and driving it through bash (with extraction sanity markers) means the symlink regression can never silently pass against a copy. `readlink -m` over `-f` is the right choice since the unpacked dir may not exist yet at gate time.

- scripts/desktop-update/posix.sh:253 — issue (comment hygiene) — the block carries local-patch markers ("LOCAL (mhines 2026-08-21)") and the dangling note "Upstream issue drafted (not yet filed)" — why it matters — these read as private-fork breadcrumbs that shouldn't ship in the project's update script; they'll confuse every future reader who isn't you, and the issue reference points nowhere — suggestion — rewrite the comment to describe the environment fact (Fedora/ostree symlinks `/home`→`/var/home`; kernel-canonicalised `/proc/<pid>/exe`) without personal attribution, and either file/link the issue or drop the sentence.

- tests/test_desktop_update_linux_gate.py:60 — nit (coverage) — no case for an empty/unset `RELAUNCH_TARGET`; the new `[ -n ... ]` guard means canonicalisation is skipped on that side and the raw empty string falls to the `skew` branch — worth one assertion pinning that behavior so the guard isn't "simplified" away later. Also the file is missing a trailing newline (`\ No newline at end of file`), which most lint setups will flag.

No blocking issues found — item 1 before merge, please.

— reviewer-b (automated review)
