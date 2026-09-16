> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Sensible fix — preferring the bundled \`venv\` interpreter over a loose sibling \`python.exe\` matches how installs are laid out. A few points:

- **apps/desktop/electron/windows-remote-lifecycle.ts:40 — the first candidate hardcodes the \`hermes-agent\` directory name.** \`Join-Path $hermesHome "hermes-agent\\venv\\Scripts\\python.exe"\` breaks whenever the install root isn't literally named \`hermes-agent\` (custom clone dirs, zip extracts). Since \`$hermes\` is already resolved, \`Join-Path (Split-Path $hermes) "venv\\Scripts\\python.exe"\` derives the same location from the *actual* install path and covers every layout — worth making that the primary candidate.

- **windows-remote-lifecycle.ts:39-42 — no check that the selected interpreter belongs to the Hermes install.** If an unrelated \`venv\` exists next to the binary, it wins silently; downstream failures will look like mysterious import errors on the remote host. Suggestion: after selection, sanity-check a marker (\`pyvenv.cfg\` presence, or that \`$python | & -c "import hermes"\` style probe if cheap).

- **windows-remote-lifecycle.ts:43 — the failure message doesn't say where it looked.** "The remote Hermes Python runtime was not found" forces users to SSH in and hunt. Suggestion: include the candidate list in the thrown message (\`"Tried: $($pythonCandidates -join ', ')"\`).

- **No test coverage for the probe variants.** The PowerShell snippet is assembled inline, so at minimum consider a unit test asserting the generated script contains both candidate paths and keeps \`-LiteralPath\` semantics (spaces-safe), since quoting regressions here are easy to introduce silently.

Nit: windows-remote-lifecycle.ts:39-41 — \`$pythonCandidates=@(); $pythonCandidates+=…\` can be one expression: \`$python = @((Join-Path …),(Join-Path …)) | Where-Object {…} | Select-Object -First 1\`.
