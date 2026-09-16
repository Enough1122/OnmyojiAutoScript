> AI code review — automated review for reference; please use your judgment.

This is exactly how a credential-store fix should be written. The three-way split is right: present-but-unreadable (OSError) re-raises and touches nothing; genuine corruption degrades *only after* preserving a `auth.json.corrupt` copy whose existence is honestly reported; a BOM'd healthy store reads as `utf-8-sig` instead of being misclassified into the wipe path. The test suite proves the actual regression (a photon write must not erase other providers' tokens), explains its `monkeypatch.context()` choice, and covers BOM survival, corrupt-copy preservation outliving the overwrite, and the missing-file case.

— reviewer-b (automated review)

No blocking issues found.
