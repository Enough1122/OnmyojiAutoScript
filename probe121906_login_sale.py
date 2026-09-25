import hermes_cli.auth as auth
import hermes_cli.auth_nous as auth_nous
import hermes_cli.models as models
import hermes_cli.models_pricing as pricing

sale = {
    "prompt": "0.2",
    "completion": "0.2",
    "original": {"prompt": "1.0", "completion": "1.0"},
}
full = {"prompt": "1.0", "completion": "1.0"}

models.get_curated_nous_model_ids = lambda: ["curated/only"]
models.check_nous_free_tier = lambda **kwargs: False
models.fetch_nous_recommended_models = lambda *a, **k: {"paidRecommendedModels": []}
pricing.get_pricing_for_provider = lambda *a, **k: {
    "curated/only": full,
    "vendor/sale": sale,
}
pricing.nous_policy_allowed_ids = lambda **k: None

seen = []
def fake_prompt(model_ids, **kwargs):
    seen.append(list(model_ids))
    return model_ids[0] if model_ids else None
auth._prompt_model_selection = fake_prompt

selected = auth_nous._pick_nous_model_after_login(
    {"access_token": "test-token", "portal_base_url": "https://portal.example"},
    "https://inference.example",
)
print({"selected": selected, "picker_model_ids": seen[0] if seen else None,
       "sale_present": "vendor/sale" in (seen[0] if seen else [])})
