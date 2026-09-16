> AI code review — automated review for reference; please use your judgment.

Review of "feat: remote session attach (server + CLI + desktop)" (large, multi-surface; sampled desktop store/UI/tests and security greps). Strong delivery for a big feature: the attach-token lifecycle is handled end to end (pairing-code normalization, expiry tracked and enforced client-side, 401 mapped to "token expired — pair again" with stream teardown, unexpired-hydrate vs expired-discard tested), reconnecting state keeps detach/disconnect available, event rendering covers message/status/tool phases, and tests span unit, store, CLI, gateway API, and an e2e file. Docs get a dedicated page. Suggestions:

1. apps/desktop/src/store/remote-session.ts (token at rest) — the attach token persists in localStorage (`{host, port, token, expiresAt}`); any XSS or local malware read exfiltrates a credential that controls a REMOTE Hermes session until expiry — consider the existing native-auth bridge (OS keychain) for the token, or at minimum document the at-rest exposure in remote-session-attach.md alongside the expiry story.

2. Transport clarity — the pairing examples use raw host:port; please state explicitly in remote-session-attach.md whether the attach channel requires TLS (or authenticates equivalently) — a user pointing this at `http://` over the internet would be sending the bearer token in clear.

3. nit (recurring) — i18n adds en/ja/zh-hant/zh/types here but not ar; same completeness question as prior desktop PRs.
