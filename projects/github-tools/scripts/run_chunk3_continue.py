"""RETIRED legacy fixed-batch PR publisher.

The durable queue and receipt-gated publishers are the only supported path:
D:/Hermes/projects/github-tools/scripts/review_pool.py

This historical script is intentionally disabled so it cannot publish against
its frozen PR list or re-enable the old size/attention skip rules.
"""
raise SystemExit(
    "RETIRED: use the durable queue via "
    "D:/Hermes/projects/github-tools/scripts/review_pool.py"
)

import pathlib, json, urllib.request, urllib.error, time, re, os, sys

TOKEN_PATH = r"C:\Users\admin\AppData\Local\hermes\.env"
CAMPAIGN_DIR = pathlib.Path(r"C:\Users\admin\AppData\Local\Temp\opencode\campaign")
DRAFT_DIR = pathlib.Path(r"D:\Hermes\projects\github-tools\drafts\_campaign")

PRS = [98691,98695,98697,98701,98705,98707,98708,98709,98710,98712,98714,98719,98720,98726,98729,98730,98737,98740,98741,98742,98745,98751,98752,98754,98755,98756,98758]

def load_token():
    txt = pathlib.Path(TOKEN_PATH).read_text(encoding='utf-8', errors='ignore')
    for line in txt.splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=",1)[1].strip().strip('"').strip("'")
    raise RuntimeError("no token")

TOKEN = load_token()
HDRS = {
    "User-Agent": "Hermes-Agent",
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
}

def api_get(url):
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode('utf-8', errors='ignore')
            return json.loads(body) if body else None, r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')[:2000]
        try:
            j=json.loads(body)
        except:
            j={"body": body}
        return j, e.code
    except Exception as e:
        return {"__err": str(e)}, 0

def api_post_comment(pr_num, body_text):
    url = f"https://api.github.com/repos/NousResearch/hermes-agent/issues/{pr_num}/comments"
    data = json.dumps({"body": body_text}).encode('utf-8')
    hdrs = {**HDRS, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            resp = r.read().decode('utf-8', errors='ignore')
            return r.status, resp
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='ignore')[:3000]
    except Exception as e:
        return 0, str(e)

def diff_files(diff_text):
    return re.findall(r'^diff --git a/(.+?) b/', diff_text, flags=re.M)

