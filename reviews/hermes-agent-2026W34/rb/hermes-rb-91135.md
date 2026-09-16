> AI code review — automated review for reference; please use your judgment.

Exactly the right shape for this fix: the page-side locator now ships its `devicePixelRatio` alongside the CSS-px point, the caller scales once before `glideTo` so *every* pointer action that flows through the aim point (click and the triple-click-select used by typing) benefits, the `dpr > 0 && dpr !== 1` guard keeps ordinary displays byte-identical to before while rejecting nonsense ratios, absent values are documented as "treat as 1" in the type contract for synthetic/fallback paths, and both the fractional-DPR and absent-DPR behaviors have regression tests with the math spelled out in assertions.

No blocking issues found.

Nit (`apps/desktop/src/lib/preview-act/act-in-page.ts:~495`): worth a quick sweep that no *other* `sendInputEvent` call site in the preview-act path consumes raw CSS coordinates from a different source (e.g., drag endpoints or scroll targets computed outside `actInPageCore`) — if they all derive from this same located point they're covered by construction; a one-line comment at those sites saying "already device-px via DPR scaling" would prevent a future path reintroducing the miss.

— reviewer-a · automated agent review (Hermes week-review)
