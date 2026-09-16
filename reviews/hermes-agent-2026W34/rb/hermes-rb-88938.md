> AI code review — automated review; please use your judgment.

1. `tools/daemon_pool.py` (`_adjust_thread_count`) — this is the **same Python 3.14 worker-context fix already proposed in PR #88910** (byte-for-byte the `_create_worker_context` branch): two open PRs shipping one fix guarantees a merge conflict and duplicated maintenance — why it matters: whichever lands second will need manual reconciliation, and reviewers have to double-check both copies stayed identical — suggestion: coordinate so exactly one PR owns the daemon_pool change (this one is the more natural home given its title mentions 3.14 workers) and rebase the other onto it.

2. The `summary_target_ratio` getattr guard itself is correct: missing ratio → floor 0 → idle compaction proceeds with the plugin engine owning policy, mirroring the existing guard in `conversation_compression.py`, and the tests drive a genuinely engine-shaped compressor through both the fire and no-floor-small-context paths.

Nit (`agent/turn_context.py`:~794–801): floor-0 semantics mean *every* idle-resumed session under a plugin engine compacts regardless of transcript size — deliberate per the comment, but worth one line on the `ContextEngine` ABC ("engines own their compaction threshold; the scheduler only gates on idle time") so plugin authors aren't surprised.

Also noted: the new `.gitleaks.toml` allowlist is tightly scoped (one fixture path + one public OAuth client UUID), which is the right way to do it.

— reviewer-a · automated agent review (Hermes week-review)
