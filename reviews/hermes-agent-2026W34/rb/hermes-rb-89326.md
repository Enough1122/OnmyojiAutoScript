AI code review note for PR 89326:

Right fix with the right regression test: the provider-recall note wording changed and sanitize_context silently stopped stripping it at boundaries; extending _INTERNAL_NOTE_RE to match both the new "untrusted historical data" phrasing and the legacy "recalled memory context" phrasing keeps persisted transcripts scrubbing correctly. The dual-wording test pins exactly that.

Nit: this bug happened because the note template and its sanitizer regex live in different modules with only prose coupling. Suggest exporting the canonical note strings (builder-side constants) and deriving/matching against those - or at minimum a comment on each pointing at the other - so the next wording change cannot outrun the stripper again.

No blocking issues found.