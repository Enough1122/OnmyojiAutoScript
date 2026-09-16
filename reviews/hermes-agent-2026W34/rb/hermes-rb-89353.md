> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Correct React fix: `event.currentTarget` is nulled once the synthetic event is released, so reading it inside the setState updater callback races the pool - hoisting `const value = event.currentTarget.value` before the updater is the canonical pattern. The inline comment explains why, which matters because the next person to "simplify" it back will reintroduce a flaky empty-field bug that only reproduces on slower machines.

Nit: the sibling env-var Input blocks in the same file (and the mcp.json editor form) likely share this shape; a quick grep for `event.currentTarget.value` inside updater callbacks across skills/mcp-tab.tsx would catch the remaining instances in the same pass.