> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Good snapshot refresh with honest versioning (`deepseek-pricing-2026-08`, source URL, and the alias history preserved), and tests track the new numbers. One design question worth resolving before merge:

1. agent/usage_pricing.py:512 — the table stores **off-peak** rates while the comment notes peak windows (weekdays 09:00–12:00 & 14:00–18:00 Beijing) run at **2x**. Since `PricingEntry` has no time dimension, every cost estimate computed during peak hours will silently understate spend by 2× — for a usage-*pricing* module that's a systematic error, not a rounding one. Options in order of fidelity: implement the Beijing-time multiplier in the cost path; add a second peak `PricingEntry` variant selected by clock; or at minimum tag these entries (`note="off-peak"`) and document that peak costs are understated so downstream displays can caveat.
