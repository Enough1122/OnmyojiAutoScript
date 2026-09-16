> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right fix for a subtle staleness window: between-turn restoration never runs during a many-tool-call turn, so an expired primary cooldown left the rest of the turn on the fallback. The iteration-boundary re-check closes that, and — the part that matters most — syncing `active_system_prompt` from `_cached_system_prompt` prevents calling the restored primary with the fallback's system-prompt identity. The three behavioral tests are clean; one nit:

1. tests/agent/test_mid_turn_primary_restore.py:test_outer_iteration_probes_before_building_the_next_request — the AST-based placement assertion is clever but brittle: any refactor that renames the helper or splits the loop condition breaks the test for non-behavioral reasons. Consider softening it to a runtime observable (e.g. a restore spy whose call order relative to the first redirected request is asserted through the agent), so the *ordering* stays pinned without coupling to source structure.
