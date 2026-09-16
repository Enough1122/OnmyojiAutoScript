> AI code review — automated review for reference; please use your judgment.

1. `apps/desktop/src/app/shell/hooks/use-statusbar-items.tsx:401–407` — the statusbar gateway switcher is deleted outright, but the statusbar renders in surfaces where `ChatSidebar` may not (auxiliary/peer-instance windows — cf. the `isAuxiliaryWindow`/`isPeerInstanceWindow` handling inside `connection-switcher.tsx`) — why it matters: those windows previously showed which gateway they were talking to and now have no gateway indicator at all, a silent regression for popout workflows — suggestion: verify aux/peer window chrome against the new design and either keep a minimal read-only indicator or document the intended absence.

2. `apps/desktop/src/app/chat/sidebar/index.tsx:~1896` — the manage action deep-links to `SETTINGS_ROUTE + '?tab=gateway'` while the removed statusbar entry used `'?tab=connections'` — why it matters: if both tab ids are live this silently changes which pane users land on from the switcher (docs uniformly say Gateways), and the string-concatenated query invites future drift between call sites — suggestion: export a single `SETTINGS_GATEWAYS_ROUTE` constant from ````routes```` and use it in every entry point.

3. `apps/desktop/src/app/chat/sidebar/profile-switcher.tsx` — `connectGateway` is dropped from the component and its test mock, but no locale file is touched in this PR — why it matters: the key becomes dead weight in every translation bundle (and a trap for translators re-flowing that section) — suggestion: remove `profiles.connectGateway` from the locale sources in this same PR so string cleanup ships with the feature that orphaned it.

4. `apps/desktop/e2e/gateway-switcher.spec.ts:31–38` — the placement contract is asserted via pixel geometry (`gatewayBox.y + height <= profileBox.y`) — why it matters: bounding-box comparisons are sensitive to zoom, DPI scaling, and font-metric changes, producing flaky red builds unrelated to real regressions — suggestion: prefer structural assertions (DOM order, flex-parent class contract) or widen the comparison with a tolerance and retry.

Nit (`connection-switcher.tsx:121–134`): dropping the `connections.length <= 1` early-return means the group/trigger markup now renders for local-only setups — intended per docs, but worth an explicit unit case asserting the single-connection DOM shape so a later refactor doesn't reintroduce the hidden state by accident.

Overall: coherent UX consolidation with unusually complete docs and test updates following the moved control; no blocking issues found — item 1 deserves a quick verification before merge.

— reviewer-a · automated agent review (Hermes week-review)
