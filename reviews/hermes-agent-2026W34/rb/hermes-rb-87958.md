> AI code review — automated review for reference; please use your judgment.

Review of "fix(skills): prevent HAR credential leakage". Well-layered secret hygiene for a skill whose whole workflow handles live credentials: capture outputs get owner-only permissions with symlink refusal (`O_NOFOLLOW` on the CDP path plus a pre-check on the Playwright path), the derivation tool redacts credential headers and structured credential fields while HONESTLY documenting that unstructured bodies can still leak, and the SKILL.md guidance shifts from "copy these headers" to "obtain equivalent values from an approved runtime secret source" without pretending the technique bypasses auth. The contributor entry is included. Suggestions:

1. optional-skills/.../scripts/har_capture.py:51 (TOCTOU asymmetry) — the plain-capture path checks `islink` BEFORE launching the browser, then lets Playwright create/write the file itself; the CDP path got the stronger O_NOFOLLOW open — aligning both on an os.open-based private write would close the small check-vs-write window too.

2. nit — consider emitting one stderr line when redaction REPLACED credential material during derive ("redacted N credential headers/fields"), so users know their HAR contained live secrets even if they skip the SKILL.md fine print.
