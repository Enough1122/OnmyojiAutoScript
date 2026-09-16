> AI code review — automated review for reference; please use your judgment.

Correct recovery model, and the signal taxonomy is right: power-resume and network-online are *strong* signals (the OS may have discarded TCP underneath a still-OPEN WebSocket, so the only honest state is to retire and redial), while visibility stays soft — a sensible gradient rather than blanket force. The redundant-backoff cleanup (`clearReconnectTimer()` after `close()` schedules the regular retry) shows the interaction was thought through, secondaries get the same treatment via `forceOpenSockets`, and both halves are tested against real hook/store code with fake sockets that deliberately keep `readyState === OPEN` across resume — precisely reproducing the macOS failure mode instead of approximating it. I also verified the blast radius of upgrading `registerGatewayReconnect` to force semantics: its sole producer is the user-invoked gateway menu "reconnect" action, where destructive redial is exactly what the button promises.

No blocking issues found.

Nit: every wake event now closes a *healthy* socket too — a 5-minute lid-close on AC power where TCP survived will still eat a disconnect/reconnect cycle and a transient UI state flip on resume. Acceptable as the safe default, but worth a comment recording that tradeoff ("cheap redial beats a half-open socket we can't cheaply probe"), so a future contributor who adds a lightweight ping-probe knows the behavior change they'd be introducing rather than fighting an unexplained close().

— Reviewed by Hermes AI reviewer (reviewer-f2)
