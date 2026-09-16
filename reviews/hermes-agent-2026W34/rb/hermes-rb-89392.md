> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Clean compatibility fix: endpoints that expose the context window as a flattened camelCase key (capabilities.contextWindow arriving as "contextwindow" after normalization) previously fell through every known alias and lost their true window; adding the concatenated form to _CONTEXT_LENGTH_KEYS covers them without touching resolution order. The regression test exercises the exact nested shape end-to-end and asserts connection cleanup too.

No blocking issues found.