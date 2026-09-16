> AI code review — automated review; please use your judgment.

Correct fix for a real class of bug: the desktop normalizer was rewriting gateway-host POSIX paths into local Windows forms (`\\wsl.localhost\…`) before the renderer could read them remotely. The new gate handles bare `/paths`, host-less `file:///` URLs while deliberately excluding drive-letter spellings (`/^\/ [a-z]:\//i`) and hosted `file://server/share` URLs, strips wrapping backticks from model output, and only treats *relative* targets as remote when the cwd itself is POSIX and the target carries neither a URI scheme nor a backslash — each decision has its own test, including the four-way negative matrix that must still reach the Electron normalizer.

No blocking issues found.

Nit (`apps/desktop/src/lib/local-preview.ts:~67–87`): two residual ambiguities worth one comment or test each — (a) ````~/notes/x.html```` home-relative remote targets don't start with `/`, so they take the relative branch and depend on `joinPath` doing something sane with `~`; (b) a protocol-relative ````//server/share/x.html```` spelling of a Windows UNC path starts with `/` and will be classified as remote POSIX — rare model output, but the classifier's boundary cases deserve to be pinned so future edits know they're deliberate.

— reviewer-a · automated agent review (Hermes week-review)
