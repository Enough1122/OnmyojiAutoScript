> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Important correctness layer for multi-profile desktops: stored-session ids can collide across profiles, so giving every pane/tile an owner (`profile` on PaneMirror, `payload.profile` through drag-open) and resolving visibility through `findSessionForProfile(sessions, id, foregroundProfile)` fixes tabs being titled/resumed against another profile's same-id row. The readiness gate that also honors the *pending* swap target (scope flips the moment the rail is clicked, before the gateway settles) is the subtle part, and both the same-id collision and swap-timing cases are directly tested. Findings below are minor:

1. apps/desktop/src/app/chat/session-tile.tsx:257 — `profileReady` requires `tileProfile === normalizeProfileKey(activeGatewayProfile)`; on a cold boot before any gateway profile is resolved (empty string), normalize presumably yields `` and no unlisted tab will ever promote to listed until the first profile lands. If that's intended (no resume before connect), fine — but a comment or a test for the cold-boot shape would keep it from reading as a bug later.

2. Scope note — at 24 files this touches drag, mirror, header, composer directives, and wiring beyond what fits a single review pass; I focused on the ownership-resolution core. The pieces I sampled are consistent, but the breadth itself argues for landing behind the feature flag/scope you have for the profile-scope rollout.
