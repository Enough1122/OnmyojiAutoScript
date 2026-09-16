> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct approach: probing `::1` with an ephemeral bind up front (instead of hard-requiring dual-stack bindability per port) means kernels/containers that expose `AF_INET6` but reject loopback binds can no longer veto every IPv4 candidate, and the mocked-socket test pins the exact reported scenario. The probe correctly wraps socket creation *and* bind, so EAFNOSUPPORT builds are covered too.

Nit (non-blocking): hermes_cli/browser_connect.py:241 — dropping `SO_REUSEADDR` from the probe is a second, unrelated behavior change riding along: ports sitting in TIME_WAIT (e.g. right after closing a CDP session) now count as in-use, so selection skips them where it previously reused them. Arguably safer (and on Windows it fixes REUSEADDR's permissive double-bind semantics), but it deserves its own line in the docstring/PR description so future readers don't mistake it for part of the IPv6 fix.

No blocking issues found.
