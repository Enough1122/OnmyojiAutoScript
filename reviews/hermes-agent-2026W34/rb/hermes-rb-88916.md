> AI code review — automated review; please use your judgment.

Correct and complete fix for a nasty replay bug: all three prune paths (TTL-expired, over-max oldest, and the belt-and-suspenders untracked sweep) now retain a `_completion_consumed` marker while its matching completion event still sits in `completion_queue`, so a stale event that the TUI poller requeues can't be re-delivered as a fresh synthetic turn after its session record is pruned — and the marker is dropped on a later prune once the event is gone, so nothing grows unboundedly. Both the dict-prune path and the lookup-path sweep are covered by tests that drive the real queue, including the post-delivery cleanup assertion.

No blocking issues found.

Nit (`tools/process_registry.py` `_completion_event_pending`:~2500): it reads `self.completion_queue.queue` directly; fine for a stdlib `queue.Queue` you own, but wrapping that access in one tiny helper (`_iter_completion_events()`) or asserting the queue type would keep the invariant obvious if the container ever changes.

— reviewer-a · automated agent review (Hermes week-review)
