> AI code review — automated review for reference; please use your judgment.

The reasoning flip ("layout-specific" only applies when deriving the shifted char from an unshifted codepoint — modifyOtherKeys reports the already-shifted one) is correct per the xterm spec, the decision to exclude the CSI-u/Kitty spelling is right, and the test suite is exemplary: exhaustive leak check, regression guard on letters, dedicated-key preservation, Kitty non-mapping, and idempotency. Minor notes:

1. hermes_cli/pt_input_extras.py:338 — same-class gaps remain for higher modifiers: `ESC[27;4;63~` (Alt+Shift+/, etc.), `27;6;` (Ctrl+Shift), `27;8;` are still unmapped, so those combos keep leaking literal text into the buffer under the very mode this module enables. The identical already-shifted argument applies; worth a fast-follow rather than expanding this PR's blast radius.
2. pt_input_extras.py:341 — terminals that deviate from the spec by reporting the UNSHIFTED codepoint under modifyOtherKeys=2 (a few older VTE builds have historically done this) will now insert the base character instead of leaking the sequence — strictly better than the status quo, but a silent-wrong-input class. If you want belt-and-braces, a startup probe or a documented opt-out env var would give those users an escape hatch. Low priority given how rare that deviation is.
3. pt_input_extras.py:340 — `[27;{mod};{cp}~` construction now exists in three places (letters above, symbols here, multi-modifier below). A tiny `_mok_seq(modifier, codepoint)` helper would make the next extension mechanical. (nit)

No blocking issues found.
