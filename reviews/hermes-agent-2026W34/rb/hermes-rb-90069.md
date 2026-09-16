> AI code review — automated review; please use your judgment.

Well-executed exemption with the correct failure posture throughout: every parse doubt (no destination, wrapper muddles, bare /etc/hosts-style aliases, localhost/loopback/[::1] targets) returns `None` and keeps the plain-regex block, masking only ever *allows* what the regex would have blocked, and the test matrix pins both directions including the important chained-command case (`… && systemctl restart` outside the payload must still die).

1. `cron/lifecycle_guard.py:~186–189` — the local-destination set covers only literal `localhost/127.0.0.1/::1/0.0.0.0`; a dotted name that resolves to **this machine** (````ssh mybox.lan systemctl restart hermes-gateway````) passes the non-local check because it contains a dot — why it matters: that reopens the exact SIGTERM foot-gun for single-host users whose hostname happens to be dotted, arguably the most common home-server setup — suggestion: document the limitation explicitly next to `_SSH_LOCAL_DESTINATIONS`, or optionally resolve the destination once via `socket.getaddrinfo` and compare against local addresses (with a short cache) before exempting.

2. Nit (`:~180–185`): `_SSH_LONG_WITH_VALUE` lists options that aren't OpenSSH client flags at all (`--bind-address`, `--remote-user`, `--user`, …) — they look copied from another tool's option table. Harmless today only because unknown long options already consume one token conservatively; pruning the set to real ssh long forms (or deleting it) would remove confusing dead knowledge.

3. Nit: the wrapper-skipping loop treats `sshpass -e` as flag+value, swallowing the following `ssh` token — which then correctly fails the executable check and stays blocked (safe), but a one-line comment noting "−e degrades to blocked by design" would prevent someone from 'fixing' it into an unsafe fast-path later.

— reviewer-a · automated agent review (Hermes week-review)
