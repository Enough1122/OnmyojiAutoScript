> AI code review — automated review for reference; please use your judgment.

Well-shaped extraction: `SessionSurfaceChat` reuses the native transcript/composer tree via a surface-scoped `SessionView` (per-surface turn clock included, mirroring the tile refactor), routes every request through the *owning profile's* socket without foregrounding that profile, namespaces the composer scope (``surface:<profile>:<id>``) so drafts can't cross-contaminate the primary chat, and opts surfaces out of focus-stealing via an explicit `focusOnSessionChange={false}` that the main chat keeps defaulting to true. The test updates threading `focusKey` through the harness pin the new behavior at the hook level too. Points:

1. apps/desktop/src/app/chat/session-surface-chat.tsx:~57 — `requestSurfaceGateway` is forced through ```as unknown as GatewayRequester```. That double cast suppresses exactly the check that would catch GatewayRequester growing methods this surface shim doesn't implement. Define a narrow structural type (e.g. `SurfaceGatewayRequester = { request }`) or make the shim genuinely satisfy the interface.
2. `buildSessionSurfaceView` constructs a fresh atom set per identity triple inside `useMemo` — correct for isolated surfaces, but two mounts of the same stored session would hold *separate* message arrays until a refresh reconciles them. Fine if surfaces are single-instance by construction; one comment stating that invariant would help.
3. The model menu receives `gateway={gateway || undefined}` while requests route through the surface requester — confirm the menu's own reads tolerate a non-active gateway object (the profile-scoped pattern suggests yes). (nit)
4. Reusing `useSessionTileActions` for surface actions is the right dedup — tiles and plugin surfaces now share submit/steer/cancel semantics by construction. (positive)

No blocking issues found.
