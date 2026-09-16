> AI code review — automated review; please use your judgment.

1. `gateway/run.py:~12327–12330` — the abort calls ````self.async_session_store.assert_no_cross_profile_session_aliases()````, but the test stubs `_async_session_store` with a `SimpleNamespace` rather than exercising the real `AsyncSessionStore` — why it matters: if `AsyncSessionStore` forwards methods **explicitly** (the `@_offloaded` pattern at the top of `gateway/session.py` suggests per-method wrapping rather than generic `__getattr__`), the new sync method may not exist on the async wrapper and *every* multiplexed gateway would die at startup with `AttributeError` instead of reaching this guard — suggestion: either confirm a generic forwarder exists, add the explicit `@_offloaded` forwarding, and add one integration test calling through the real async wrapper.

2. Nit (`gateway/session.py` `assert_no_cross_profile_session_aliases`): like #90034's gate, the raised operator-facing message names counts but no remedy; one clause ("resolve by renaming/removing one profile's routing row, or migrate the shared session into a single profile") would save operators a source dive. The deliberate omission of keys/session IDs is the right call and nicely tested.

3. Nit: the docstring honestly scopes the check to the root/legacy routing index; consider a follow-up TODO marker for scanning per-profile `state.db` indexes once a migration path exists, so the limitation stays visible.

The guard logic itself is precise: `main`/`default` namespace equivalence, within-profile aliases legitimate, unprofiled legacy keys skipped (can't prove a collision), per-session counting, multiplex-off fast path that doesn't even load the index — each pinned. Aborting *before* adapter creation (`_create_adapter.assert_not_called()`) is exactly the right ordering for an invariant whose violation corrupts from first message.

— reviewer-a · automated agent review (Hermes week-review)
