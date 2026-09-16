> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Correctly scoped fix for a real reply-continuity hole: script-provisioned ("managed") crons never capture an origin, so deliver=origin silently fell back to the home channel while the June origin-scoping refactor refused to mirror it - brief delivered, replies context-less. The provenance-tag design is clean: eligibility decided at resolution time (`_resolved_from`), ranked OR-merge on dedup so token order cannot strip eligibility ("origin,all" vs "all,origin" both tested), the global flag explicitly NEVER activates plain explicit targets (only the per-job attach_to_session opt-in does), broadcasts stay unmirrored, and the in_channel seed refuses user-less group targets that would orphan a session no reply resolves to. The end-to-end tests drive _deliver_result through a stubbed registry and assert both the field repro (fallback mirrors) and all the negative shapes.

- Nit: `_resolved_from` now rides on every resolved target dict; if anything downstream ever serializes these targets verbatim (job audit logs, dashboards rendering delivery plans) the internal key becomes visible - harmless, just worth knowing before someone builds UI on it.

- Nit: `attach_to_session: true` on an explicit target moves trust from configuration to the job author; the tool description updated nicely, but a one-line docs note in the cron feature page stating "the job author declares the explicit target a conversation" would round it out.

No blocking issues found.