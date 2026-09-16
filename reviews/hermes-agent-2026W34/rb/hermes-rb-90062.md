> AI code review — automated review; please use your judgment.

Important safety fix with the right shape: durable runtime trees are excluded both from category guessing (so `scripts/test_*.py` authored by the agent is never auto-disposed just because of its filename) and from empty-directory sweeps via the existing protected-set union, and the migration tests prove a **stale tracker entry** gets cleared without deleting the file it points at — that's the subtle half most fixes would miss.

No blocking issues found.

Nit (`plugins/disk-cleanup/disk_cleanup.py:~147–155`): `_DURABLE_RUNTIME_TOP_LEVEL` hand-copies Hermes' top-level runtime tree names; when core adds a new one, this plugin silently re-exposes it to cleanup until someone remembers this list — if the names are derivable from a shared constant (or a small core helper listing durable roots), deriving them would turn future drift into a compile-time concern rather than a deleted-files incident report.

— reviewer-a · automated agent review (Hermes week-review)
