> AI code review — automated review for reference; please use your judgment.

Good expansion area — Unicode tag/bidi detection and the supply-chain patterns are genuinely valuable. The main risk in a scanner PR is false-positive economics, and two of the new families have that problem:

- tools/skills_guard.py:381 — issue — `mcp_poison` fires HIGH on the bare substrings `mcp_servers`/`register_mcp`/`add_mcp_server` — why it matters — *every* MCP setup guide legitimately contains `mcp_servers:`; flagging documentation at "high" trains users to dismiss HIGH alerts, which is how real poison slips through — suggestion — require poisoning-shaped context (co-occurrence with an inbound URL, instruction-like imperative, or a write into another skill's directory), or demote to medium/info with the verify-your-source advice kept in the message.

- tools/skills_guard.py:385 — issue — `memory_poison` uses `memory.*(...write...)s*(` on one line, which flags any legitimate memory-API call (`memory_store.save(...)`) at HIGH — why it matters — same alert-fatigue economics; the OWASP ASI06 threat is about *content*, not the API name — suggestion — raise severity only when the write target/content came from tool output or user text (harder), else keep medium and lean on the existing unicode/obfuscation signals for escalation.

- tools/skills_guard.py:360 — issue — `sql_injection_concat` catches `"..." +` concatenation but not f-string interpolation (`execute(f"… {user_input}")`), which is the dominant vector in Python skill scripts — why it matters — the pattern gives partial coverage while implying SQL-injection checking — suggestion — add an `execute\s*\(\s*f['"]` variant (accepting some false positives given the scanner's advisory role).

- tools/skills_guard.py:367 — issue (verification) — confirm the compilation pipeline lowercases content before matching: `Shell(``/``SendKeys(`` are written in many casings and the VBA patterns are effectively case-sensitive as written — if content isn't normalized, half these patterns never fire; if it is, say so in a comment.

- tools/skills_guard.py:374 — nit — bidi coverage lists U+202A–E but omits the isolate set U+2066–U+2069 (LRI/RLI/FSI/PDI), which modern exploits prefer precisely because older scanners skip them; also none of the new families have positive/negative fixture tests — add at least one per family.

No blocking issues found — items 1–2 determine whether the new HIGH tier stays trustworthy.

— reviewer-b (automated review)
