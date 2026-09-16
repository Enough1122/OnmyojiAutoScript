> AI code review — automated review for reference; please use your judgment.

Reviewed the full diff. This is careful work: sequence-numbered intents with identity guards, an explicit committed-refresh barrier before validating the remembered session, synchronous anchor capture ahead of the gateway swap, and the serialization rewrite in profile.ts genuinely fixes a latent bug (the old code had concurrent callers *both* await the same gatewaySwitch promise and then *both* fall through to dial — the chained previousSwitch version closes that double-dial race). Test quality is well above bar (deferred-gate serialization ordering, re-click-latest-intent, cross-backend scoping). Remaining points:

- **apps/desktop/src/app/contrib/hooks/use-desktop-integrations.ts:~150-215 — the post-await identity recheck omits pendingConnectionId.** After the refresh barrier resolves, the code re-validates sequence/connectionId/profile but not whether a connection became pending *during* the await, so a restore can still fire while a connect/deeplink flow is mid-flight (the pre-await check alone gated it). Re-read $pendingConnectionId.get() alongside latest and bail symmetrically.

- **use-desktop-integrations.ts:~168-176 — the 3-attempt retry loop has no spacing.** Each false return immediately re-invokes refreshSessions(); since a false means "superseded," a tight triple-call just burns three requests in one tick. A microtask/short delay (or exiting early when the intent was superseded — detectable via sequence) would be cheaper and easier to reason about.

- **Untested lifecycle branches.** The suite covers happy paths and cancellation-by-pending-connection, but not: behavior toggled to fresh_draft while an intent is pending (effect should clear it), retry exhaustion (3x stale -> intent cleared, no openSession), and refreshSessions throwing (catch path preserves the anchor). All are cheap renders away and pin the fail-safe direction.

- **profile.ts:~330-336 — transient swap-target mislabel during chained switches.** $gatewaySwapTarget is set to the *newest* target before the chain reaches it, so while beta is still activating, the UI can display gamma's target. Probably acceptable ("latest wins"), but worth a comment so nobody treats it as a bug later.

- **Anchor-capture staleness window:** registerProfileSwitchAnchorCapture swaps the closure whenever sessions/visibleStoredSessionId change; a click landing between a state update and the effect re-run captures with the previous snapshot. The consequence is benign (anchor one tile behind) but worth a one-line comment documenting that the capture is best-effort.

- **Nit:** appearance-settings.tsx:~726 casts the SegmentedControl id with `as ProfileSwitchBehavior`; deriving options from a const tuple (satisfies readonly {id: ProfileSwitchBehavior}[]) would keep the control type-safe if ids ever drift.

The i18n sweep (5 locales + types) and settings-search wiring are complete, and the refreshSessionsCommitted boolean contract is cleanly layered under the existing refreshSessions wrapper.