> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-reasoned payload extension: routing streamed tokens to the right conversation genuinely is a different question than which stored history a turn extends, and `chat_id`/`chat_type`/`thread_id` answer it directly. Folding `on_interim_message` onto the shared `_stream_hook_base_payload()` also quietly fixes the interim hook's missing session/model/provider/surface fields, and always-present-empty-string keys (instead of absent ones) spare consumers key-existence guessing — both behaviors are pinned by the new gateway-shaped and CLI-shape tests.

Nit (non-blocking): hermes_cli/plugins.py:170 — the base-payload field list is now hand-maintained prose in the hook registry comment, duplicated against `_stream_hook_base_payload()`; the next added field will inevitably update one and not the other (this PR itself had to touch both). Point the comment at the code as the source of truth ("see AIAgent._stream_hook_base_payload for the exact base payload") instead of enumerating fields.
