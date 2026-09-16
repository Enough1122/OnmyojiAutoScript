> AI code review — automated review for reference; please use your judgment.

Right fix at the right chokepoint: all three command accessors now share one boundary-stripper covering whitespace + Cc/Cf (word joiners, BOM, LRM — exactly what mobile clients and copy/paste inject), and the tests pin both directions that matter: wrapped commands now detect, and `allow_gateway_control=False` still gates them so the stripping can't be used to smuggle control past the gate. Points:

1. Deliberate behavior widening worth stating in the PR body: messages that *look* like plain text in some clients (leading U+2060 + "/approve …") now execute as gateway commands where they previously fell through to the model. Auth layers are unchanged, but reviewers should know the command surface grew to include invisible-prefixed variants.
2. gateway/platforms/base.py:_is_command_boundary_char (~32) — U+200B (zero width space) is category Cf so it's covered; a tiny comment listing intended characters ("ZWSP/ZWNJ/BOM/LRM…") would help the next person extend it without consulting Unicode charts. (nit)
3. Interior invisibles are untouched by design (`/ne⁠w` stays non-command) — correct, since mid-word joiners shouldn't rewrite identity; one test pinning that would stop an over-eager future "normalize everywhere" refactor from changing it silently. (nit)
4. The manual two-pointer strip is fine; stdlib `.strip(chars)` can't express categories, so no simpler form exists — acknowledging the choice, no change needed. (nit)

No blocking issues found.
