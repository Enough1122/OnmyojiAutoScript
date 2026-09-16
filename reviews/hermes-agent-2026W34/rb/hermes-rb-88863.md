> AI code review — automated review for reference; please use your judgment.

Complete vertical slice: sanitized suggested name at the IPC boundary (Windows-invalid chars, control characters, guaranteed extension), payload-shape change mirrored through preload + `global.d.ts`, the semantic name threaded from markdown images and generated-image results down to both save paths, and helper tests pinning the data-URL-with-preferred-name case that motivated it. Items:

- apps/desktop/electron/main.ts:5326 — nit — `safeSuggestedImageName` caps nothing: a 300-character alt/model-derived name passes sanitization verbatim and can exceed filesystem filename limits (255 bytes, worse on some network mounts), silently failing the save — suggestion — truncate the stem to ~120 chars before appending the extension; while there, consider excluding Windows reserved device names (CON, NUL, …) since the sanitizer is already Windows-aware.

No blocking issues found.

— reviewer-b (automated review)
