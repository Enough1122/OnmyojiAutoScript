> AI code review — automated review; please use your judgment.

Entry is well-formed and consistent with its siblings: all required fields present, `ref` pinned to a full commit SHA (good supply-chain hygiene for an installable index), tags are reasonable, and `api_version`/`added_at` match convention.

No blocking issues found.

Nit (`hermes_cli/data/plugin_index.json`): this change also **removes the file's trailing newline** (the closing brace now ends without `\n`) — harmless functionally, but it makes every future JSON edit produce a no-newline-at-eof diff artifact and differs from the rest of the repo's data files; please restore the trailing byte.

— reviewer-a · automated agent review (Hermes week-review)
