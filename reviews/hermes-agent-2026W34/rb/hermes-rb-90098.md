> AI code review — automated review; please use your judgment.

Right guard in the right place: ad-hoc-signed local builds have nothing valid for stapler to staple, the creds-present bypass path (BWS re-injecting `APPLE_*`) is called out as the reason the existing check misses this case, and mirroring `_force_adhoc_macos_signing` keeps the two signing decisions consistent.

No blocking issues found.

Nit (`apps/desktop/scripts/notarize.mjs:~58–59`): the ````'false'```` comparison is case-sensitive — ````CSC_IDENTITY_AUTO_DISCOVERY=False```` (or `FALSE`) would still attempt notarization and hit the original stapler failure; lowercasing already happens, so comparing against `{'false','0','no'}` (or just lowercasing the value before comparing) closes that spelling gap. Also worth a one-line note that the script has no unit coverage since it only runs inside electron-builder hooks.

— reviewer-a · automated agent review (Hermes week-review)
