> AI code review — automated review; please use your judgment.

Correctly scoped compatibility fix: `value` is added as the **last** unwrap key so display keys (`label`/`description`/`text`/`title`) keep winning when present, the GLM-family no-display-key shape stops emptying the whole choice set, and `name` stays excluded with its component-field rationale intact. Both the new unit case and the flipped expectation in the callback test document the behavior change at the exact spot a future reader will look.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
