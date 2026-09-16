> AI code review — automated review for reference; please use your judgment.

Review of "fix(provider): expose DeepInfra env vars". Additive and consistent with neighboring provider entries (password-masked key, advanced category, optional base-URL override). One verification item:

- config_defaults.py is metadata only — confirm the runtime side actually consumes `DEEPINFRA_BASE_URL` as an override in the DeepInfra resolution path (the sibling entries suggest the wiring exists; just making sure this isn't advertising a knob that's read nowhere).
