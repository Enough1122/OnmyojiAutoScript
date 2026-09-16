> AI code review — automated review; please use your judgment.

Right tool choice: `plistlib` transparently handles the binary `bplist00` form that `launchd` rewrites on bootstrap (which made every `gateway status`/`install` path throw `UnicodeDecodeError`), and re-emitting XML feeds the existing comparison pipeline unchanged.

1. `hermes_cli/gateway.py:~4705–4710` — `plistlib.load()` raises (`plistlib.InvalidFileException`) on a truncated/corrupt plist, and nothing here catches it — why it matters: the old code crashed with a decode error; the new one crashes with a different error unless *every* caller already guards — suggestion: wrap the load in `try/except Exception: return False`; a corrupt installed plist reporting "not current" is exactly right, because it drives the auto-refresh path to rewrite it (self-healing instead of crash).

2. `hermes_cli/gateway.py:~4710–4711` — comparing `plistlib.dumps(loaded, FMT_XML)` against the hand-written generated template assumes `_normalize_launchd_plist_for_comparison` is insensitive to key ordering and whitespace/indentation differences that a plistlib round-trip introduces — why it matters: if the normalizer is line-oriented, an equivalent-but-reordered plist now reads as "not current" and forces pointless reinstall churn on every check — suggestion: verify the normalizer tolerates reorder (or better, compare `plistlib.loads(generate_launchd_plist()) == _installed_data` structurally and keep the text path only as fallback).

Nit: `import plistlib` can live at module top with the other imports per file convention.

— reviewer-a · automated agent review (Hermes week-review)
