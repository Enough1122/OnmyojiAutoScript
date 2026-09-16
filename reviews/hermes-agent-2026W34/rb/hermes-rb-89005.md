> AI code review — automated review for reference; please use your judgment.

Correct fix: an explicitly configured `default` was being conflated with "unset", so the resolver fell through to derive a profile from the SSH pool key (`mac-mini`) instead of honoring the user's choice of the remote's own default profile. Treating any non-empty configured value as authoritative (mapping `default` → empty for the remote) matches user intent, and the new assertion pins exactly the case that used to misresolve.

1. apps/desktop/electron/connection-config.ts:~222 — worth one comment distinguishing the three states (empty=unset → derive; `default`=explicit default → ``; anything else=named profile) since the old behavior trained nobody to expect this. (nit)
2. Behavior note for release notes: anyone who relied on `default` meaning "derive from pool key" will see the remote default profile used instead — almost certainly what they wanted anyway. (nit)

No blocking issues found.
