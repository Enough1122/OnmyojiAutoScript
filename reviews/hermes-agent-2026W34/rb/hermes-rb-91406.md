> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Small and correct: `_resolve_json_type` recursively lowers array/item schemas into real Python generics (`list[str]`, `list[list[int]]`, ...), keeps the legacy behaviors intact (items-less arrays still map via `_JSON_TO_PY`, unknown types stay `Any`), and the single call site swap means the MCP server now emits schemas whose `items` survive the signature→schema round-trip instead of degrading every array to a bare `list`.

Nit (non-blocking): agent/transports/hermes_tools_mcp_server.py:68 — the recursion is unbounded, so a tool registered with a pathologically deep nested-array schema (hand-written config, or a future generator bug) raises RecursionError while building signatures and takes down tool listing rather than degrading. A cheap depth counter that falls back to plain `list` beyond ~16 levels keeps the improvement while staying fail-open. Cosmetic sibling: the return annotation is `-> type`, but `list[str]`/`dict` results are typing generics, not classes — `-> Any` would be honest.
