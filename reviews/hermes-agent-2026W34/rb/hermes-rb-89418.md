> AI code review — automated review for reference; please use your judgment.

The provenance-tail convention itself is well designed — concrete-premise ALLOW/REJECT pairs, honest date rules (never backfill), and an explicit scope disclaimer distinguishing it from #81015's changelog. Two concerns about what the rewrite *removed*:

- agent/prompt_builder.py:186 — issue — the old block's routing rule "**Procedures and workflows belong in skills, not memory**" is gone entirely; the new text keeps only the anti-imperative clause — why it matters — that sentence was doing double duty: it redirected step-by-step content away from a memory store that fills and decays, into artifacts that don't; provenance tails make bad entries *traceable* but don't stop procedural drift into MEMORY — suggestion — keep one line of it alongside the new convention ("Multi-step procedures belong in skills; memory holds facts and their premises").

- agent/prompt_builder.py:183 — issue (cost) — this grows MEMORY_GUIDANCE by ~40 lines (~450 tokens) of standing per-turn prompt for every agent, forever — why it matters — the convention's value depends on models actually emitting tails, which a wall of ALLOW/REJECT prose may not achieve proportionally to its cost — suggestion — consider compressing the four examples to two and moving the full policy to the skill-authoring docs; also confirm no existing test asserts the removed `'Always respond concisely' ✗` example strings.

No blocking issues found — item 1 is the substantive one.

— reviewer-b (automated review)
