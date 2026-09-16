> AI code review — automated review for reference; please use your judgment.

Complete feature slice: config → defaults → agent_init → compressor → both prompt paths → gateway hot-reload watcher → example yaml → website docs. The two details that usually bite are handled and *tested*: verbatim insertion by concatenation (a user value containing `{prices}` survives un-interpolated — pinned) and tri-state unset semantics (empty/whitespace/None/non-string all keep the default sentence). The asymmetric placement (batch: replaces Be CONCRETE; micro: appends after NEVER/[REDACTED]) is deliberate, documented in three places, and ordering assertions pin it. One nit:

- hermes_cli/config_defaults.py:809 — nit — the comment says the string "is appended after the NEVER/[REDACTED] block on micro-compact" — worth also stating the rationale for the asymmetry in one clause (micro-compact must not lose the redaction directive; batch keeps it elsewhere in the template), so a future prompt-tuning pass doesn't "fix" the inconsistency blindly.

No blocking issues found.

— reviewer-b (automated review)
