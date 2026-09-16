> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Pragmatic fix for the #90952 wedge: treating a terminal \`session/update\` as an authoritative turn end — rather than waiting indefinitely for an id-matched \`session/prompt\` result that opencode v1.18+ may never deliver — unblocks gateway async runs while the control test proves plain chunks alone still wait for the real result. The case-insensitive state matcher and the \`session/prompt\`-only gating keep the blast radius tight.

Points to consider:

- **agent/copilot_acp_client.py:~703 — the fallback requires non-empty \`text_parts\`.** A turn that ends entirely in tool calls (no final assistant text — common for pure-action prompts) produces no text parts, so a wedged transport still hangs until timeout even though \`turn_complete\` arrived. If the terminal update is authoritative, it arguably is regardless of whether text was emitted; at minimum consider also accepting non-empty \`reasoning_parts\` or tracked tool-use activity, and note the remaining gap in the comment.

- **The synthetic return discards the terminal update's own payload.** \`content: []\` plus \`completed: True\` works only because callers read the mutated \`text_parts\`/\`reasoning_parts\` lists; worth confirming no consumer branches on result \`content\` emptiness (e.g., to decide "no output"). Also, real results carry richer stop metadata (\`stopReason\`) used elsewhere for telemetry — when the fallback fires, consider stashing \\"completedViaTerminalUpdate\\": true (or the update kind) into the return so metrics can distinguish wedged-recovery from clean completion.

- **State vocabulary is a cross-vendor superset** (\`turn_complete/turn_finished/complete/finished/done\`). Fine as a heuristic, but if a server ever emits \\"done\\\" for a non-turn event the prompt would end early with whatever partial text exists. The docstring's framing ("opencode ACP v1.18+") suggests pinning to observed spellings first and widening only with evidence.

No blocking issues found.