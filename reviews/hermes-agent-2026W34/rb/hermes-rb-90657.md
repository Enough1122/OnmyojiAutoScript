> AI code review — automated review for reference; please use your judgment.

Right fix with the right failure semantics: an unavailable preview pane should answer `text: ""` immediately rather than letting the requesting tool burn its full 30s timeout, and the `.then(answer, () => answer(null))` shape keeps one response path so the request can't double-answer. Notably, unlike some sibling rejection-handler fixes, this test drives the *real* `handleDesktopBridgeEvent` rather than an inline copy — good.

1. desktop-bridge.ts:~50 — if `$gateway.get()` returns undefined/null at answer time (gateway dropped mid-read), `answer` becomes a no-op and the requesting side still stalls its full timeout. Pre-existing shape, but since this PR's whole point is "never stall the tool", consider a fallback channel or at least a debug log when no gateway is available to answer through. (nit)
2. The reject branch intentionally discards the error object; a `console.debug` of it would help distinguish "pane closed" from "webview read broke" when diagnosing why agents report empty previews. (nit)

No blocking issues found.
