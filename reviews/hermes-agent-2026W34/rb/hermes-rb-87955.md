> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): scan every served profile's /loop wakeups, not just the launch profile's". Correct fix for a silent multi-profile failure: a gateway-wide watcher task pins `get_hermes_home()` to whichever profile was ambient at creation, so every OTHER profile's /loop never fired. Re-resolving the served set each tick and scanning each profile under its own `_profile_runtime_scope` — with fail-closed `_authorization_adapter` resolution so a secondary profile's loop fires through ITS bot rather than the default profile's adapter on a shared platform — also fixes the subtler wrong-bot-delivery hazard the old bare adapters lookup had. Suggestions:

1. nit — `warned_no_route` is keyed by sid alone but now spans profiles; if session ids aren't globally unique across profiles, one profile's warning suppresses another's — key by (profile, sid).

2. nit — per-tick work scales with served-profile count × loops every 15s; fine today, worth a cheap "profiles unchanged since last scan" fast path if multiplex usage grows.
