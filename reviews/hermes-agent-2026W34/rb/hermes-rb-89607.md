> AI code review — automated review for reference; please use your judgment.

Review of "feat(agent): configure intent-ack vocabulary for multilingual models". Clean extension point: additive literal phrase lists per marker class, normalization to casefold at the detector boundary (with the built-in path upgraded from lower() to casefold() for better Unicode handling — a subtle improvement beyond the feature itself), malformed user config contributing nothing instead of breaking init, tests covering real Chinese phrasing plus the Codex workspace scope and the malformed shape, and a docs section that states the substring/additive/non-regex semantics precisely. One nit:

- the docs should warn that custom markers match as UNBOUNDED substrings — the built-in English future-ack pattern uses \b word boundaries, so a user-contributed alphabetic marker like "will do" is fine, but something short like "ok" would match inside unrelated words ("broker", "token") and cause spurious continuations; one sentence recommending distinctive multi-word phrases would prevent the most likely misconfiguration.

No blocking issues found.
