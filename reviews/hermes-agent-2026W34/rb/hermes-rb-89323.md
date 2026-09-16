AI code review note for PR 89323:

Clean feature: the curated prefix keeps its hand-tuned descriptions and ordering, then every remaining live model that is both free and tool-capable is appended with the same "free" marker computed by the existing pricing helper - so free-tier users see the full set without importing the 400-model paid catalog. The test pins all four quadrants (curated paid kept, uncurated free+tools added as "free", free-without-tools excluded, uncurated paid excluded), including the supported_parameters gate.

Nit: ordering of the appended block follows the catalog's JSON array order, so it may shuffle between refreshes; sorting that tail alphabetically would keep the picker stable across polls. Cosmetic either way.

No blocking issues found.