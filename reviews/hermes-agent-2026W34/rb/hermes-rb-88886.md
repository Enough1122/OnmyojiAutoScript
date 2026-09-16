> AI code review — automated review; please use your judgment.

Nicely built affordance: the matcher covers POSIX, drive-letter, and UNC absolutes with boundary anchors that stop at sentence punctuation (`file.sh!`, `file.tar.gz.` cases tested), reject `/`, `//`, and relatives, and the reveal action goes through a new SDK door (`host.revealFileInTree`) whose docstring correctly notes out-of-workspace paths are ignored by the tree — so arbitrary system files never become clickable. Rendering keeps everything else literal (no markdown interpretation), no side effects at render time are asserted, and the static-markup test approach keeps these fast.

No blocking issues found.

Nits:
1. (`filepath-links.tsx` `ABS_PATH_RE`) single-segment tokens like ````"/v2"```` or ````"/thread"```` in prose will match and render as dead buttons (the tree silently ignores them); if that gets noisy, require either a second segment or a known file extension before linking.
2. (`drawer.tsx`:~858) only comment bodies are linkified — the task description/body shown in the same drawer has the same "worker mentions a path" pattern; worth applying `LinkifiedFilePath` there too for consistency.
3. The new `revealFileInTree` SDK surface extends the plugin host API — worth one line in the plugin-sdk changelog/docs if such a file exists, since third-party plugins can now call it.

— reviewer-a · automated agent review (Hermes week-review)
