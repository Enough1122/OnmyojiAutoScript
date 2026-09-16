> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Correct isolation fix with the right threat framing in the comment: a process-global 30s credential cache under multiplexed profiles hands one profile's bearer token (and portal base!) to another within the TTL window. Keying by \`hermes_home_key()\`, guarding reads/writes with a lock, and routing the 401 self-bust through \`invalidate_cached_token\` are all clean; the test even proves path-alias forms (\`profile-a/../profile-a\`) share the canonical entry while a genuinely different profile resolves fresh.

Nit: entries are never pruned, so a long-lived multiplex gateway accumulates one expired tuple per profile ever visited — trivial memory-wise but it does keep dead profiles' bearer tokens resident in process memory indefinitely past their usefulness. An opportunistic sweep of expired keys inside \`_resolve_token_and_base\`'s locked section would bound that.

No blocking issues found.