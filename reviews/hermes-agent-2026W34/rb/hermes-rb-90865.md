> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Solid implementation of a deceptively fiddly feature: the sanitizer is genuinely allowlist-driven (tags, per-tag attrs, style property whitelist plus an `url(|expression(|@import|javascript:`) kill-switch, scheme-checked hrefs, event handlers dropped), prior-quote detection across Gmail/Thunderbird/ProtonMail/Yahoo markers prevents recursive quoting, `References` is now a real chain instead of a single message-id, and the `--html`/`--no-quote-original` flags keep old behavior one flag away. Findings:

1. skills/productivity/google-workspace/scripts/gmail_reply_formatting.py:_SanitizingHTMLParser — once a prior-quote marker sets `stopped`, all remaining input is dropped *including end tags*, so safe elements opened before the stop point are emitted without their closers. The sanitized fragment then gets wrapped in our own `<blockquote>`, and unclosed `<table>/<div>` ancestors from the original mail will swallow or distort the rest of the composed reply depending on the client's recovery behavior. On transition to `stopped`, emit closing tags for any still-open non-dropped entries in `open_tags` (reverse order) before halting.

2. scripts/gmail_reply_formatting.py:_HTMLToTextParser — the plain-text fallback path only recognizes `gmail_quote` as a quote boundary, while the HTML sanitizer honors the full set (`_QUOTE_CLASSES`, `_QUOTE_IDS`, `data-hermes-quote`, cite-blockquotes). A thread whose prior message is an Outlook (`divreplyfwdmsg`) or ProtonMail quote gets those quotes duplicated into the "> "-prefixed history of a plain-text fallback reply. Share the same detection predicate between both parsers.
