> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean extraction of a pure helper with the validation edge cases handled up front: only a real 40-hex commit becomes the panel's `version` (all-zero placeholder stamps correctly rejected), dirty builds get the `-dirty` suffix, and the renderer-skew warning moves into `credits` secondary text instead of being concatenated into the version string. Seeding before app-readiness plus the existing refresh-before-open now share one code path, and the vitest suite covers valid/skew/invalid/dirty including the fallback-commit rejection.
