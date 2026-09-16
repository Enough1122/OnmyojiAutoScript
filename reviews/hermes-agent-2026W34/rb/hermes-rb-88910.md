> AI code review — automated review; please use your judgment.

Two well-motivated fixes in one PR, both cleanly executed:

- `hermes update --reset-state` closes a real operational gap (no supported way to stop the post-failure retry loop after manual repair). The implementation is appropriately paranoid: update-lock guarded, gated on the **strict** venv health probe so "probe couldn't run" no longer counts as healthy when affirmative proof is required, marker removal verified after the fact, and both success and failure paths tested including the exact probe kwargs.
- The `DaemonThreadPoolExecutor` 3.14 compatibility branch detects `_create_worker_context` instead of version-sniffing, keeps the legacy four-arg layout for ≤3.13, and the new test pins both the worker startup and initializer contract so the private-API change can't regress silently.

Nit (`hermes_cli/main.py` `_reset_update_recovery_state`): output mixes plain `print` with the ✓/✗ prefixed style used elsewhere in update flows — consistent, just noting the failure message embeds the remediation hint (````hermes update --reset-state````) which is helpful. No changes needed beyond awareness; alternatively route through the same reporting helper the updater uses so formatting stays uniform.

— reviewer-a · automated agent review (Hermes week-review)
