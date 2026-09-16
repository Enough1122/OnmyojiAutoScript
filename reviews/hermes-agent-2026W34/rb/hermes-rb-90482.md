> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Solid upgrade on both axes. The durable UID cursor fixes a real restart-safety hole (another client marking mail SEEN while Hermes is down silently swallowed those messages under the UNSEEN search), with write-after-dispatch ordering proven by the failure test, atomic tmp+replace persistence, and an \`int(uid) <= cursor\` guard covering the \`X:*\` inclusive-range quirk. Recipient preservation is similarly complete: getaddresses-based extraction with dedup, thread-context carrying To/Cc into replies (self dropped, extras de-duped into Cc), always-cc/reply-all-senders config plus per-send cc/subject plumbed through both the adapter path and the standalone sender, with tests pinning each combination.

Four things worth attention:

- **plugins/platforms/email/adapter.py:~600 (`_load_uid_cursor`) — the stored \`imap_host\` is written but never validated on load.** UIDs are scoped to a specific server's mailbox; if the same address is later pointed at a different host (migration, provider switch), the stale high-water mark silently suppresses everything below it on the *new* host. Suggestion: compare \`payload["imap_host"]\` against \`self._imap_host.lower()\` and discard the cursor on mismatch (log it).

- **One-time upgrade gap:** on the first run after this change \`_last_processed_uid\` is None and connect bootstraps it to the *current* newest UID — so mail that arrived while the previous version was down (which UNSEEN would have caught) is skipped exactly once. Worth a line in the changelog; alternatively seed the cursor from the lowest unseen UID on that first bootstrap.

- **Head-of-line blocking is now durable.** Since the cursor only advances post-dispatch, one persistently failing message (poison attachment, handler crash) both stops cursor progress and, if \`_dispatch_message\`'s exception escapes the poll loop unchecked, halts polling altogether. Confirm the poll task wraps \`_check_inbox\` failures; consider a retry-cap that logs-and-skips a repeatedly failing UID past N attempts so one bad message can't freeze the inbox.

- **Two sources of truth for external correspondents.** The adapter accepts \`extra.external_correspondents\` *or* \`EMAIL_EXTERNAL_CORRESPONDENTS\", while the gateway-side isolation (the companion mechanism for skipping memory/persona) reads only the config key. A user configuring via the env var gets the "[External correspondent email]" tag but full operator context. Unify on one lookup path.

No blocking issues found — the cursor work in particular is the right fix.