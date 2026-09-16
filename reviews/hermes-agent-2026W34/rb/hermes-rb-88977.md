> AI code review — automated review for reference; please use your judgment.

Plausible cosmetic fix: the horizontal bar now matches the box's interior width (`inner`) instead of the outer `w`, so the ═ rule should line up with the side borders instead of overhanging by two columns.

1. cli.py:~4614 — this hunk doesn't show where the side borders are emitted; worth confirming visually once that the bar and the border corners actually meet at both widths (narrow terminal + wide title). If they do, ship it.
2. nit: `inner = w - 2` plus `content_width = inner - 2` suggests a small width ladder that keeps drifting; deriving all three from one `_box_widths(w)` helper would stop the next off-by-two at the source.

No blocking issues found.
