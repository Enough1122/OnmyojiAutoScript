> AI code review — automated review for reference; please use your judgment.

Review of "feat(plugins): expose declared config fields to UIs". Good contract design: the new `config_fields` list form is NORMALIZED into the existing `config_schema` mapping at parse time (single downstream representation), explicit duplicates warn and let config_schema win, unknown-key reservations are updated, and the voice panels union three sources (static keys ∪ backend schema ∪ live config presence) so plugin fields render even before a schema fetch lands. STT plugins joining the TTS picker path keeps the surfaces symmetric, and the label override on ConfigField preserves i18n precedence. Suggestions:

1. hermes_cli/tools_config.py:_plugin_voice_providers — the bare `except Exception: return []` makes a broken plugin's setup_schema silently vanish from the picker; a debug log naming the provider would turn "my plugin disappeared" into a diagnosable event.

2. nit — config-presence-derived keys bypass any type information (no options/required), so they always fall to inferred generic inputs; consider marking them in the schema response as `declared_in_config: true` so UIs can hint "(detected)" rather than presenting an undocumented field as fully supported.
