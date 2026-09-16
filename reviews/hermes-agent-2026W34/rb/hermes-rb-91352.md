> AI code review — automated review for reference; please use your judgment.

1. agent/redact.py:1434 — the guard regex only matches %(name)s conversions. Why it matters: a custom format string using %(session_tag)d or %(session_tag)r still crashes with the same 'Formatting field not found' error, because the missing field gets skipped by the scan but then fails at render time (and '' would be wrong for non-string conversions anyway). Suggestion: broaden the scan to all conversions (r'%\((\w+)\)[a-zA-Z]') and either type-aware-default (0/'') or document that only string conversions are protected.

2. agent/redact.py:1436 — re.findall runs against self._fmt on every single formatted log line. The format string is fixed for the formatter's lifetime, so this is repeated work on the hottest logging path. Suggestion: compute the field list once in __init__ (after super()) and store it; keep the isinstance(_style, PercentStyle) check inline.

3. Root-cause option worth considering: hermes_logging's _install_session_record_factory presumably *replaces* whatever factory exists instead of chaining it. Wrapping any pre-existing factory (factory = lambda *a, **k: inject(old_factory(*a, **k))) would eliminate this entire failure class — plugins could then replace factories freely — while today's formatter guard remains a sensible second layer of defense. Both together are ideal.

Good defensive instinct and an honest regression test that constructs the bare LogRecord directly rather than mocking hasattr.
