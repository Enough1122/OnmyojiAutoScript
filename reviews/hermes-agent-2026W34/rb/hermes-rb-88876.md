> AI code review — automated review; please use your judgment.

Nice flake fix with an unusual degree of care for a test-only change: `vi.useFakeTimers({ toFake: ['Date'] })` pins the clock *selectively* so the timestamp assertion becomes deterministic while the component's own timers (running arc animation, tooltip delay) keep running for real, `afterEach` restores the timers, and the comment explains precisely which day-boundary race the test was never meant to exercise ("Yesterday at 11:5x PM" between 00:00 and 00:05). Future readers get the full story inline.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
