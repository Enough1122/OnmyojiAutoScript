> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right routing semantics for Bot Mode: a same-install backend reachable over plain HTTP should never have its turns tunneled through an SSH window-primary just because that's where the user happens to be connected — restricting the "active primary wins" rule to the *preferred* class (local outright, else HTTP, else everything) while keeping SSH-only groups routing through SSH preserves the old guarantee exactly where it still applies. The hover-warm skip for SSH sourceScoped rows closes the connect-on-demand violation on the interaction side, and the tests cover the three decisive shapes: remote-beats-SSH-primary, SSH-only passthrough, and no-dial-on-hover.
