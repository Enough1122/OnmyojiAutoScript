> AI code review — automated review for reference; please use your judgment.

Good fix with the right conservatism: unwrapping keyed on the `mcp__` prefix plus shape-checked payloads means every non-MCP JSON tool output stays byte-verbatim (pinned by `test_non_mcp_json_envelope_remains_verbatim`), and threading the *real* tool name through `enforce_turn_budget` so budget-path spills get the same treatment is the subtle half that's usually missed.

- tools/tool_result_storage.py:244 — issue — the unwrap also fires when an MCP tool deliberately returns a JSON envelope as its *model-facing payload*: `{"result": "{\"rows\": [...]}", ...}` persists the inner string raw while the inline preview switches from showing the whole envelope to the inner text; any consumer that diffs inline vs persisted (or re-reads spill files expecting the historical verbatim envelope) sees a format change — why it matters — spill files are recovery artifacts; a silent schema change to them can break ad-hoc scripts and future re-ingest features — suggestion — note the format change in the docstring/changelog, or version the spill sidecar (e.g., `.txt` vs `.envelope.txt`) if any code reads these back today.

- tests/tools/test_tool_result_storage.py:297 — nit (coverage) — no case for an `mcp__`-prefixed tool whose body is valid JSON but matches neither shape (`{"other": 1}`) — the fall-through-to-verbatim branch for MCP-named tools is what guards against over-eager unwrapping; five lines to pin.

No blocking issues found.

— reviewer-b (automated review)
