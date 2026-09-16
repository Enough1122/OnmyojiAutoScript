> AI code review — automated review for reference; please use your judgment.

Excellent fix for a genuinely nasty cross-platform repo-health bug (case-differing filenames = permanently dirty fresh clones on Windows/macOS). Refusing at write time with an actionable error, plus the repo-wide guard test that *allowlists the one known real conflict* rather than silently passing, is exactly how to stop the class from spreading while forcing the maintainer decision on the existing pair.

— reviewer-b (automated review)

No blocking issues found.
