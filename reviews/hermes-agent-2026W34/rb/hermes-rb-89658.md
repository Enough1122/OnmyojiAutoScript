> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): keep lazy code highlighting from shifting the transcript". Root-cause fix with a first-class regression harness: the jitter came from the LazyShiki Suspense fallback (<code> with display:block + Streamdown's 0.9em prose reset) disagreeing with the highlighted DOM's typography; dropping `block` from the single-chunk fallback and pinning `.aui-shiki > code` to inherited font metrics makes both render paths share geometry, and the CSS comment documents exactly which reset it neutralizes. The e2e is a genuinely diagnostic MutationObserver layout probe — it captures fallback AND highlighted states, exercises the >200-line chunked path, attaches raw samples as an artifact, logs the deltas, and asserts per-block AND total heights within 1px rather than a vague "no big shift". The `replyText` mock-server option is additive and backwards compatible. One nit:

- styles.css — the selector hard-couples to Streamdown's `aui-md`/`aui-shiki` class names and its prose-reset behavior; the comment explains the dependency, but if those classes are library-owned consider also scoping a fallback rule under the chat container so an upstream rename degrades to the old jitter instead of silently unstyled code.

No blocking issues found.
