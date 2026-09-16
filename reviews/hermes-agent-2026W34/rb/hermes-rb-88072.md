> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-targeted redaction widening for OAuth payloads specifically: `id_token`, `authorization`, `client_secret`, and `private_key` are exactly the fields an OAuth token/registration JSON carries that the old keyword list missed (`access_token`/`refresh_token` were covered; `authorization` also catches raw `Authorization: Bearer …` header dumps serialized into logs). Dropping straight into the existing `_JSON_KEY_NAMES` alternation inherits the established "quoted string values" matching and case-insensitivity for free.
