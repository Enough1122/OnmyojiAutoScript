> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correctly layered fallback for the "is this named profile's gateway up" question: private runtime state wins first, then a live *root* gateway counts only when its explicit `served_profiles` list names the profile, and older records without that list defer to the same multiplex enablement switches startup uses. The guards are careful where they need to be (profile must be exactly one level under the profiles root, `default` excluded, id regex validated, everything fails closed through the outer except), and the three tests cover served / not-served / legacy-status-with-config paths including the allowlist-not-superset case.

Nit (non-blocking): hermes_cli/profiles.py:_gateway_multiplex_enabled — the env-var name and the YAML key/coercion rules for multiplex mode are now re-implemented here, duplicating whatever gateway startup does; if the startup side ever renames the env or accepts another spelling, this checker silently disagrees about whether the root gateway is shared. Import the canonical predicate from the gateway/config layer (or move this helper there) so "is multiplexing on" has one definition.
