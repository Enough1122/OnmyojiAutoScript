> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Excellent TTS hygiene work with unusually good test discipline: every rule carries its real-world repro in a comment (the "eeeeee" loop on hyphenated slugs, the growl on em dashes, the hanging colon stutter), the negative cases are pinned as carefully as the positives (and/or, N/A, dates, ratios, 5/month all survive the path matcher), digit-preceded colons stay ratios, and the desktop and gateway implementations ship mirrored test corpora so both voices behave identically.

- **The two implementations will drift.** speech-text.ts and tts_text_normalize.py now carry byte-identical PATH_TOKEN_RE plus parallel dash/euro/colon rules, maintained by hand in TypeScript and Python. The mirrored tests help, but nothing fails when someone tweaks one regex and forgets the other. Suggestion: extract the shared cases into a JSON corpus file both suites consume verbatim (and optionally a CI check that the two PATH regex source strings remain equal) - the tests are already 80% of the way there.

- Nit: MEDIA_PATH_RE uses \S+, so a token at sentence end swallows the following period ("see MEDIA:/tmp/x.py." loses its full stop); the surrounding-prose examples happen to place tokens on their own lines or at string end, but an inline mid-sentence case would silently eat punctuation. A trailing [.,;:!?)\]] exclusion (re-inserting it) would tidy that.

No blocking issues found.