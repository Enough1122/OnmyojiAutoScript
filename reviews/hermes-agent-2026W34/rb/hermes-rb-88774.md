> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Important fail-open-to-fail-closed conversion: a broken or unimportable website blocklist previously returned None (allow) - meaning a config typo or module failure silently disabled web enforcement; now both failure shapes return a structured policy-unavailable block at every pre-navigation call site (evaluate_url_safety AND browser_navigate, both tested through a simulated import failure), while operator-disabled (enabled: false with valid config) remains a distinct, explicitly-logged allow so the two states are never confused. Deleting the old fail-open test and replacing it with its fail-closed inverse is exactly the right way to flip this contract.

Nit: consider surfacing the policy-unavailable block in whatever health/diagnostics surface exists (doctor or gateway status) - operators running with a malformed blocklist should learn about it somewhere louder than individual navigation refusals.

No blocking issues found.