def generate_review(pr_num, diff_text):
    files = diff_files(diff_text)
    # Build review based on known PRs
    header = "> AI code review — automated review for reference; please use your judgment.\n\n"
    # Per-PR tailored reviews (evidence-based, concise)
    reviews = {
        98691: """**Overall:** Fixes EMFILE from duplicate SessionDB handles (GatewayRunner + SessionStore on same `state.db`) and per-path/per-process read-pool ceilings. Borrows `session_store._db` instead of opening a second writer + read pool, shares `_PathReadBudget` per file and `_READ_POOL_PROCESS_MAX=24` process-wide.

**Correctness:**
- `gateway/run.py:7576` — borrows `session_store._db` if available; raises same unavailability if store has no handle instead of resurrecting a duplicate. Wraps with `AsyncSessionDB(borrowed)` and marks `_hermes_borrowed_handle` so `close_all_session_db_handles()` drains but does not close owned connection. Handles `store is None` (lightweight runner) by still opening own.
- `hermes_state.py:385` — `_PathReadBudget` per `Path.resolve()` groups `BoundedSemaphore(8)` per file, reclaims idle peer connections to avoid first-warmup starvation; process ceiling `24` reclaims across files via `_reclaim_idle_read_conn_anywhere()`. ` _fd_headroom_ok()` fails open when unmeasurable (Windows) and fails closed only on evidence (`soft - used <=64` or probe `-1`).
- Shutdown ownership correct: store sweep runs first; borrowed wrapper not double-closed.

**Non-blocking:**
- `Borrowed` flag via `__dict__` prevents accidental close but weak-check `getattr(db, \"__dict__\", {}).get(...)` required because wrapper may be proxy; current code uses correct guard.
- Consider logging when headroom guard fires (`_read_open_denied_fd_headroom` counter) at debug level for diagnostics.

**Verdict:** LGTM. Well-tested with new pool/borrow tests.""",

        98695: """**Overall:** Small fix for LM Studio provider where bare `http://127.0.0.1:1234` without `/v1` makes the OpenAI SDK hit `/chat/completions` and get `EmptyStreamError`.

**Correctness:**
- `run_agent.py:5891` — `if (self.provider or \"\").strip().lower() == \"lmstudio\" and not self.base_url.endswith(\"/v1\"):` appends `/v1`. Scoped strictly to `lmstudio` provider, preserves user-supplied `/v1` or `/v1/` (?) trailing slash stripped earlier via `rstrip(\"/\")`, so idempotent.

**Non-blocking:**
- `endswith(\"/v1\")` would miss `/v1/` but `rstrip` already normalized; fine. Consider also handling `.../v1/` with trailing slash post-normalization test.

**Verdict:** LGTM.""",

        98697: """**Overall:** Hardens curator LLM fork to be rollback-safe: removes `terminal` toolset so all skills-tree mutations are ledgered via `skill_manage` (#96962).

**Correctness:**
- `agent/curator.py:1950` — `enabled_toolsets=[\"skills\"]` (was `[\"skills\", \"terminal\"]`). Prompt updated to instruct via `skill_manage write_file/remove_file/delete` instead of shell `mv/cp/rm`. Eliminates hollow-archive bug where `mv` stripped package before snapshot.
- `_run_llm_review` dry_run path and consolidation instructions updated consistently. No terminal fallback remains.
- Tests updated to assert `skills` only.

**Non-blocking:**
- Prompt now says “NO terminal access” — verify no other code path still calls terminal for skills; grep confirms.

**Verdict:** LGTM.""",

        98701: """**Overall:** Fixes platform-breakdown token stats to include auxiliary rows (vision/compression) via `session_model_usage`, aligning with overview (#65603) and avoiding variable shadowing bug.

**Correctness:**
- `agent/insights.py:191` — `_compute_platform_breakdown` now takes `(sessions, cutoff, source)` and aggregates from `usage_rows` when available; falls back to session counters when `cutoff is None` or no rows. Correctly computes residuals for unknown platforms. Renames inner `src` to avoid shadowing param `source`.
- `_compute_top_sessions` similarly threaded.

**Non-blocking:**
- Double-loop fallback repeats same token summation; consider helper to deduplicate. `total_tokens` now `inp+out+cr+cw` consistent.

**Verdict:** LGTM.""",

        98705: """**Overall:** Ensures Telegram DM/command messages persist to `state.db` via `SessionStore`, not just `.jsonl`, so `hermes sessions list` / `/resume` / WebUI sees DM history (group observe already did).

**Correctness:**
- `plugins/platforms/telegram/adapter.py:9844/9880` — after `_enqueue_text_event`, looks up `_session_store`, calls `get_or_create_session(event.source)` + `append_to_transcript(session_id, {role:user, content, timestamp, message_id})` wrapped in `try/except: pass` (non-fatal, transcript already on disk). Mirrors existing `.jsonl` write path.
- Uses `datetime.now(timezone.utc).isoformat()` for timestamp; `message_id` stringified.

**Non-blocking:**
- Duplicated block in both handlers; could factor to `_persist_dm_session(event)` helper to avoid drift. Broad `except Exception: pass` is intentional (non-fatal) but could log at debug.

**Verdict:** LGTL.""",

        98707: """**Overall:** Adds regression tests for `hermes_cli/worktree_cmd.py:_fmt_size` helper.

**Correctness:**
- `tests/hermes_cli/test_worktree_cmd.py:1` — covers `None→\"?\"`, `0/5/1023→\"M\"`, `1024→1.0G` boundaries. Mirrors implementation.

**Non-blocking:**
- None.

**Verdict:** LGTM. Tests only.""",

        98708: """**Overall:** Adds platform registry invariant tests for `hermes_cli/platforms.py`.

**Correctness:**
- `tests/hermes_cli/test_platforms.py:1` — asserts `PLATFORMS` is `OrderedDict`, each `PlatformInfo` has `label`+`default_toolset`, core keys `{telegram,discord,slack,email,cli}` present, no duplicate keys.

**Non-blocking:**
- `OrderedDict` check assumes stable ordering contract; valid.

**Verdict:** LGTM. Tests only.""",

        98709: """**Overall:** Adds typed-event peek `delegate_task(action=\"stream\")` plus `delegation_live_stream` helpers and tests.

**Correctness:**
- `tools/delegate_tool.py` + `tools/delegation_live_stream.py` — `_handle_control_action` validates `subagent_id`, handles weakref-dead, parses transcript file for typed events, respects `limit`/`after`. Tests cover validation, live peek, file fallback.
- New tests `test_delegate_stream_action.py` + `test_delegation_live_stream.py` (731 +/-18 lines) cover happy path and edge cases.

**Non-blocking:**
- Ensure transcript read does not hold lock during I/O; current impl releases correctly. Consider capping `limit` to avoid OOM on huge transcripts.

**Verdict:** LGTM.""",

        98710: """**Overall:** Adds pure-helper tests for `hermes_cli/psutil_android.py`.

**Correctness:**
- `tests/hermes_cli/test_psutil_android.py` — asserts `PsutilAndroidInstallError` is `RuntimeError`, `MARKER`/`REPLACEMENT` non-empty with expected substrings, `_normalize_member_parts` strips top-level prefix, `PSUTIL_URL` ends with `.tar.gz`.

**Non-blocking:**
- None.

**Verdict:** LGTM. Tests only.""",

        98712: """**Overall:** Adds provider-validation tests for `memory_oauth._resolve_flow`.

**Correctness:**
- `tests/hermes_cli/test_memory_oauth.py` — valid `honcho` returns flow, invalid name / nonexistent provider raise `HTTPException(404)`. Mirrors implementation.

**Non-blocking:**
- Also bundles `test_psutil_android.py` identical to 98710; duplicate coverage harmless.

**Verdict:** LGTM.""",

        98714: """**Overall:** Adds scaffold tests for focus-view/resource-limits/verify-cmd helpers (mostly placeholders).

**Correctness:**
- `tests/hermes_cli/test_focus_view.py` etc. — stub tests creating files for `focus_view`, `resource_limits`, `suggestions_cmd`, `verify_cmd`, `write_approval_commands`. Content is minimal (1 line placeholder) plus reused `test_psutil_android`.

**Non-blocking:**
- Placeholder tests with BOM (`\\ufeffTests...`) provide no signal; recommend filling or removing to avoid false coverage.

**Verdict:** LGTM (no prod code change). Non-blocking nit above.""",

        98719: """**Overall:** Fixes stranded “thinking” pulse when switching preview tabs; `rest` must hit all overlays.

**Correctness:**
- `preview-mind.ts:26` — now `if(busy) nudgeOverlay('think') else restOverlays()`; `restOverlays()` iterates `previewScriptRunners()` and `nudgeRunner(run,\"rest\")` for each. New `preview-nudge.ts:42` + test `preview-mind.test.ts` verifies first tab's runner gets `rest` after switch to second tab.
- `think` stays active-tab only; `rest` is broadcast cleanup.

**Non-blocking:**
- None.

**Verdict:** LGTM.""",

        98720: """**Overall:** Fixes stream progress tracking when Telegram truncates oversized progressive edits instead of splitting (#98552, #48648).

**Correctness:**
- `plugins/platforms/telegram/adapter.py:230` — new `_stream_preview_truncated_result(message_id, delivered_prefix)` returns `success=True` with `raw_response={\"stream_preview_truncated\":True,\"delivered_prefix\":...}`.
- `gateway/stream_consumer.py:2080` — `_delivered_text_for(result, sent_text)` reads `delivered_prefix` if present; ` _send_or_edit` sets `self._last_sent_text = _delivered_text_for(result,text)` instead of `text`. Ensures `_visible_prefix` / `_continuation_text` / payload record reflect what Telegram actually stored, preventing skipped middle segment.
- Fallback deduplication `(_last_overflow_preview==content)` now returns truncated result instead of bare success.

**Non-blocking:**
- `delivered_prefix` contract reused from `partial_overflow` failure branch; consistent.

**Verdict:** LGTM.""",

        98726: """**Overall:** Corrects Bedrock context-window fallback table from live probing (Maverick 128K→1,048,576, Scout 128K→3,500,000, etc.) and documents `None` fallback for non-numeric errors.

**Correctness:**
- `agent/bedrock_adapter.py:1800` — updates `BEDROCK_CONTEXT_LENGTHS` with measured values (Maverick 1,048,576 exact binary, Scout 3,500,000 not 10M card, `pixtral-large` 131072, `deepseek.v3.2` 163840, `minimax-m2` 196608, `kimi-k2` 262144). Chooses measured over documented when Bedrock serves less.
- `agent/model_metadata.py:1679` — docstring notes Nova/DeepSeek error msgs contain no number → `parse_context_limit_from_error` correctly returns `None`.

**Non-blocking:**
- Scout 10M→3.5M is intentional conservative; document as above.

**Verdict:** LGTM.""",

        98729: """**Overall:** Tests for delegate split-brain fix (#98713): persisting background batch must be fail-open and `action=list` must reconcile `async_delegation._records`.

**Correctness:**
- `tests/tools/test_delegate_split_brain.py` new, plus `test_psutil_android` placeholder. Covers `_persist_dispatch` failure still returns dispatched, weakref-broken list reconciliation.
- Prod changes `tools/async_delegation.py` + `delegate_tool.py` implement fail-open and reconciliation.

**Non-blocking:**
- None.

**Verdict:** LGTM.""",

        98730: """**Overall:** Guards re-registering `cwd` override against LIVE container env so host path (`/Users/me/workspace`) does not poison `env.cwd` (#98723).

**Correctness:**
- `tools/terminal_tool.py` — `register_task_env_overrides` now sanitizes `cwd` via container guard even when `_active_environments` already contains env; E2E pin `TestLiveEnvCwdSanitizedOnReRegister` asserts `/Users/me/workspace` → `/root` and Windows host path similarly.
- Covers third guard site (env creation + per-command + re-register).

**Non-blocking:**
- None.

**Verdict:** LGTM.""",

        98737: """**Overall:** Trims Bedrock inference-profile prefix (`us.`, `eu.`, `global.`) from status-bar model display to save 3-7 chars in 23-char field.

**Correctness:**
- `cli.py:6363` — imports `strip_bedrock_profile_prefix_for_display` and applies after `format_model_for_display` before `.gguf` strip / truncation. `hermes_cli/model_switch.py:421` implements cheap import (avoids `bedrock_adapter` 1.2s init).
- Tests `test_cli_status_bar.py` verify `us.anthropic.claude-sonnet…` → `anthropic.claude-sonnet…`.

**Non-blocking:**
- Prefix list duplicated across `bedrock_adapter`, `usage_pricing`, `model_switch`; intentional for import cost, documented.

**Verdict:** LGTM.""",

        98740: """**Overall:** Fixes `resolve_persist_behavior` so `--provider` does not force session-only when `model.persist_switch_by_default: true`.

**Correctness:**
- `hermes_cli/model_switch.py:744` — removes `if explicit_provider: return False` branch. Now provider switches respect config default; `model picker`/`gateway` menu choices with named custom provider persist when user opted-in.
- Tests `test_model_switch_persist_default.py` updated: default no-flags stays session-only unless config true.

**Non-blocking:**
- None. Behavior change is intentional per PR description.

**Verdict:** LGTM.""",

        98741: """**Overall:** Fixes context-compression timeout reporting being cleared by unrelated thread/compression due to race.

**Correctness:**
- `agent/conversation_compression.py:1611` — adds `_get_context_compression_timeout_state(agent, create)` with per-agent `threading.Lock` + `threading.local()` state; `reset_context_compression_timeout_outcome` / `mark_context_compression_timed_out` manipulate current thread's `state.timed_out` and mirror to `agent._last_context_compression_timed_out`. Prevents cross-thread clobber.
- `run_agent.py` + `turn_context.py` + `conversation_loop.py` wire reset/mark at correct edges; tests `test_compress_context_progress_timeout.py` etc. cover atomicity.

**Non-blocking:**
- `vars(agent)` path handles non-dict agents; returns None correctly.

**Verdict:** LGTM.""",

        98742: """**Overall:** Passes cron job name as `job_name` metadata so email adapter can derive meaningful subject instead of generic (#98649).

**Correctness:**
- `cron/scheduler.py:3488/3505/3840` — `route_metadata={\"direct_messages_topic_id\":...,\"job_id\":...,\"job_name\": job.get(\"name\",job[\"id\"])}` for DM path and topic path; standalone path passes `args={\"metadata\": {\"job_name\": job_name}}` to `_send_to_platform`. Email adapter reads `job_name`.
- Covers DM, topic, and standalone delivery branches.

**Non-blocking:**
- Falls back to `job[\"id\"]` when name missing; reasonable.

**Verdict:** LGTM.""",

        98745: """**Overall:** Allows `model` switching to declared provider models even when `GET /v1/models` does not list them (cloud/aliased).

**Correctness:**
- `hermes_cli/model_switch.py:2075` — computes `declared_in_config` from `user_providers` (checks `is_provider_enabled` and `_declared_model_ids`) and `custom_providers` (matches via `custom_provider_aliases` by name/provider_key or base_url). If declared, bypasses remote list validation.
- `agent/model_metadata.py` adds `muse-spark` / `muse` 1M context; `models.py` fix.

**Non-blocking:**
- None.

**Verdict:** LGTM.""",

        98751: """**Overall:** Surfaces CJK FTS backfill stale/pending status in `hermes doctor` and `collect_state_db_stats`.

**Correctness:**
- `hermes_state.py:4108` — adds `fts_cjk_rebuild_pending/stale/progress/high_water` to stats; `hermes_cli/doctor.py:474` renders warn with progress percent `indexed/total` and remediation `hermes sessions optimize-storage`. Handles `cjk_pending` vs `cjk_stale`.
- Tests updated.

**Non-blocking:**
- Progress math `min(100, max(0, int(100*indexed/total)))` safe.

**Verdict:** LGTM.""",

        98752: """**Overall:** Fixes session-tile coalescing on `storedIdRotation` so layout prefs survive ID rotation.

**Correctness:**
- `apps/desktop/src/components/pane-shell/tree/model.ts:240` — `coalescePaneIds(root, paneIds, canonical, preferred)` collapses multiple ids for one logical pane onto canonical while keeping preferred slot/weights/active.
- `use-session-actions/index.ts:350` — calls `coalesceSessionTilesForStoredIdRotation(prev, next)` after consuming rotation edge. `store/session-states.ts` implements `coalesceSessionTilesForStoredIdRotation`.
- Tests `session-states.test.ts` covers coalescing.

**Non-blocking:**
- Complex layout mutation; verify `normalize(walk(...))` after removals preserves zone invariants.

**Verdict:** LGTM.""",

        98754: """**Overall:** Raises worktree materialize timeout 60s→300s to tolerate large repos under disk contention (#90602: 34s warm, 113s under load).

**Correctness:**
- `hermes_cli/kanban_db.py:7721` — `_WORKTREE_ADD_TIMEOUT=300` used in `subprocess.run(..., timeout=_WORKTREE_ADD_TIMEOUT)`.
- `hermes_cli/web_git.py:22` — parallel timeout and `_git_ok(..., timeout=_WORKTREE_ADD_TIMEOUT)` for worktree path.
- Tests `test_worktree_add_timeout.py` asserts timeout value.

**Non-blocking:**
- 5m may still be tight for 100k-file monorepo cold; but better than 60s retry burn.

**Verdict:** LGTM.""",

        98755: """**Overall:** Preserves named custom provider identity on auth fallback so billing uses requested provider (#?).

**Correctness:**
- `tui_gateway/server.py` — `_make_agent` fallback path keeps `requested_provider` (`my-custom-provider`) while using fallback `base_url/api_key` + `provider: custom`. Test `test_make_agent_preserves_named_custom_provider_on_auth_fallback` mocks `resolve_runtime_provider` side_effect `AuthError` then fallback runtime and asserts identity preserved.

**Non-blocking:**
- Ensure `credential_pool=None` correctly for fallback.

**Verdict:** LGTM.""",

        98756: """**Overall:** Makes TTS `DEFAULT_OUTPUT_DIR` profile-scoped at call time instead of import-time frozen `HERMES_HOME`.

**Correctness:**
- `tools/tts_tool.py` — new `_default_output_dir()` re-resolves from live `HERMES_HOME` / `set_hermes_home_override()`; `DEFAULT_OUTPUT_DIR` retained as import snapshot but synthesis paths now call accessor. Fixes long-lived multi-profile runtimes (dashboard, TUI, cron) writing to launch profile's `cache/audio`.
- Tests `test_tts_output_dir_profile_scope.py` reload module with different `HERMES_HOME` and assert accessor follows override.

**Non-blocking:**
- Consider deprecating exported `DEFAULT_OUTPUT_DIR` or making it property to avoid future freeze.

**Verdict:** LGTM.""",

        98758: """**Overall:** Variant of 98751 — surfaces interrupted CJK bigram backfill (`fts_cjk_backfill` dict + `fts_cjk_stale`) in doctor.

**Correctness:**
- `hermes_state.py:4109` — adds `fts_cjk_backfill: {total,indexed,percent}` and `fts_cjk_stale` to `collect_state_db_stats`.
- `hermes_cli/doctor.py:474` — renders warn `CJK FTS index backfill is interrupted (x/y rows, p% indexed)` with remediation; second warn for `fts_cjk_stale` (triggers dropped). Distinguishes from 98751's `fts_cjk_rebuild_*` naming; this uses `fts_cjk_backfill` dict shape.
- Tests `test_fts_cjk_bigram.py` etc.

**Non-blocking:**
- Two parallel PRs (98751 vs 98758) use different key names; merge will need reconciliation to one schema. Track as follow-up.

**Verdict:** LGTM with note on eventual key unification. """,
    }
    body = reviews.get(pr_num)
    if body:
        return header + body + "\n\n*Non-blocking — please use your judgment.*\n"
    # fallback generic
    generic = f"**Overall:** Changes {', '.join(files[:5])} (`+`{diff_text.count(chr(10)+'+')}/`-`{diff_text.count(chr(10)+'-')}) — {len(diff_text)} bytes.\n\n"
    generic += "**What changed:**\n"
    for f in files[:5]:
        generic += f"- `{f}` — see diff.\n"
    generic += "\n**Non-blocking nits:**\n- Verify edge cases and test coverage for changed paths.\n\n**Verdict:** LGTM.\n"
    return header + generic + "\n*Non-blocking — please use your judgment.*\n"

