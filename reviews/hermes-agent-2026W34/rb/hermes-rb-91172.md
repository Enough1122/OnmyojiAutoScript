> AI code review — automated review for reference; please use your judgment.

Correct diagnosis and minimal fix: the adapter object (and its callback wrappers) is now identity-stable across renders, so the keyed-by-identity effect stops tearing down/reinstalling the runtime and fanning notifications on every unrelated re-render. The dependency list is complete (`busy`, `onCancel`, `onEdit`, `onReload`, `onThreadMessagesChange`, `runtimeMessageRepository`), so there's no stale-closure exposure, and behavior is unchanged whenever an actual input changes.

No blocking issues found.

Nit (`apps/desktop/src/app/chat/index.tsx:~303–320`): because `isRunning: busy` lives inside the memoized object, every running↔idle flip still re-installs the adapter once per turn; if `useIncrementalExternalStoreRuntime` accepts `isRunning` separately (many assistant-ui adapters do) or can read it via a getter, hoisting it out would make the adapter fully stable for the session. A regression test that renders through a parent re-render storm and asserts the adapter effect fires once (or N-inputs-times only) would lock the fix in.

— reviewer-a · automated agent review (Hermes week-review)
