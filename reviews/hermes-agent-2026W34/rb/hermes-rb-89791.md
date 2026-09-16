> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Fix and guardrail land together: swapping `leading-none` for explicit line heights keeps g/y/p/q descenders visible at every session-row text tier, the mirrored `pe-2` stops timestamps sitting on the row edge, and — the part most CSS fixes skip — the new Playwright spec asserts the *geometry* rather than screenshots: symmetric inline padding, timestamp clearing trailing padding, `scrollHeight ≤ clientHeight` for descender fit, ellipsis actually engaged on long titles, and a walk up the overflow-hidden ancestor chain proving no clipping box shaves the title, across both densities. Findings below are minor:

1. apps/desktop/src/app/chat/sidebar/session-row.tsx:484 et al. — the line heights are hard-coded pixels pinned to today's rem sizes (`text-[0.625rem]` ↔ `leading-[13px]`, `0.6875rem` ↔ 14px, `0.8125rem` ↔ 17px). If any of those type sizes are later tokenized or user-scaled, every pairing silently re-clips. Unitless/em ratios (`leading-[1.3]`) would track future size changes automatically while preserving the same visual result today.
