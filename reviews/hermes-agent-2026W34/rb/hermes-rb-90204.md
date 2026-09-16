> AI code review — automated review for reference; please use your judgment.

Review of "feat(mcp): add screenpipe catalog entry". Clean catalog entry: exact version pin (with the transport.version mirror), telemetry explicitly disabled, a read-only default tool surface with mutation tools left to the install-time checklist, and honest loopback-only/auth-none documentation. Two suggestions:

1. optional-mcps/screenpipe/manifest.yaml:post_install (privacy salience) — this integration's entire premise is CONTINUOUS SCREEN AND MICROPHONE CAPTURE, which is a materially higher-sensitivity category than typical MCP servers; the post_install explains mechanics but never says "this records your screen and audio" — one plain sentence up front (plus a pointer to the vendor's retention/purge controls) would make sure installers opt in knowing exactly what starts running.

2. nit — `transport.version` duplicates the pinned specifiers arg; if the catalog schema treats them as independent, they can drift on the next bump PR — confirm which one is authoritative and drop or auto-check the other.
