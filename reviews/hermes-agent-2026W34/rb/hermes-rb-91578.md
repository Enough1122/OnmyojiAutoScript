> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right architecture for #91569: declarative allow-listing with fail-closed parsing, severity kept on every undeclared path, and a solid negative-test matrix. One real bypass plus hardening notes:

- **tools/skills_guard.py:~1176 (_URL_HOST_RE) + ~1249 (scope_hosts) — userinfo URLs defeat the host check, so the exemption can leak credentials.** The regex grabs whatever follows the scheme up to a non-host char: in a URL like https://probe.example@evil.com/collect it extracts probe.example while the connection actually goes to evil.com. A malicious skill declares PROBE_API_KEY with destination [probe.example], then sends the bearer token to https://probe.example@evil.com/x — the issubset check passes, the finding downgrades to low [declared], install is allowed, and the credential lands on the attacker host. Suggestion: extract hosts via urllib.parse.urlsplit per URL (use .hostname, which excludes userinfo) instead of running findall over raw source lines, and add the userinfo variant as a regression test. This is the one item I would treat as blocking for a security scanner.

- **skills_guard.py:~1175 (_SECRET_NAME_RE) — uppercase-only secret names silently miss common conventions.** Declarations like openai_api_key or hf_token can never match the pattern, so authors following lowercase env styles get zero exemptions and no diagnostics. Either normalize case on both sides, or validate declarations at load time and warn when a declared name can never match.

- **Matching semantics are implicit: exact-host, port-blind.** Declared r.jina.ai does not cover api.r.jina.ai (fails closed — surprising but safe), while probe.example:8443 IS covered because the regex drops the port. Both directions belong in the author-facing docs/comment: authors will reason about this like an origin allow-list, and it isn't one.

- **skills_guard.py:~1247 — the plus-or-minus-3-line window collects hosts from comments and unrelated strings too.** Any URL mentioned anywhere in scope joins the host set; that only ever makes exemptions harder (safe direction), but it produces confusing outcomes when e.g. a documentation link sits inside the window. Worth a comment acknowledging the conservatism.

- **Frontmatter parser edges (~1195-1200):** a multi-line value containing a stray closing-dashes line truncates parsing into silent empty-map (fail closed — acceptable); duplicate secret keys resolve last-wins silently. Consider warning on either instead of pure silence, since authors will believe coverage exists.

- **tests/tools/test_skills_guard.py — add the adversarial cases:** the userinfo bypass above, a mixed scope (one declared request + one undeclared request in the same function -> must stay dangerous), subdomain and port variants pinning the chosen semantics, and lowercase secret declarations.

Nit: tools/skills_guard.py:~1240 — the 3-line window deserves a named constant (e.g. _NON_PY_SCOPE_LINES) next to the pattern-ID set, so tuning one does not require hunting for the other.