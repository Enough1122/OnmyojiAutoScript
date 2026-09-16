> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-bounded widening: only the two documented forum kinds join dispatch, the WebSocket REQ filter is updated in lockstep (so the live path actually receives what the gate would accept — the test asserting filter ⊇ dispatch set catches the classic half-fix), undocumented stream kinds are explicitly kept out until their semantics are known, and — best of all — the DM-reclassification check deliberately stays kind-9-only with a test pinning that a p-tagged forum post cannot bypass mention gating. Findings below are minor:

1. plugins/platforms/buzz/adapter.py:_handle_event — kind 45003 replies carry their thread linkage in Nostr tag conventions (`e`/`root` markers referencing the 45001 root), but dispatch flattens them to bare content, so the agent sees "re: something" out of context and can't tell which forum post a comment belongs to. Consider extracting the referenced root/reply ids from tags into the dispatch metadata now that these events flow at all — otherwise every forum thread reads to the model like disconnected one-off questions.
