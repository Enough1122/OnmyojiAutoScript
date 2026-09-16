> AI code review — automated review for reference; please use your judgment.

Right fix in the right direction: JID-vs-bare-ID mismatch fails closed (an admin just loses access, nothing is over-granted), and normalizing before `policy.is_admin` is the minimal change. Two small things:

- gateway/slash_commands.py:1110 — issue — the normalization is patched into this one call site, wrapped in `except Exception: pass`; if the helper's import or signature ever drifts, every WhatsApp admin silently stops matching and there is no log line anywhere explaining why — why it matters — silent auth-degradation is the worst kind to diagnose after a refactor — suggestion — add `logger.debug("whatsapp uid normalization failed: %s", exc)`, and more importantly consider hoisting the JID→bare-ID normalization into `policy_for_source`/`is_admin` itself so *every* admin/allowlist comparison (this one plus any future slash command) benefits instead of each site remembering to normalize.

- gateway/slash_commands.py:1108 — nit (verification) — the guard reads `source.platform.value`, which assumes an enum; confirm WhatsApp SessionSources always carry `Platform.WHATSAPP` and never a plain string, or accept both spellings.

No blocking issues found.

— reviewer-b (automated review)
