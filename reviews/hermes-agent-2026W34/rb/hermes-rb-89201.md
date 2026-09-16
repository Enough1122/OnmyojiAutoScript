> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Fixes a genuinely ironic data-loss path: every STT *failure* branch preserved the audio path while **success** dropped it — so better transcription made recordings less reachable, since `content` is the only durable record of an attachment. Appending the `[User sent audio: <agent-visible path>]` marker after the quoted transcript keeps the model reading the words first (#41603's lesson, explicitly tested), reuses the marker grammar consumers actually parse instead of the prose variant, routes the path through `to_agent_visible_cache_path`, and the five tests cover success/grammar/ordering/empty-sentinel/multi-clip precisely, including that the empty sentinel still emits no marker.

Nit (non-blocking): gateway/run.py:24414 — the marker is hand-built as an f-string next to `_build_media_placeholder`'s existing audio grammar; if that builder ever gains fields or changes wording, this site silently drifts out of the parseable contract the tests just pinned. Call the builder (or extract its audio arm) here so there's one emitter for the grammar.
