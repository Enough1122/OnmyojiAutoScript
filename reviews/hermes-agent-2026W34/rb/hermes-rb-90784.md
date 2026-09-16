> AI code review — automated review for reference; please use your judgment.

1. plugins/memory/mem0/__init__.py:359 — the new fallback scopes memory by raw gateway_session_key. Why it matters: if any client class mints fresh session keys per connection or per conversation rather than per human (API wrappers commonly do), each new key silently starts an empty memory store — fragmentation that looks to users like 'the agent forgot me', with no signal tying the buckets together. Suggestion: document the stability contract the fallback assumes (session_key must be stable per human for API platforms), and consider normalizing known-volatile segments before use.

2. Same line — the full internal session key ('agent:main:webui:dm:user-7') now leaves the process as the Mem0 user_id on hosted Mem0. Why it matters: it leaks internal topology (profile, platform, chat/thread shape) to a third party where previously only bare platform-native ids went out. Probably acceptable, but a cheap hardening is hashing the key (sha256, hex) for the wire while keeping the readable form in logs — same isolation, less disclosure.

The precedence tests are exactly right: explicit-config beats native id beats session key beats default, API clients get distinct stores, and the CLI-without-identity case still lands on hermes-user instead of accidentally inheriting a session key.
