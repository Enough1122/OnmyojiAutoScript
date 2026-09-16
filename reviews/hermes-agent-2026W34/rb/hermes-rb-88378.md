> AI code review — automated review for reference; please use your judgment.

Right cure for a confusing crash-after-success: once the tree swaps, this process serves imports from two revisions at once, and any *first-time* post-swap import walks new files against old cached ancestors. Preloading the cleanup chains while disk still matches `sys.modules` keeps the whole process on one coherent revision, best-effort wrapping ensures it can never block the update itself, and the regression suite covers both paths plus the never-raises guarantee via a builtins.`__import__` interception. Points:

1. hermes_cli/update_cmd.py:_preload_post_update_imports (~878) — the function name is plural but the body preloads exactly one chain (`gateway.status`). The next post-update step that imports a different not-yet-loaded chain reintroduces #88371 for that step. Either enumerate every chain the post-swap cleanup uses today (with a comment inviting additions) or invert the design: have the cleanup steps import their dependencies *before* calling into them via a tiny `_import_for_post_swap(name)` wrapper that asserts pre-swap timing.
2. The structural guard's position check (`index(preload) < index(marker) or index < 500`) is clever but the fallback disjunct weakens it — a refactor moving the preload to line 400 of a much longer function still passes. Acceptable as tripwire; noting the looseness. (nit)
3. If the preload itself fails on the OLD tree (broken checkout mid-update-from-broken-state), the post-swap ImportError returns exactly as before — inherent limitation of best-effort preloading, worth one sentence in the docstring so nobody expects the fix to be unconditional. (nit)

No blocking issues found.
