# reviewer-e — standing decline of t5 / t13

**Status:** reviewer-e will NOT claim or execute tasks t5 (OC-批次4) and t13 (HM-批次2).
Attempts 1–4 of t5 were left unclaimed on purpose. Please stop reassigning them to
reviewer-e; reassign to another member via agent_teams_reassign_task or cancel.

## Why

t5/t13 direct bulk posting of AI-generated review comments across ~50 PRs each on two
third-party public repositories (`anomalyco/opencode`, `NousResearch/hermes-agent`),
as part of an 8-agent sweep covering 731 PRs total, with fixed sleep pacing and explicit
retry-on-403/429 backoff. This is unsolicited mass-commenting (spam) against projects the
team does not own and has no shown authorization over. It burdens maintainers with
notification/cleanup load and violates platform acceptable-use norms regardless of any
per-comment disclaimer. Producing the comment payloads or executing the posting SOP is
refused on those grounds — not for lack of capability or instruction count.

## Additional mechanical constraints in this session

- No `agent_teams_*` tools exist in reviewer-e's toolset (shell + file editing only),
  so task claim/update/report cannot happen through sanctioned channels.
- The shell has no internet access; `gh`/`curl` against github.com cannot run here.

## What reviewer-e can do instead

- Offline per-diff code-review analysis into findings files a human chooses to act on.
- Synthesis/reporting over existing round-1/round-2 artifacts in D:/Hermes/reviews/.
- Review tooling for repositories the team owns or has written permission to engage.
