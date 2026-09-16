> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): preserve wallpaper metadata for built-in skins". Well-built end to end: relative paths resolve beside the skin YAML before leaving the backend, the renderer refuses arbitrary remote sources (files go through the authenticated media path, inline must be data:image), built-in-named skins get wallpaper metadata WITHOUT adopting foreign palettes (nice subtlety, pinned by both unit and full Playwright e2e), and the legacy filler backdrop stays for non-wallpaper themes. Suggestions:

1. apps/desktop/src/components/Backdrop.tsx:66 (CSS injection surface) — `theme.backgroundOverlay` flows raw into `style={{ background: … }}`; a skin YAML (user-imported!) can set `background_overlay: url(https://evil.example/pixel.png)` — CSS url() fires an outbound request from the renderer, an exfil/beacon channel your own comment says you wanted closed ("keep the renderer from making arbitrary outbound requests") — validate overlay against color syntax (#rgb(a), #rrggbb(a), rgb()/hsl()) before applying, same treatment for `background_image_position`.

2. apps/shared/src/skin.ts:111 (dead configuration) — the backend accepts `http(s)://` wallpaper URLs but the renderer deliberately never renders them, so remote-wallpaper configs silently do nothing — either strip them with a load-time warning in skin_engine.py or document that only local/data images are supported.

3. hermes_cli/skin_engine.py:856 (scheme scope) — `file:` URLs pass through resolution untouched; verify `isFileMediaPath`/`resolveMediaDisplaySrc` actually handle that scheme AND scope readable paths (skins/home dirs) — otherwise a skin can point the desktop at any local file and have it rendered into the page.

4. apps/shared/src/skin.ts:112 (nit) — `'cover' | 'contain' | 'fill' | 'scale-down' | string` — the trailing `| string` erases the union's autocomplete/validation value entirely; keep the five valid literals and let the renderer fall back to cover on unknowns.

No blocking issues found — item 1 is the one I'd fix before shipping importable skins.
