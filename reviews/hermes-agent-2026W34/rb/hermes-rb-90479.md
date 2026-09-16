> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Three solid restorations in one: (1) the payload-ID dedup fallback is carefully bounded — route-scoped via JSON array encoding, scalar-only with bool/empty rejection, and strictly *below* trusted delivery headers, with tests proving both single-invocation retries and header-priority preservation plus an explicit no-secret/no-payload-leak assertion; (2) provider signature support (Linear/Attio/\`X-Signature\`) keeps the commit-to-V2 semantics intact — malformed V2 still never downgrades to body-only V1 — and \`removeprefix("sha256=")\` normalization matches what most emit; any attacker-supplied extra header can only cause additional strict comparisons, so mixed-header games fail closed; (3) the GET readiness endpoint deliberately touches none of the POST pipeline (no auth/rate/dedup/agent), verified by state-preservation assertions.

One design point to make explicit:

- **gateway/platforms/webhook.py:~527 (`_handle_webhook_readiness`) is an unauthenticated route-name oracle.** A 200-vs-404 difference lets anyone probe whether \`/webhooks/<name>\` exists. Since the POST path treats knowing the route name as necessary-but-insufficient (signature still required), the leak is low-severity — but route names sometimes embed tenant hints. Consider documenting "treat route_name as a credential component" alongside the endpoint, or returning a constant-status/generic body for unknown routes too (404 with identical shape still distinguishes). The profile-multiplex variant at least gates on configured profiles first, which is good.

Nit: the V2 comment block lost some of its original rationale (the mixed-header downgrade attack walkthrough) in this refactor — that reasoning is exactly what stops a future cleanup from re-nesting the V2 check inside \`if generic_sig:\`; worth preserving somewhere.

No blocking issues found.