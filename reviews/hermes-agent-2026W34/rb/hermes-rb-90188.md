> AI code review — automated review for reference; please use your judgment.

Review of "feat(web): keyless local extract provider (httpx + trafilatura)". This is how a local-origin fetcher should be built: manual redirect loop with SSRF AND website-policy checks re-run on EVERY hop, 10MB streamed body cap feeding lxml, content-type allowlist with typed hand-off suggestions, honest UA with product token, trafilatura used purely as an in-memory extractor (its own networking never invoked) via the allowlisted lazy install, and a test transport hook. The docstring alone documents the threat model better than most code comments. Suggestions:

1. provider.py (DNS-rebinding TOCTOU) — `is_safe_url` resolves the hostname at CHECK time and httpx resolves again at REQUEST time; an attacker-controlled DNS name can answer differently between the two and land the fetch on an internal address despite passing the gate — if `is_safe_url` doesn't already pin addresses, either resolve once and connect by literal IP (with Host header), or state this residual explicitly in the module docstring so future maintainers know it's a known trade-off rather than an oversight.

2. provider.py:_fetch_readable (meta-refresh blind spot) — only HTTP 3xx hops are followed and re-checked; HTML `<meta http-equiv="refresh">` and JS redirects return the STUB page's extracted text (usually empty → "No readable content" error) — acceptable v1 behavior, but worth a comment so it isn't misread as an extraction bug.

3. nit — `text/plain` bodies skip trafilatura entirely and are returned whole (capped at 10MB); consider a smaller cap for raw-text passthrough since plain files can be logs of arbitrary size that then flow into context wholesale.
