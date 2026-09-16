> AI code review — automated review; please use your judgment.

1. `agent/delegation_context.py` (`is_delegated_child_process_context`) — consuming the env marker fixes the long-lived-process wedge (#87650) but introduces a subtler flip: a *genuine* delegated fork that checks delegation **more than once** gets `True` on the first call and `False` on every later one (the marker was popped), so any second gate — e.g. a kanban write checked again after setup — silently changes classification mid-run — why it matters: the new test actually enshrines the flip (`True` then `False`), which may be the wrong contract for short-lived-but-multi-check forks — suggestion: move the consumed value into a module-level `_LINEAGE_WAS_CHILD = True` flag and return it on subsequent calls, so consumption is sticky-True for the process lifetime while still unwedging long-lived processes that were never children.

Otherwise the design reads well: ContextVar stays authoritative for the in-process case, the env marker remains the only signal across forks, and the regression test pins both sources plus the ContextVar-priority ordering.

— reviewer-a · automated agent review (Hermes week-review)
