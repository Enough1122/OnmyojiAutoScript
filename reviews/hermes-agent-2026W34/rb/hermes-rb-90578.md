> AI code review — automated review; please use your judgment.

1. `gateway/run.py` (~4353–4360, ~4409–4412) — two hunks change tool_preview_max_len semantics (**0 previously fell back to 40; now it means unlimited**) and carry comments reading "Local patch 2026-08-20 (upstream treated 0 as falsy)" — why it matters: (a) this is unrelated to the PR's stated purpose (dedup counter placement), so reviewers and changelog readers won't find it; (b) it silently flips behavior for operators who already set 0 believing they'd get the default-40 cap; (c) "local patch" narration describes deployment history, not upstream reality — suggestion: split into its own PR, document 0 = unlimited in the config reference, and reword comments to describe behavior rather than patch provenance.

2. Test gap — _append_dedup_counter is a pure function with three distinct branches (insert-before-close-fence, replace-an-existing-counter-line, non-fenced suffix strip) and zero tests — why it matters: the backwards fence-scanning loop with its insertion index is exactly the kind of logic that regresses silently — suggestion: add four unit cases (fresh fenced, repeat on fenced, repeat on non-fenced, fenced block whose *content* contains a bare fence line).

3. Nit (~4125–4131): the in-fence (×N) marker becomes literal content of the rendered code block on clients that honor fences — an accepted trade-off given the Feishu close-fence analysis, but worth one docstring sentence saying so explicitly for future formatting changes.

The core fix itself is sound: appending (×N) outside a closing fence genuinely breaks the ^```\s*$ match on Feishu, and scanning backwards for the last bare fence while replacing any prior counter prevents unbounded stacking.

— reviewer-a · automated agent review (Hermes week-review)