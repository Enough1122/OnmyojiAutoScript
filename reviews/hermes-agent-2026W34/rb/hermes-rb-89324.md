AI code review note for PR 89324:

Clean closure of the silent-drop path: when the #68539 fence blocks recovery because the peer's latest durable row is an intentional session_reset boundary, the store now recovers that boundary and flags was_auto_reset (with reason/activity/prev id) so the user still sees the automatic-reset notice instead of an unexplained fresh session. The guards are right - only end_reason == session_reset qualifies (explicit /new boundaries never claim an auto reset), policy mode != none is required, lookup failures degrade to the old behavior via the callable probe - and all three polarities plus the new_command/mode-none negatives are pinned by tests.

Tiny nit: auto_reset_reason maps anything non-"daily" to "idle"; if a third policy mode ever appears it will silently report as idle - a comment on the mapping would suffice.

No blocking issues found.