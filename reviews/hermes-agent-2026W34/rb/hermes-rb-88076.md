> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean locale addition: `defineLocale`'s English-fallback contract is used as intended for a partial translation (explicitly commented at the top of id.ts), registration in both `TRANSLATIONS` and `LOCALE_META` ("Bahasa Indonesia") is complete, and the translations themselves read naturally rather than machine-literal — including the tricky banner copy (memory/disk warnings) and the cron schedule-mode vocabulary. No wiring changes beyond the two registry touches, so risk to existing locales is nil.
