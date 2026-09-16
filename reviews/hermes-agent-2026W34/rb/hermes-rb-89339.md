AI code review note for PR 89339:

Right fix at the right layer: the bare-domain base_url is a classic silent-404 (transports append their own API path, so both a missing and a doubled /v1 fail), and catching it at config-normalization time with a warn-once-per-provider, direction-neutral message beats trying to guess the transport later. Placeholder/template URLs are sensibly exempt (the path may come from expansion), and all three behaviors - bare warns, path present silent, template exempt - are pinned by tests.

Two small notes:
- Confirm `re` is imported at hermes_cli/config.py module scope (the new re.search is the first use visible in this diff); if it was only imported lazily elsewhere this would raise at load.
- Nit: the warning text embeds two spaces ("and a doubled '/v1' 404"); trivial, but log-matching greps will trip on it.

No blocking issues found.