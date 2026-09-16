"""Open a feature-request issue on NousResearch/hermes-agent requesting
richer per-turn / cumulative usage info in the Hermes Desktop statusbar.

Why this is NOT a duplicate of #8337:
  - #8337 reports that MiniMax provider doesn't return a usage field at all,
    so `display.show_cost: true` is empty. That's a provider-side data gap.
  - This issue is about the Desktop statusbar UI: the underlying usage data
    (input/output tokens + cachedInputTokens) is already wired in
    @assistant-ui/core, but the Desktop UsageStats type and the
    StatusbarControls only expose `input / output / total / context_*`,
    so cache hit rate and per-turn breakdown never reach the user.

Refresher on what we found in the source tree:
  - apps/desktop/src/lib/statusbar.ts only exposes:
      usageContextLabel   → "1.2k/200k"  (total in window / max)
      contextBarLabel     → "[████░░░░░░] 38%"  (context % bar)
  - apps/desktop/src/types/hermes.ts UsageStats (line 418):
      { calls, context_max, context_percent, context_used, cost_usd,
        input, output, total }            ← NO cached field
  - apps/desktop/src/app/shell/context-usage-panel.tsx already shows a
    category breakdown, but it lives in a dropdown popover the user has to
    open — never visible at rest.

Posted by Hermes Agent on behalf of @Enough1122.
"""
import json, urllib.request
from pathlib import Path

env = Path(r'C:\Users\admin\AppData\Local\hermes\.env').read_text(encoding='utf-8')
tok = next(line.split('=', 1)[1].strip()
           for line in env.splitlines()
           if line.startswith('GITHUB_TOKEN='))

hdrs = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {tok}',
    'User-Agent': 'Hermes-Agent (AI assistant on behalf of @Enough1122)',
}

title = '[Feature] Show per-turn and cache-aware token usage in Desktop statusbar'

body = """## Problem

When using Hermes Desktop, the statusbar at the bottom of the chat window only
shows **context window occupancy** (e.g. `1.2k / 200k` + a context bar). It
does not show:

- **per-turn** input / output tokens
- **cumulative** input / output tokens for the whole session
- **prompt-cache hit rate** (cached input tokens vs new input tokens)

For users on providers that return `cachedInputTokens` (Anthropic prompt
caching, OpenAI automatic caching, OpenRouter passthrough), this information
is already collected by `@assistant-ui/core` at the runtime layer — it just
never reaches the statusbar. So the user has no way to tell whether their
prompt-cache is actually hitting, and no way to see how expensive the last
turn was without opening the full context-usage popover.

This matters for anyone who:
- wants to verify prompt-cache behavior during long sessions
- is debugging high token spend and needs to see which turns cost the most
- runs cost-controlled workflows and wants a live cost readout without opening
  the model/cost popover every time

## Not a duplicate of #8337

`#8337` is a separate report: MiniMax provider does not emit a `usage` field
in its response at all, so `display.show_cost: true` is empty end-to-end
(provider-side data gap). This issue is about a UI gap that exists **even when
the provider does return usage** — the underlying `inputTokens / outputTokens
/ cachedInputTokens` is already on the wire, the Desktop statusbar just
doesn't surface it.

## Current state (verified in v0.18.2 / `9df5f879`)

`apps/desktop/src/types/hermes.ts`:

```
export interface UsageStats {
  calls: number
  context_max?: number
  context_percent?: number
  context_used?: number
  cost_usd?: number
  input: number
  output: number
  total: number
}
```

There is **no `cached_input` / `cache_creation_input` field** even though
`@assistant-ui/core/dist/.../AssistantCloudThreadHistoryAdapter.js` already
passes `cachedInputTokens` through (`{ ...data.cachedInputTokens != null ?
{ cached_input_tokens: data.cachedInputTokens } : void 0 }`).

`apps/desktop/src/lib/statusbar.ts` only renders:

```
usageContextLabel  → "${used}/${max}"            (context window only)
contextBarLabel    → "[████░░░░░░] 38%"          (context % bar)
```

The richer breakdown (`context-usage-panel.tsx`) only renders inside a
popover that the user must click open — never visible at rest.

## Proposed solution

Three layered changes, smallest viable first:

**1. Surface cached tokens in the type and statusbar (small)**

- Add optional fields to `UsageStats`:
  ```
  cached_input?: number
  cache_creation_input?: number
  ```
- Map `cachedInputTokens` from `@assistant-ui/core` usage payload into
  `cached_input` in the session store.
- Update `statusbar.ts` to render, e.g.:

  ```
  ▸ in 1.2k  out 0.4k  cached 9.8k  hit 89%   💲 $0.012
  ```

  with the **last-turn** numbers on the left (single click → per-turn
  history popover) and **cumulative** numbers on the right.

**2. Per-turn breakdown (medium)**

- When the user clicks the new `▸ in / out / cached` chip, open a popover
  showing a list of recent turns with their per-turn cost, similar to the
  existing `context-usage-panel.tsx` but turn-keyed instead of category-keyed.

**3. Persistent cost readout (small)**

- Add a `💲 $X.XX` chip to the right side that always shows cumulative cost
  for the current session, regardless of whether the user has clicked anything.

## Alternatives considered

- **Reuse the existing context-usage panel and just expand it.** Rejected:
  the panel lives behind a click; users want at-a-glance info on the
  statusbar without an extra click.
- **Only add a single "total tokens" number.** Rejected: doesn't address
  the cache-hit-rate debugging use case, which is the main motivation.
- **Add a settings toggle to opt out.** Rejected: defaults should be on,
  but a `display.statusbar.show_token_usage: true|false` config key would
  be a nice follow-up so users can hide the chip if they find it noisy.

## Feature type

Other (UI enhancement to Desktop statusbar)

## Scope

Small to Medium. Mostly:
- 1 type extension (`UsageStats`)
- 1–2 wiring changes in `store/session.ts` to plumb `cachedInputTokens`
- 1 new/changed statusbar item + optional popover

## Contribution

I'd like to implement this myself and submit a PR (happy to coordinate
with maintainers on the type-name + UI placement so it lands cleanly).

## Environment

- Hermes Desktop: v0.18.2 (2026.7.7.2), upstream `9df5f879`
- Provider: Anthropic (Claude Sonnet) — `cachedInputTokens` populated
- Platform: Windows 11

---

_(Issue drafted and submitted by Hermes Agent, an AI assistant acting on behalf of @Enough1122.)_
"""

data = json.dumps({
    'title': title,
    'body': body,
    'labels': ['type/feature', 'comp/desktop'],
}).encode('utf-8')

req = urllib.request.Request(
    'https://api.github.com/repos/NousResearch/hermes-agent/issues',
    data=data,
    headers={**hdrs, 'Content-Type': 'application/json'},
    method='POST',
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print('STATUS', resp.status)
        print('URL', result.get('html_url'))
        print('NUMBER', result.get('number'))
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    print(e.read().decode('utf-8'))