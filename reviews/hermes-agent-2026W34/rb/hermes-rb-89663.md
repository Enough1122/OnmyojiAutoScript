> AI code review — automated review for reference; please use your judgment.

Review of "fix(profiles): reject non-string profile names instead of coercing". Correct fail-loud flip: `str()` coercion turned a numeric DB row id into a real on-disk `profiles/0/` directory (#88842), and rejection with a type-naming message beats silent phantom profiles; the literal-"0"-string-is-valid test draws the distinction exactly where it belongs. One verification item:

- sweep the CALL SITES of `normalize_profile_name` — any path that previously fed it an int (dashboard JSON payloads, config values, subprocess argv parsing) now gets ValueError instead of a working profile, and each such caller needs either an explicit catch or its own resolution step ("resolve the numeric id to a name first", as the docstring says) so the fix doesn't convert silent corruption into unhandled crashes at a different layer.

No blocking issues found.
