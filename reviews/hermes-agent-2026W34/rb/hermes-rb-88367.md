> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-contained scrub: the marker regex is anchored to xAI's actual `{render_inline_citation …}` shape, applied defensively to *every* returned row regardless of which extraction path produced it (the annotation-fallback test is the important one — the raw message body is exactly where Grok drops these), adjacent markers collapse to a single space rather than gluing words together, and the cheap substring gate skips the regex for clean values. Tests cover the reported case, the fallback path, and regex variants including tail-position markers.
