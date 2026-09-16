> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Complete provider integration done the way the codebase expects: registry builtins + shadow-protection tests, config defaults, setup-wizard key flow with Edge fallback, tools-picker row, desktop settings enums/free-input/labels, a documented yaml example, and a native `_generate_cartesia_tts` whose test file covers payload construction, header propagation, and error paths. Bonus hygiene: renaming the old test fakes that squatted on the "cartesia" name (`custom_tts_plugin`/`fishaudio`) keeps plugin-namespace tests honest now that the name is real.

Nit (non-blocking): the default voice id `25d7abcb-…` (Jessica) is hard-coded in at least three places — `config_defaults.py`, `cli-config.yaml.example`, and the desktop `ENUM_OPTIONS` for `tts.cartesia.voice_id`. If Cartesia ever retires that voice, three spots need synchronized edits and the desktop enum will silently offer a dead default. Reference a single documented constant (or mark all copies as illustrative-only with a pointer to the canonical one).
