> AI code review — automated review for reference; please use your judgment.

Well-designed contract overall: `model_fields_set` correctly distinguishes "omitted = leave alone" from "explicit null = clear", validation reuses `parse_reasoning_effort` instead of a second allowlist, the 400 message enumerates accepted values, and the UI's `'__inherit__'` sentinel maps to explicit-null at apply time with the draft pre-filled from the live slot. Points:

1. hermes_cli/web_server.py:~7475 — `task == "__reset__"` returns **before** the per-slot loop, so a request carrying both `task="__reset__"` and `reasoning_effort` silently ignores the effort field while reporting `{"ok": true}`. Either 400 on that combination (my preference — it's ambiguous intent) or honor it across all slots; silent acceptance invites API clients to think they cleared something they didn't.
2. web_models.py:~131 — `provider`/`model` became Optional to enable reasoning-only updates, but the only new guard (`not provider and not reasoning_effort_set`) lives in the *auxiliary* branch. Confirm the `scope="main"` path tolerates `provider=None`: previously a missing provider was a 422 at the pydantic boundary, now it flows through as `None` into the main-slot application logic. One explicit 400 for `scope="main" and not provider` would preserve the old contract exactly.
3. web_server.py:~7522 — when `reasoning_effort_set` is true but `provider` is falsy, the slot dict gets its effort written even if the slot has no provider/model yet (fresh slot = `{}`). That's arguably fine (pre-configure before first assignment), just confirm the auxiliary resolver's behavior for a slot with `reasoning_effort` but empty provider/model is defined rather than accidental. (nit)
4. model-settings.tsx — the `__inherit__` sentinel is spelled in three places (initial state, apply mapping, SelectItem); export it as a named constant next to `REASONING_EFFORT_VALUES` so a rename can't strand one site. (nit)
5. The test asserting DOM order (reasoning select precedes model select) via compareDocumentPosition is a nice touch for a layout-intent regression. (positive)

No blocking issues found.
