> AI code review — automated review for reference; please use your judgment.

Exactly right, and correctly scoped: aligning the scanner with the runtime readers' `errors="replace"` closes a real evasion (one 0xE9 byte hiding `curl | bash` behind an otherwise-skipped file) while keeping the `OSError → []` branch for genuinely unreadable paths, and the test places the detectable payload *after* the invalid byte so it proves the scan continues rather than merely that the file was opened. I checked the other decode site in this module (`_load_skill_ignore`) — skipping an undecodable `.skillignore` means *less* gets ignored, i.e., more gets scanned, so its fail-open direction is safe and correctly left alone.

No blocking issues found.

Nit: consider a debug-level log line when the replace-fallback engages; today a skill author with a legitimately non-UTF-8 encoding (Latin-1 comments, UTF-16 exports) gets silently mangled matches with no signal, and one log line makes "why does my skill keep tripping curl_pipe_shell" supportable without changing any behavior.

— Reviewed by Hermes AI reviewer (reviewer-f2)
