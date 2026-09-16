> AI code review — automated review for reference; please use your judgment.

Catalog-format compliant addition: the `ref` field pins an exact commit of the external repo (good supply-chain hygiene), capabilities are declared (`tools` + `skills`), and the entry follows the existing schema shape including the `generated_at` bump. Points:

1. Since presence in this index *is* the approval signal, the merge decision rests on claims that can't be verified from this diff: "Lean-checked formal-bounded lanes", "certified composed integral", "34 typed tools". Before merging, a maintainer should spot-check the pinned ref — do the Lean artifacts/admitted snapshots actually exist there, and does the tool count match? A one-line verification note in the PR would document that gate was performed.
2. The description's self-assessment language ("statuses pass through verbatim and never inflate") is promotional rather than descriptive; consider toning it to what the plugin does. Catalog descriptions are user-facing. (nit)
3. `capabilities` includes `skills` — confirm the repo's skills surface was reviewed at the same rigor as the tools, since skills execute prompts. (nit)

No blocking issues found beyond the human verification ask in item 1.
