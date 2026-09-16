> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Correct fail-closed semantics: explicitly requested cpu/memory limits combined with a failed controller-delegation probe now raise an actionable isolation-unavailable error instead of silently running a container without the requested bounds - the exact gap where "I asked for bounded execution" quietly became unbounded. The no-limits-requested path deliberately keeps working (nothing to drop), both trigger shapes are tested, and hoisting the probe into `_limits_available` also removes the old triple re-invocation.

Nit: the error message suggests `--cap-add` for controller delegation - device/cgroup-controller delegation is really a runtime/LXC config or systemd property concern rather than a cap-add; tightening the hint would save users a wrong turn.

No blocking issues found.