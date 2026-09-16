> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

This closes a scary data-loss class with defense-in-depth done properly: a single `_PROTECTED_TOP_LEVEL` set now feeds both auto-tracking (`guess_category`) *and* the empty-dir sweep, so the two guards can never drift again; only explicitly plugin-owned ephemeral cache roots (`cache/vision/temp_vision_images`, `cache/video/temp_video_files`) are classified as temp — everything else under `cache/` is unmanaged by default; and stale tracked.json entries are re-validated across **all** auto-delete categories (not just cron-output/test as before) with unmanageable or out-of-HERMES_HOME paths dropped rather than deleted. The regression suite mirrors the incident classes (browser-profile blob_storage, vendor, benchmarks, plans) including empty-dir-sweep survival. One nit:

1. plugins/disk-cleanup/disk_cleanup.py:_PROTECTED_TOP_LEVEL — the chained set expression relies on left-to-right `-`/`|` precedence: `(_EMPTY_DIR_PROTECTED_TOP_LEVEL - {"cron", "cronjobs"}) | {...}`. It evaluates correctly today, but explicit parentheses (especially around the subtraction, given the NOTE about why cron is excluded) would keep a future editor from reordering into the wrong semantics.
