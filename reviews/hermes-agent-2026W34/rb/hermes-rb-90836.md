> AI code review — automated review for reference; please use your judgment.

1. hermes_cli/doctor.py:1420 — the vendor-slug-accepting set grows by one hardcoded entry per aggregator (deepinfra, now commandcode; together/fireworks/groovy would each need the same patch). Why it matters: every new aggregator-style provider silently produces a false 'vendor/model slug' warning until someone edits doctor, which is exactly the class of drift this check exists to catch. Suggestion: move this to provider metadata instead — e.g. a catalog_style='vendor_slugs' attribute on ProviderConfig that doctor reads — so registering the provider registers its slug policy in one place.

2. Nice touch worth keeping: the inline comment records both the registry-id spelling ('commandcode', no hyphen) and sample catalog slugs, which is precisely what the next person grepping this set needs.
