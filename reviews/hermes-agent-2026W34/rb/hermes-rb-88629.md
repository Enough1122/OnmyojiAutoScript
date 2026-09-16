> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Small fix, high-leverage test: adding `background_review` fixes the immediate invisibility (#88618), but the real value is `test_every_default_aux_slot_is_pickable` — a meta-assertion that every `DEFAULT_CONFIG["auxiliary"]` slot must appear in the picker (with the intentional non-task keys documented as an explicit allowlist). That turns this entire class of "config slot exists but is undiscoverable" bugs into CI failures forever, instead of whack-a-mole per missing entry.
