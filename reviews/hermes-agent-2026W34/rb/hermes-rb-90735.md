> AI code review — automated review for reference; please use your judgment.

Review of "fix(qqbot): make API_BASE overridable via QQ_API_BASE env var". Clean, minimal, and consistent with the neighboring `PORTAL_HOST` pattern — import-time `os.getenv` matches the module's existing convention and the production default is unchanged. One nit:

- gateway/platforms/qqbot/constants.py:21 — `TOKEN_URL` stays hardcoded to bots.qq.com, so pointing `QQ_API_BASE` at a staging/mock host still performs token issuance against production; consider an analogous `QQ_TOKEN_HOST` (or deriving both from one override) whenever this surface is touched next.

No blocking issues found.
