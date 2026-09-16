> AI code review — automated review; please use your judgment.

Correct platform-specific pin, well documented: the constraint explains *why* (`cryptography>=50` has no bionic/aarch64 wheel and the Rust source build OOMs on phones), points at the Termux-provided working version and the issue, and the installer surfaces a note so users understand why their cryptography differs from upstream latest. Scoped entirely to the Termux constraints file — no effect on other platforms.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
