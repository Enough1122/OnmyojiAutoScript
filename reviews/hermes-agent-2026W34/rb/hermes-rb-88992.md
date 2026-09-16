> AI code review — automated review for reference; please use your judgment.

Good generalization: replacing two hardcoded `1;5C/D` cases with a parameter-driven `parseCsiArrow` fixes the entire family of extended encodings (lock-state bits, event fields, reversed param order seen through proxies) instead of whack-a-mole, and `CSI_U_RE` accepting Kitty's trailing event/text fields closes the sibling gap. Tests assert full modifier shapes plus the InputEvent-empty property. Points:

1. agent-side mapping question: `[1;131C` expects `{meta:true}` with **no shift**, yet 131 = base(1) + 2(alt) + 128(numlock) under the standard bitfield — i.e. Alt+Shift. Either `decodeModifier` intentionally reports alt-as-meta and ignores shift for nav keys, or the expectation encodes a bug. Whatever the answer, it should match how the *mouse-wheel* modifier decoding interprets the same bits (consistency between the two decoders matters more than which convention wins) — worth one cross-reference comment or test.
2. `parseCsiArrow` returns null when no parameter equals 1, so legacy single-param forms (`[5D` = Ctrl+Left without the leading 1) fall through to the older handlers exactly as before — correct, but pin that with one test so the early-return isn't later "simplified" into swallowing them. (nit)
3. `CSI_U_RE` gained a `$` anchor it didn't have before — stricter (good), but verify nothing fed it prefixes of longer sequences expecting a match. The new kitty event-field form (`;129;1u`) being accepted suggests you already did. (nit)
4. Removing the hardcoded Ctrl-arrows in favor of the generic path is exactly the dedup this file needed. (positive)

No blocking issues found.
