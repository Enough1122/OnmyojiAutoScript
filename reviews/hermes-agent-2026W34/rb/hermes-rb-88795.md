AI code review note for PR 88795:

Clean SDK surface addition: a one-line wrapper over the internal reveal verb, exposed with an honest docstring, documented in both the API table and prose, and covered by a test that proves the un-dismiss actually restores the pane into the layout tree. Letting plugin commands route into their own pane instead of falling back to openExternal is a genuine UX improvement.

Nit: the docstring promises reveal handles "un-collapses its side, un-hides it, un-minimizes its zone, and fronts its tab," but the test pins only the dismissed case - the other hiding mechanisms are presumably handled inside revealTreePane, so one more test each (or a pointer to existing coverage) would keep the promise honest as that helper evolves.

No blocking issues found.