> AI code review — automated review for reference; please use your judgment.

Clean provider addition: raw-hex HMAC verification for `X-Gitea-Signature`/`X-Forgejo-Signature` via timing-safe comparison, correctly positioned after the GitHub branch so modern senders that also emit `X-Hub-Signature-256` hit that path first, event-type header recognition wired into filtering, and the test set covers valid/invalid/wrong-body plus non-ASCII-header rejection for every new header.

— reviewer-b (automated review)

No blocking issues found.
