> AI code review — automated review for reference; please use your judgment.

Correct and complete-feeling fix: treating Caps(64)/Num(128) lock bits as semantically transparent matches the xterm/Kitty modifier spec, deriving navigation lock variants from `ANSI_SEQUENCES.get(base_seq)` (rather than re-deriving semantics) means modified forms keep their Ctrl/Alt meaning automatically — and the tests prove exactly that (133D → ControlLeft, not Left). The cache-dump comment shows awareness of the VT100 parser prefix-cache trap. Points:

1. hermes_cli/pt_input_extras.py:~395 — the two navigation loops (arrow-final vs tilde-code) are structurally identical; a small helper taking `(build_seq, key_for)` would halve them and make the next key family (Find/Select F1-F12 tilde codes 1,4,11-15?) a one-line addition. Currently adding those means another copy-paste block. (nit)
2. Coverage gap in tests: modified-plus-lock for H/F (`ESC[1;133H` → Home) and tilde keys with real modifiers (`ESC[3;133~`) aren't asserted — plain 129 is, and D/C have the modified case. Two more parametrize entries would seal it. (nit)
3. `_modifier_lock_variants` returns 4 tuples for every paired install — mapping size ×4 registrations at import; trivial memory, but worth knowing the ANSI table grows ~4× for these families if anyone later iterates it diagnostically. No action needed. (nit)
4. Consider asserting `changed` increments stay idempotent across double-install (the membership guard implies it; one test would pin it against future refactors of the guard). (nit)

No blocking issues found.
