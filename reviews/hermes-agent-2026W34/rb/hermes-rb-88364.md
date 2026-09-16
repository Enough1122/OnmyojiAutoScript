> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right replacement of a fragile pattern: temporarily nulling `agent._session_db` around `_compress_context` mutated live agent state mid-operation and depended on a finally-restore for correctness; the declarative `compression_in_place = True` stamp at agent construction expresses the actual requirement (ACP clients own the stable session id) and lets the compressor do the right thing internally — including archiving pre-compaction messages with the `compacted` flag rather than losing them. The restart-survival test is the strong one: it verifies the durable contract across a fresh SessionDB/SessionManager (summary-only history, originals archived + flagged), not just the in-memory call.
