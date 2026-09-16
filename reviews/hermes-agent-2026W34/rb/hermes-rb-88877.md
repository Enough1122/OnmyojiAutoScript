> AI code review — automated review; please use your judgment.

Well-bounded fix: `isWorkspaceLiveReloadUrl` implements a proper local-origin allowlist (loopback incl. all of 127/8 and `*.localhost`, `.local` mDNS, RFC1918 ranges, link-local) with careful host normalization (case, IPv6 brackets, trailing dot), and the negative matrix catches the classic smuggles — `user@evil.test` userinfo, `172.32`/`11.x` just outside the ranges, invalid octets. The pane now reloads only when the *current* webview URL still satisfies that predicate, so a redirect from the dev server to a public origin correctly opts out of further workspace-triggered reloads, and both behaviors have tests. The effect's dependency list gained `currentUrl` as needed.

No blocking issues found.

Nit (`apps/desktop/src/lib/local-preview.ts` `isLocalOrPrivateIpv4`): IPv6 unique-local addresses (`fc00::/7`, common for self-hosted dev on modern stacks) aren't recognized, so a dev server served on e.g. `http://[fd00::1]:3000` would lose live reload under this policy; adding a ULA check would keep parity with the IPv4 private ranges.

— reviewer-a · automated agent review (Hermes week-review)
