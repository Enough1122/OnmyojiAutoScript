> AI code review — automated review for reference; please use your judgment.

Excellent outage-resilience fix: the incident narrative (GitHub unreachable → library default → stream error 405 reconnect loop) makes the design obvious, the three-tier fallback (live → memory → disk → default) covers exactly the cold-start gap that bit during the outage, persisted-version validation rejects every junk shape rather than trusting disk, write failures warn once instead of spamming per reconnect, and the opt-out (`cacheFile: null`) preserves legacy behavior verbatim. The top-level-assertion test file exercises every tier and failure mode including hung-fetch timeouts.

— reviewer-b (automated review)

No blocking issues found.
