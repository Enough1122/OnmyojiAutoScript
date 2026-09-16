> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): surface an actionable hint when Smart App Control blocks a backend DLL". Nice DX addition: dependency-free pure diagnosis function (testable without Electron), a pattern that matches the real-world Chinese-localized SAC error string, honest docs stating SAC and unsigned bundled Python are incompatible until signing happens (with WSL2 as the workaround), and the hint rides both the UI progress message and the rejection error. One nit:

- apps/desktop/electron/main.ts:10613 — `recentHermesLog()` is evaluated twice (once for the hint, once inside the rejection Error); capture it once in a local so both consumers see the same tail even if the log grows between the two reads.

No blocking issues found.
