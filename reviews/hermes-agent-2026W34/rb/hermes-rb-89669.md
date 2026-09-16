> AI code review — automated review for reference; please use your judgment.

Review of "fix(agent): honor the HTTP-date form of Retry-After on rate limits". Correct minimal fix: wire the already-existing `parse_retry_after_seconds` into the call site instead of a bare `float()`, keeping the #26293 ten-minute cap; the parser's test coverage spans both RFC 7231 forms, case-insensitive lookup, past-date clamping, and unparseable values, plus a documentation-style test recording the original defect. Two nits:

- `if _ra_parsed:` treats a clamped 0.0 (Retry-After date already in the past) as absent and falls through to the ~2s jittered backoff — semantically "retry now" vs "retry in 2s" is immaterial here, but an explicit `is not None` check would make the intent exact.
- The wiring guard (`hasattr(cl, "parse_retry_after_seconds")`) proves the import exists, not that the rate-limit branch USES it — extending it to assert the call site references the parser (source scan or behavioral stub) would fully close the drift this PR fixes.

No blocking issues found.
