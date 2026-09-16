> AI code review — automated review for reference; please use your judgment.

Textbook dependency-hygiene fix: both packages are genuinely imported directly by production code (`agent/markdown_tables.py:35` for wcwidth, `tools/mcp_tool.py:5027/:5061` for portalocker), the win32 marker on portalocker mirrors the established `concurrent-log-handler` precedent and matches its actual conditional usage (POSIX takes the fcntl branch), versions are pinned to the house standard, and all three `uv.lock` sections (dependencies/requires-dist/package table) were regenerated consistently rather than hand-patched.

No blocking issues found.

Nit: worth a quick pass over the other consumers of the dependency set — the Nix derivation and any Dockerfile that install from `uv.lock` will pick these up automatically, but if any packaging surface maintains a hand-written requirement list (snapcraft, winget manifest, docs' manual-install instructions), those need the same two entries or a fresh install of that artifact regresses exactly the CJK padding and Windows file-locking behavior this PR fixes.

— Reviewed by Hermes AI reviewer (reviewer-f2)
