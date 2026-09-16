> AI code review — automated review for reference; please use your judgment.

Complete feature with the hard parts handled: the tri-state `extra_headers` contract (`None` = preserve hand-written headers, `{}` = clear) mirrors the api_key guarantee exactly and is pinned by three tests including the round-trip-would-have-wiped regression; the validate probe sends the headers (applied after the derived bearer so custom-scheme auth wins) with both behaviors tested; and normalization is shared with the runtime reader so on-disk shape can't drift. One documentation nit:

- apps/desktop/src/app/settings/custom-endpoints-settings.tsx:407 — nit — the helper text says headers are "Sent with every request" but not that they're persisted in **config.yaml** (unlike API keys, which go to `.env`); users pasting `Authorization: Bearer …` or Cloudflare secrets into this field should know the storage location differs from the key field right above it.

No blocking issues found.

— reviewer-b (automated review)
