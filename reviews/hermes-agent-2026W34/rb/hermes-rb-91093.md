> AI code review — automated review for reference; please use your judgment.

Solid feature slice across all four surfaces (DB+migration, CLI, swarm plumbing, desktop UI with four locales), and the migration story is right: legacy rows stay NULL with an amber chip plus one-click linking instead of a destructive backfill. Items:

- apps/desktop/src/plugins/kanban/board.tsx:148 — issue — `beadUrl` hardcodes `http://127.0.0.1:8767/` and strips *only* the `worktracker-` prefix, while the backend's `VALID_BEAD_RE` deliberately accepts any `<tracker>-<digits>` scheme — why it matters — the first card created with `jira-123` or `linear-456` renders a link to `127.0.0.1:8767/123`, i.e., the wrong tracker page presented as authoritative status truth, which is precisely what this field exists to be — suggestion — either restrict the frontend to the estate tracker (mirror `worktracker-` in the shared validator so both layers agree) or derive the base URL from a config key / prefix→base map instead of a literal.

- hermes_cli/kanban_db.py:3327 — issue — multi-parent creation inherits the *first* parent that happens to carry a bead, silently, even when parents reference different beads — why it matters — a child spanning two upstream items gets attributed to whichever parent iterated first; ordering-dependent data attribution is the kind of quiet wrongness that surfaces months later during audits — suggestion — when parents carry conflicting non-null beads, either require an explicit `--bead` (error listing both candidates) or pick deterministically *and* append a task note recording the ambiguity.

- hermes_cli/kanban_db.py / plugins/kanban dashboard — issue (verification) — two things I can't confirm from the visible hunks: (a) does the dashboard PATCH path catch `set_bead_id`'s ValueError and map it to a 4xx rather than a 500 (invalid ids arrive from the new inline editor)? (b) do dedicated tests exist for the new failure modes themselves — create-without-bead refusal, parent inheritance, invalid-shape rejection, and legacy-row NULL acceptance — given ~60 files of mechanical test edits, it's easy for the *new* assertions to have been forgotten.

- hermes_cli/kanban_db.py:3203 — nit — `set_bead_id` appends a `bead_set` event even when the value is unchanged; repeated opens/saves in the drawer will spam the event log — skip the write (and event) when `current == new`.

No blocking issues found — item 1 should be settled before merge since it produces confidently-wrong links.

— reviewer-b (automated review)
