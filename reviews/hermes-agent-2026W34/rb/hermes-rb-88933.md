> AI code review — automated review; please use your judgment.

Correct diagnosis and appropriately scoped fix across all three surfaces (CLI mixin, TUI `editor.ts`, composer state): Windows `shell: true`/`shell=True` is what lets CreateProcess resolve `.CMD`/`.BAT` shims like VS Code's `code`, while POSIX keeps direct list execution specifically to avoid shell-interpreting $EDITOR content — and both sides of that security/behavior split have spy-based tests asserting the exact flag. The TUI side also improves error propagation (`result.error && status === null` now throws instead of silently reporting a null exit).

No blocking issues found.

Nits:
1. (`ui-tui/src/app/useComposerState.ts`:~400) the spawn/error-handling block duplicates `openInEditor()` in `lib/editor.ts` almost line-for-line (same shell:true comment, same error throw); factoring a shared `spawnEditor(cmd, args, file)` helper would keep the two Windows behaviors in lockstep.
2. Worth one docs line noting that on Windows the $EDITOR string is interpreted by cmd.exe when shell:true is set (so exotic quoting may behave differently than on POSIX) — it's the standard trade-off git/npm also make, but users hit it rarely enough that a mention helps.

— reviewer-a · automated agent review (Hermes week-review)
