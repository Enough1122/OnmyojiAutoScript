> AI code review — automated review for reference; please use your judgment.

Clean third-source addition that follows the established conventions exactly: read-only access, schema-verified docstring with the discovery date, wrapper/duplicate-row filtering (`turn.prompt`, injections, tasks), CoT `think` parts deliberately excluded, and the parser-registry refactor removes the growing conditional. The mtime fallback chain (updatedAt → wire stat) and session-id fallback (state.id → dir name) are both sensible. Points:

1. hermes_cli/foreign_sessions.py:`parse_kimi_session` (~340) — the origin filter is a **denylist** (`kind in ("injection", "task")` → skip). Any *future* Kimi origin kind (a new machine-generated row type) would be imported as user input by default. An allowlist (`if kind != "user": continue`) matches the stated intent ("typed user messages") and fails closed against protocol drift. If untyped rows are legitimately user input on some Kimi versions, keep the denylist but say so in a comment.
2. foreign_sessions.py:~365 — `tool.call` becomes a synthetic `("assistant", "[ran tool: name]")` row relying on `_merge_turns` to fold it into neighbors. Two adjacent calls with different names concatenate into one bracketed blob — check the merged rendering reads acceptably ("[ran tool: a] [ran tool: b]") rather than "[ran tool: ab]". One unit assertion on the two-call shape would pin whichever is intended.
3. foreign_sessions.py:`list_kimi_sessions` (~395) — `parse_kimi_session` runs once per wire file at listing time, then again inside `import_foreign_session`; harmless today (files are small) but worth remembering if Kimi sessions grow large — the listing path only needs turn_count + first line. (nit)
4. The glob `*/*/agents/main/wire.jsonl` hardcodes the `agents/main` layout; if Kimi ever ships subagent wires (`agents/<other>/`), they're silently invisible. The docstring pins protocol 1.5 — add the same caveat inline. (nit)

No blocking issues found.
