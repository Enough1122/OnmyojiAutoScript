> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Nice contract-first approach — parser-only now, wiring later, fail-fast errors, real tests. Design points worth settling *before* the runtime wiring lands:

- **hermes_cli/profile_provider_sharing.py:30-33,100-105 — the boolean shorthand inherits future capabilities by construction.** \`_DEFAULT_CAPABILITY_KEYS = _SHAREABLE_CAPABILITY_KEYS\` means \`share_model_providers: true\` today shares four scopes, but any capability added to the shareable set next quarter is *automatically* granted to every existing boolean-opted-in config — silent privilege expansion across a trust boundary. Suggestion: freeze the boolean default as an explicit tuple ("the v1 default set") independent of the superset, and/or version the block (\`schema_version: 1\`) so widening requires a conscious config edit. This is the one change I'd insist on before wiring exists.

- **profile_provider_sharing.py:~168-175 — placeholder extraction only accepts the exact full-string \`${VAR}\` form.** A custom provider declaring a base_url like \`https://${ACME_HOST}/v1\` contributes *nothing* to the share scope, so the declared contract under-reports what runtime will actually need (and the failure mode is silent). Either document "only whole-value placeholders count" prominently, or scan with \`finditer\` so embedded placeholders register too.

- **Strictness asymmetry between sections.** Unknown capability names raise immediately, but \`custom_provider_share_env_vars\` (~lines 185-200) silently skips non-Mapping entries and empty fields — a YAML indentation slip that turns a provider entry into a string drops its env vars from the share scope with zero signal. Suggestion: raise (consistent with the rest) or at minimum log a warning naming the offending entry.

- **Document the participating field set.** The custom-entry scanner reads exactly \`key_env\`, \`api_key_env\`, and base_url/url/api placeholders. Since this module *is* the reviewable contract, enumerate those fields in the docstring (and state explicitly that literal inline keys and headers-based auth are out of scope) so follow-up wiring can't quietly widen it.

- **profile_provider_sharing.py:35 — name validation permits oddities that become paths later.** \`.hidden\`, \`a..b\`, and Windows-reserved names (CON, NUL) pass \`_PROFILE_NAME_RE\`; harmless today, but this is explicitly destined to become a profile directory reference in the follow-up. Worth tightening there (or noting the TODO now).

- **tests/hermes_cli/test_profile_provider_sharing.py — small gaps.** Untested: mapping form with \`enabled: false\` resolving disabled, profiles present but not a Mapping, \`source_profile: "."\` rejection, and the current skip-don't-raise behavior for malformed custom entries (pin whatever point 3 lands on).

Nit: profile_provider_sharing.py:14 — \`logger_name = __name__\` is assigned but never used; drop it or wire up a module logger when warnings arrive.
