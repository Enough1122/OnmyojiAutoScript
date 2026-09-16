> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: the recovery action hardcodes '/settings?tab=gateway'. If a shared routes module exists in this app, import it so a future settings-route refactor can't silently break the deep link. The OAuth-only gating is the right call (token sources keep their ordinary unreachable state rather than being offered a sign-in that doesn't apply), retained rows carry AND clear the flag across recovery, and the tests cover the merge carry-over, both notification shapes, and the navigation click.

— Reviewed by Hermes AI reviewer (reviewer-f)
