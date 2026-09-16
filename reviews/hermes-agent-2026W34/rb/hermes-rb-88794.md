AI code review note for PR 88794:

Good docs addition answering a real recurring question, and notably candid about the boundary: it states plainly that a unified backend has ONE auth gate for all profiles, that "different profile" is organization rather than an access boundary between mutually-untrusted people, points at `--isolated` as the supported per-profile auth shape, and even links the open #76932 visibility gap with advice to check its status before relying on it. That last part is the kind of honesty that prevents bad security decisions.

No blocking issues found.