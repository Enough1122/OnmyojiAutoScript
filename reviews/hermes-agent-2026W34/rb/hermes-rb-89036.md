> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): layout reset clears session tiles in every profile". Correct fix for a self-undoing reset: per-profile tile persistence meant inactive profiles re-adopted saved splits on the next gateway swap, so a reset held only until the first bot click. `clearInactiveProfileTiles` prunes exactly the non-live entries from PERSISTED storage while leaving the live atom to the normal stacking handler, skips secondary windows, and persists only on change; tests cover both the immediate prune and the swap-after-clear simulation via module re-import. Suggestions:

1. session-states.ts (design confirm) — this makes one profile's reset DESTRUCTIVE to other profiles' saved layouts without those sessions being open or consulted; that matches "reset restores the whole window," but it is silent data loss for someone who curated profile B's tiles and reset in profile A — worth either a confirm-dialog mention ("this clears tiles for all profiles") or a one-shot backup of the pruned map before deletion.

2. nit — the function reads the live profile through `profileKey()`; if a gateway swap races the reset (profile changed between stack and prune), the wrong set could be pruned — cheap to snapshot the active key once at reset start and pass it in.