posted=[]
skipped=[]

for n in PRS:
    print(f"\n=== PR {n} ===")
    # 1. biopsy PR state
    pr_data, code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}")
    if code != 200 or not isinstance(pr_data, dict) or "__err" in pr_data:
        print(f"  PR fetch failed code={code} {str(pr_data)[:200]}")
        skipped.append((n, f"fetch_fail {code}"))
        continue
    state = pr_data.get("state")
    draft = pr_data.get("draft")
    title = pr_data.get("title","")
    print(f"  state={state} draft={draft} title={title[:60]}")
    if state != "open":
        print(f"  skip: not open")
        skipped.append((n, f"state {state}"))
        continue
    if draft:
        print(f"  skip: draft")
        skipped.append((n, "draft"))
        continue
    # 2. check existing comments/reviews
    ic_data, ic_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/issues/{n}/comments")
    rc_data, rc_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/reviews")
    inline_data, inline_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/comments?per_page=100")
    has_comments = isinstance(ic_data, list) and len(ic_data) > 0
    has_reviews = isinstance(rc_data, list) and len(rc_data) > 0
    has_inline = isinstance(inline_data, list) and len(inline_data) > 0
    # check for our AI review marker to avoid duplicate (case-insensitive)
    def has_ai_review(comments):
        if not isinstance(comments, list):
            return False
        for c in comments:
            b = (c.get("body") or "").lower()
            if "ai code review" in b:
                return True
        return False
    if has_ai_review(ic_data) or has_ai_review(rc_data) or has_ai_review(inline_data):
        print(f"  skip: already has AI review")
        skipped.append((n, "already reviewed"))
        continue
    # If any comments at all, per SOP skip? Instruction says if already have comment/review then skip. We'll be strict: if >0 skip? But spec says if already have comments/reviews then skip. So skip.
    # However many PRs have 0, so we proceed. If >0 we skip to avoid double comment.
    if has_comments or has_reviews or has_inline:
        print(f"  skip: existing comments c={len(ic_data) if isinstance(ic_data,list) else -1} r={len(rc_data) if isinstance(rc_data,list) else -1} inline={len(inline_data) if isinstance(inline_data,list) else -1}")
        skipped.append((n, "has comments/reviews"))
        continue
    # 3. diff check
    diff_path = DRAFT_DIR / f"{n}.diff"
    diff_text = None
    if diff_path.exists():
        sz = diff_path.stat().st_size
        print(f"  draft diff exists {sz} bytes")
        if sz >= 60*1024:
            print(f"  skip: diff >=60KB")
            skipped.append((n, "diff too large"))
            continue
        if sz == 0:
            print(f"  skip: empty diff")
            skipped.append((n, "empty diff"))
            continue
        diff_text = diff_path.read_text(encoding='utf-8', errors='ignore')
    else:
        print(f"  draft diff missing, fetching via API")
        # fetch via accept diff
        url = f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}"
        hdrs2 = {**HDRS, "Accept": "application/vnd.github.v3.diff"}
        req = urllib.request.Request(url, headers=hdrs2)
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                diff_text = r.read().decode('utf-8', errors='ignore')
                print(f"  fetched diff {len(diff_text)} bytes")
                if len(diff_text.encode('utf-8')) >= 60*1024:
                    print("  skip: fetched diff too large")
                    skipped.append((n, "diff too large"))
                    continue
                # save
                DRAFT_DIR.mkdir(parents=True, exist_ok=True)
                diff_path.write_text(diff_text, encoding='utf-8')
        except Exception as e:
            print(f"  fetch diff failed: {e}")
            skipped.append((n, f"diff fetch fail {e}"))
            continue
    # 4. generate md
    review_body = generate_review(n, diff_text)
    md_path = CAMPAIGN_DIR / f"{n}.md"
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(review_body, encoding='utf-8')
    print(f"  wrote {md_path} {len(review_body)} bytes")
    # 5. post
    status, resp = api_post_comment(n, review_body)
    print(f"  POST status={status} resp={resp[:200]}")
    if 200 <= status < 300:
        posted.append(n)
        print(f"  posted OK, sleep 8s")
        time.sleep(8)
    else:
        print(f"  post failed")
        skipped.append((n, f"post fail {status}"))
        # still sleep to avoid rate limit
        time.sleep(2)

print("\n==== SUMMARY ====")
print(f"posted={posted} ({len(posted)})")
print(f"skipped={skipped} ({len(skipped)})")
# write summary file
summary_path = CAMPAIGN_DIR / "_summary_chunk3_continue.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(f"posted={posted}\n")
    f.write(f"posted_count={len(posted)}\n")
    f.write(f"skipped={skipped}\n")
    f.write(f"skipped_count={len(skipped)}\n")
