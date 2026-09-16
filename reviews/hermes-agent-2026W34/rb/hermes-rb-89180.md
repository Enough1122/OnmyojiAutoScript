> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean fix for notification flooding with the right single-source discipline: the refresh wording moves into `SESSION_TURN_LEASE_WAIT_REFRESH_STATUS_TEMPLATE` and the gateway *derives* its matcher from that same constant (never re-inlining the prose — explicitly called out as the #69550 convention), so emitter and suppressor can't drift. Suppression keys on real adapter capability (`send_or_update_status` present) rather than a platform name list, the initial notice and lease-timeout warning are provably immune by wording difference, and the five tests cover suppressed/delivered/initial/timeout/unrelated shapes including a "refresh survives the noise filter first" assertion.
