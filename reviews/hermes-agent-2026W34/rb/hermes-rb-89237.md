> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct narrowing of the bare-path walker: yielding only tokens that resolve to a **regular file** eliminates the false hard-blocks from directory assignments, heredoc fragments, and comment-shaped path strings, while the layered safety story stays intact (the cloud-placeholder branch upstream still fails closed for any *yielded* path). Equally important, the negative-control test proves the extension restriction didn't disarm the guard — a .sh that both assigns a path and invokes `hermes gateway restart` is still blocked via the direct body scan, and the generic walker test pins yield semantics including the no-extension real file. Findings below are minor:

1. tests/hermes_cli/test_gateway_restart_loop.py:766 — the canonical preflight regression test skips unless `/home/hermes/.hermes/scripts/tabjoy-e2e-preflight.sh` exists, so on every other machine (and in CI) it's a no-op. The third test covers the walker mechanics generically, but consider adding a portable tmp_path replica of the actual preflight body (`SRC=/tmp/tabjoy-e2e` + heredoc echoes, no lifecycle verbs) asserted through `check_gateway_lifecycle`, so the original incident can never silently regress in CI.
