> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Exactly the right fix shape for #90606: detecting the `bplist00` magic and pushing *both* sides through a plistlib parse → XML re-render gives one canonical serialization, which simultaneously fixes the crash, prevents formatting-only false staleness (and thus the rewrite/re-binarize endless refresh loop the docstring warns about), and keeps the existing PATH normalization working since it now operates on stable XML text. The test set is exemplary — matching binary, differing binary, PATH-only delta across the round-trip, unchanged XML behavior, and corrupt-file-stays-stale. Fail-closed (`None` → stale → reinstall) is also the right default for an unreadable plist.

Nit (non-blocking): hermes_cli/gateway.py:4749 — if the *expected* side ever fails its own round-trip (i.e., `generate_launchd_plist()` emits something plistlib rejects), every staleness check returns False and reinstalls the same unparseable file forever — a quiet write-on-every-status loop with no signal. Consider logging once (or caching a "generated plist invalid" flag) when `expected_xml is None`, distinguishing it from "installed file unreadable" so a generator regression announces itself instead of manifesting as mysterious repeated plist rewrites.
