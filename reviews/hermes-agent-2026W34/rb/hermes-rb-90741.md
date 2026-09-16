> AI code review — automated review for reference; please use your judgment.

Review of "fix(sessions): keep tool arguments and output when importing foreign sessions (#90433)". Good fix for a real fidelity problem: tool activity was being flattened to `[ran tool: Bash]` markers, losing exactly what makes coding-agent transcripts useful. The implementation is careful — arg digests prioritize the signal-bearing keys, results handle string/block-list/dict shapes, non-printable payloads collapse to a sized placeholder, truncation markers report original lengths, and Codex outputs land on the user side to preserve alternation. Suggestions:

1. hermes_cli/foreign_sessions.py:106 (injection surface grows) — imported tool OUTPUT now enters the local transcript as USER-role text, up to 2000 chars per result; a foreign session's tool output is attacker-influencable data (web fetches, command output), and rendering it as plain user content gives prompt-injection payloads direct conversational standing — consider wrapping it in an explicit provenance marker (`[imported tool output — data, not instruction]`) so downstream agents weight it as quoted material.

2. hermes_cli/foreign_sessions.py:225 (deliberate reversal?) — the old code skipped tool_result blocks with the comment "not typed input"; this change makes user-role turns that contain NO human-typed text at all — confirm nothing downstream assumes user messages are human-authored (title guessing, session previews/search ranking, turn statistics), since those now ingest tool noise.

3. hermes_cli/foreign_sessions.py:121 (nit, binary probe) — `_is_mostly_printable` samples only the first 4096 chars, so a text-headed/binary-tailed payload renders as text; fine as a cheap heuristic, but one comment saying the tail is unexamined would preempt bug reports about garbled imports.

4. tests/hermes_cli/test_foreign_sessions.py (coverage suggestion) — add one case asserting the exact truncation-marker format past `_TOOL_RESULT_MAX` (the "N more chars" arithmetic is easy to regress silently).

No blocking issues found.
