> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Exemplary change for #90837's actual root cause: durability was previously whatever `SQLITE_DEFAULT_WAL_SYNCHRONOUS` the local SQLite build shipped with — invisible and unpinnable. The parser deliberately distinguishes "unrecognized" (warn + leave untouched) from "unset" (no write), handles the YAML `on`/`off`→bool trap explicitly (`off`=OFF, `on` rejected rather than coerced to 1 via `int(True)`), and the Darwin floor is exactly right — refusing to *lower* below FULL while allowing EXTRA, because `_enforce_macos_synchronous_full()` runs earlier in WAL activation and config would otherwise silently undo it by running last. The test matrix covers every branch including "other pragmas still work" and "floor doesn't apply off-Darwin", plus a doc-presence guard.

Nit (non-blocking): cli-config.yaml.example:23 — "macOS is always held at FULL regardless" undersells the implementation slightly: it's a *floor*, not a pin — `EXTRA` is honored on Darwin and only sub-FULL values are refused. Since operators choosing EXTRA for extra safety might read "held at FULL" as "don't bother", suggest "never below FULL on macOS; higher levels are honored".
