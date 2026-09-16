> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Correct scoping of the 10 GiB cap to Daytona Cloud only, with the endpoint resolution centralized in one helper that both the environment and \`hermes doctor\` consume (the doctor output helpfully distinguishes Cloud vs self-hosted and, per the new test, never echoes the API key). The four-way test matrix — default cloud, explicit cloud, self-hosted via \`DAYTONA_API_URL\`, and the legacy \`DAYTONA_SERVER_URL\` — pins exactly the behaviors that matter, and the fixture now clearing both env vars fixes latent cross-test leakage. Docs updated in three places consistently.

One edge worth deciding deliberately:

- **tools/environments/daytona.py:~41 (`is_daytona_cloud_endpoint`) — exact string equality is brittle for "is this Cloud."** A Cloud endpoint reached via a corporate proxy URL, an explicit default port (\`:443\`), or any path suffix (\`/api/v1\`) classifies as *self-hosted*, so the protective cap is skipped and oversized requests surface later as opaque Cloud API errors instead of the clean warning+cap. Suggest classifying on \`urlparse(api_url).hostname == "app.daytona.io"\` (scheme-insensitive, port/path-tolerant) while keeping the equality check for the doctor's friendly label.

Nit: the docs table documents \`DAYTONA_TARGET\`, which this PR doesn't read directly (the SDK consumes it) — fine, just noting the resolver intentionally mirrors only two of the three SDK vars, so a future SDK rename needs a matching edit here.

No blocking issues found.