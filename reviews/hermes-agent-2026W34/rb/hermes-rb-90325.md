> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix, right convention: moving the truncation hint from trailing free text into a structured `_hint` payload field restores the tool-output JSON contract that strict tool-message providers depend on, and matching the existing `_omitted`/`_warning` side-channel style keeps the function internally consistent. The regression file asserts exactly the three things that matter — full round-trip through `json.loads`, hint present as a field with the right next-offset, and no hint key on untruncated results — while the two updated legacy tests confirm the old string-append assertions are gone everywhere.
