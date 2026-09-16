> AI code review — automated review for reference; please use your judgment.

Well-targeted fix using the right mechanism: stamping the bridge-written value at *set-time* (`_HERMES_TERMINAL_CWD_LAUNCHED`, mirroring the `_HERMES_GATEWAY` idiom) means the suppression decision compares against what this process actually wrote rather than guessing from liveness or cwd state — and the test suite proves the properties that matter: mismatched sentinel still warns, absent sentinel still warns, explicit config stays independent, a chdir between bridge and warn can't resurrect the false positive, and MESSAGING_CWD suppression remains orthogonal.

No blocking issues found.

Nit: the comparison uses bare `os.path.realpath()` on both sides, which normalizes symlinks/junctions but not letter case — on Windows, a sentinel of `C:\Users\me\proj` versus a `.env`-derived `c:\users\me\proj` represents the same directory yet fails the equality check, reintroducing the false positive in exactly the environment where path-casing drift is most common. Wrapping both sides in `os.path.normcase(os.path.realpath(...))` makes the fix platform-complete; worth one test with mixed-case paths guarded by a win32 skipif for POSIX runners.

— Reviewed by Hermes AI reviewer (reviewer-f2)
