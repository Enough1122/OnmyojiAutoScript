> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Correct and well-targeted: Vertex/Gemini's OpenAI-compat surface flags thought summaries only via \`extra_content.google.thought\` (no \\<think>\\ tags on the wire), so tag-based scrubbing structurally couldn't catch them, and routing flagged deltas into \`_fire_reasoning_delta\` + \`reasoning_parts\` before content accumulation keeps summaries out of the visible reply. The dual read (attribute, then \`model_extra\` dict) covers pydantic v1/v2 shapes, the empty-\`reasoning_parts\` guard is handled, and the negative test proving \`thought_signature\`-only payloads don't hijack visibility is exactly the right companion.

Two edge questions:

- **agent/chat_completion_helpers.py:~4156 — a flagged chunk that *also* carries \`tool_calls\` bypasses routing entirely.** The guard requires \`not delta.tool_calls\`; on the real wire, vendors occasionally pack content/thought plus the first tool-call shard into one chunk, in which case the thought text would fall through to visible content again. Consider splitting behavior: route \`content\` to reasoning while letting the tool-call accumulation below proceed, instead of an all-or-nothing branch. A unit chunk with thought=True + content + one tool_call would pin it.

- **Non-streaming parity:** the fix lives in the streaming loop only. If the same Vertex surface can return a complete message whose content embeds thought summaries with the same \`extra_content\` marker (non-stream responses do carry per-part thought flags), those would still leak into \`message.content\`. Worth either handling in the assembly path or noting the limitation in the PR.

Nit: the detection now spans attribute access + \`model_extra\` fallback + nested shape checks inline; extracting an \`_is_gemini_thought_delta(delta) -> bool | None\` helper would keep the streaming loop readable as more vendors add flag variants.

No blocking issues found.