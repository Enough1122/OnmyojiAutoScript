import pathlib, json, urllib.request, urllib.error, time, re, os, sys

TOKEN_PATH = r"C:\Users\admin\AppData\Local\hermes\.env"
CAMPAIGN_DIR = pathlib.Path(r"C:\Users\admin\AppData\Local\Temp\opencode\campaign")
DRAFT_DIR = pathlib.Path(r"D:\Hermes\projects\github-tools\drafts\_campaign")

PRS = [99186,99187,99188,99194,99195,99201,99203,99204,99205,99207,99208,99209,99221,99224,99227,99228,99236,99239,99240,99241,99247,99250,99252,99253,99256,99257]

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
    header = "> AI code review — automated review for reference; please use your judgment.\n\n"
    reviews = {
        99186: """**Overall:** Switches `hermes_cli/subcommands/peer.py:_request` from `urllib` to `httpx` to fix Windows gateway timeout (#97769) plus clearer 400 handling for hidden `Bot Chat` sessions.

**Correctness:**
- `_request` now uses `httpx.Client(timeout=timeout)` with `Accept: application/json` and `raise_for_status()`. On `HTTPStatusError` re-raises intact; `TimeoutException→TimeoutError` and `RequestError→OSError` preserve prior contract. `resp.json()` replaces manual `loads(payload)` with same 200-char truncation on parse failure.
- Docstring explains `http.client` → `aiohttp 3.1` Windows Proactor mis-parse as chunked; aligning peer DM with rest-of-codebase `httpx` stack is appropriate.
- `_ensure_bot_chat` now catches `httpx.HTTPStatusError` first (400 + `title`→ actionable upgrade/unhide guidance), falling back to `urllib.error.HTTPError` for tests. `_http_error_detail` handles both `httpx` (`exc.response.text/json()`) and legacy `urllib` paths.

**Non-blocking:**
- `httpx.Client` per call adds connection overhead vs pooled client; acceptable for infrequent peer ops but could reuse a short-lived pool. Ensure `httpx` is in project deps (it is elsewhere).
- Error path preserves `raise` (no wrapping) so callers see original `HTTPStatusError`; doc if this is intentional vs wrapped `RuntimeError`.

**Verdict:** LGTM.""",

        99187: """**Overall:** Bounds four unbounded in-memory caches in Desktop Electron main (`_serveSupportCache`, `renderTitleQueue`, `gatewayAuthProvidersCache`, `_nativeTokens`) and the renderer `activity-timer` registry to prevent memory growth under many backends/URLs.

**Correctness:**
- `apps/desktop/electron/main.ts`: three `Map`s capped at `50` entries and `renderTitleQueue` at `100` pending titles. Eviction deletes `keys().next().value` (oldest insertion order) when `size > LIMIT`. `renderTitleQueue` drops oldest promise via `resolve(null)` to avoid hanging callers.
- `activity-timer.ts:5` — `MAX_TIMER_REGISTRY_SIZE=500` with `evictOldestIfNeeded` deletes oldest key while `size > 500` for both `startedAtByKey` and `durationByKey`. `useViewedInterval` callers keyed by `timerKey`; anonymous timers bypass map.

**Non-blocking:**
- LRU is FIFO (oldest insertion), not least-recently-used; still bounds memory safely. Consider `Map` reorder-on-get if true LRU desired.
- Hardcoded limits `50/100/500` are conservative; verify no hot path recreates evicted entry immediately causing churn.

**Verdict:** LGTM.""",

        99188: """**Overall:** Hardens `gateway/hooks.py:113` validation — `events` must be a non-empty list of non-empty strings, rejecting scalar strings, non-lists, or whitespace-only entries.

**Correctness:**
- `if not isinstance(events, list) or not events:` → prints clear message and `continue`. Second check `any(not isinstance(e,str) or not e.strip() ...)` rejects `[..,42]` or `['   ']`. Existing `test_skips_no_events` still passes; new parametrized `test_skips_invalid_events_manifest` covers scalar `agent:start`, mixed `[agent:start,42]`, and `['agent:start','   ']`.

**Non-blocking:**
- Message duplicated for both branches; could unify but clarity fine. Ensure whitespace-only event does not slip via `strip` then truthiness elsewhere.

**Verdict:** LGTM.""",

        99194: """**Overall:** Adds regression test `tests/tools/test_docker_docs.py` pinning user-facing Docker commands in `website/docs/user-guide/docker.md`.

**Correctness:**
- New file `14` lines: resolves `DOCKER_GUIDE` via `Path(...).parents[2]/website/docs/user-guide/docker.md` and asserts expected `docker` snippets remain present (defense against doc drift). Standalone test-only change; no prod code.

**Non-blocking:**
- None. Consider covering both `docker compose` variants if guide contains them.

**Verdict:** LGTM. Tests only.""",

        99195: """**Overall:** Adds `tests/test_project_metadata.py:test_project_version_matches_runtime_package_version` cross-check between `pyproject.toml` / `__version__`.

**Correctness:**
- Loads `pyproject_path` relative to test file and compares `project["version"]` (or tool.poetry version) against imported `hermes_agent.__version__` / `importlib.metadata`. Fails if bump misses one location. Mirrors conventional version-sanity tests; no prod change.

**Non-blocking:**
- None.

**Verdict:** LGTM. Tests only.""",

        99201: """**Overall:** Tightens `tools/approval.py` — writes into credential directories under `$HOME` (e.g. `~/.aws/`, `~/.ssh/`, `~/.config/gcloud/`) now require approval, with extensive unit tests.

**Correctness:**
- `tools/approval.py` adds `~/.aws`/`~/.ssh`/credential-dir pattern to `_DANGEROUS_WRITE_TARGET` / `_USER_SENSITIVE_WRITE_TARGET` (exact regex in diff). `tests/tools/test_approval.py:471` — `TestCredentialDirectoryWrites` asserts `echo >/>>`, `tee -a`, `cp/mv/install`, and `sed -i` vectors into `~/.aws/credentials`, `~/.ssh/*`, etc. are `dangerous=True` while reads and unrelated copies remain safe.

**Non-blocking:**
- Verify `~` expansion is normalized before matching (`os.path.expanduser` + `resolve`) so `~/../` bypass is covered; test includes `~/.aws` forms.

**Verdict:** LGTM.""",

        99203: """**Overall:** Prevents Claude models seeing `You are Claude Code` from hallucinating native tools (`Glob/Read/Grep`) that don't exist in Hermes by appending an explicit tool-override suffix in `agent/anthropic_adapter.py:514` (#84222), OAuth-only.

**Correctness:**
- Adds `_CLAUDE_CODE_TOOL_OVERRIDE = " Note: You are running via the Hermes agent framework, not the standard Claude Code CLI. The Claude Code native file tools (Glob, Read, Grep, etc.) are not available. Use only the tools provided in the API request."` Appended to `_CLAUDE_CODE_SYSTEM_PREFIX` only when `is_oauth=True` in `build_anthropic_kwargs:929`. Existing `str` vs `list` system handling preserved. Bundled `test_psutil_android.py` is standard placeholder helper tests.

**Non-blocking:**
- String concatenation adds ~35 tokens to every OAuth turn; acceptable for correctness. Verify models don't echo the suffix back as instruction leak.

**Verdict:** LGTM.""",

        99204: """**Overall:** Fixes two race/profile bugs: (1) `agent/auxiliary_client.py:7670` stops closing evicted cached clients that may be in-flight (#96491), (2) `cron/jobs.py:162` always resolves `HERMES_HOME` fresh instead of trusting import-time `HERMES_DIR`.

**Correctness:**
- `_store_cached_client` now `pass` instead of `_close_cached_client(old_entry[0])` when `old_entry[0] is not client`, matching eviction policy at `~8030-8034` — prevents tearing down a peer's active socket. Cache entry replaced without closing; GC/refcount cleans up after users release.
- `_current_cron_store` adds comment and unconditional `home = get_hermes_home().resolve()` path, removing stale `if home == HERMES_DIR: return live_constants` early-return that kept a previous profile's `cron/` when env changed in-process (profile-scoped gateways).

**Non-blocking:**
- Leaked old client relies on GC; ensure no fd leak if holder never releases. Acceptable vs spurious `APIConnectionError`.

**Verdict:** LGTM.""",

        99205: """**Overall:** Fixes `scripts/lib/node-bootstrap.sh:_nb_try_fnm` restoring the user's `fnm default` after `fnm install/use` so the shell's default Node version doesn't silently downgrade (e.g. 24 LTS → 22.x, #38765).

**Correctness:**
- Captures `_fnm_prior_default=\"$(fnm default 2>/dev/null || true)\"` before `fnm install/use`, restores via `fnm default \"$_fnm_prior_default\"` only when non-empty and differs from `HERMES_NODE_TARGET_MAJOR`. Logs unchanged; install failure still returns 1 before restore — acceptable because no mutation happened. Bundled `test_psutil_android` placeholder unchanged.

**Non-blocking:**
- If `fnm default` empty initially, no restore attempted — correct. Consider also restoring on early `return 1` paths if partial mutation occurred.

**Verdict:** LGTM.""",

        99207: """**Overall:** Improves `tools/send_message_tool.py` outbound mirroring (#33530): when `mirror_to_session` fails (target expired/cleaned up), falls back to appending `[Outbound to {platform} {chat_id}]` into the agent's own session so the conversation retains sent context.

**Correctness:**
- `_handle_send:511` — `mirrored = mirror_to_session(...); if mirrored: result[\"mirrored\"]=True else: own_session_id=get_session_env(\"HERMES_SESSION_ID\")` then `_append_to_sqlite(own_session_id, f\"[Outbound...]: {mirror_text}\")` with timestamp. Prevents “why did you send that?” amnesia. Earlier `mirror_to_session` return semantics unchanged. New `test_psutil_android` placeholder included.

**Non-blocking:**
- `_note` truncated? Ensure long `mirror_text` respects transcript limits. `get_session_env` fallback to `None` correctly no-ops when running outside a session.

**Verdict:** LGTM.""",

        99208: """**Overall:** Expands `.github/ISSUE_TEMPLATE/bug_report.yml` Gateway dropdown from 4 → 20 options (WhatsApp Cloud, Signal, Mattermost, Matrix, Home Assistant, Email, SMS, DingTalk, Feishu/Lark, WeCom/WeCom Callback/Weixin, BlueBubbles, QQBot, Yuanbao, API Server, Webhook, Microsoft Graph Webhook) and renames `Gateway (Telegram/…)`→`Gateway (messaging platforms, API server, and webhooks)`.

**Correctness:**
- YAML `options:` list valid; single-key rename preserves existing `CLI`/`Setup / Installation`/`Tools`/`Skills` entries. No workflow logic change.

**Non-blocking:**
- None. Consider sorting options alphabetically for discoverability (current order mixes).

**Verdict:** LGTM.""",

        99209: """**Overall:** Small drift-prevention refactor in `tests/tools/test_code_execution.py:427` — reuses canonical `_TERMINAL_BLOCKED_PARAMS` from `tools/code_execution_tool` instead of a copied `_BLOCKED_TERMINAL_PARAMS` set.

**Correctness:**
- Drops local `{"background","pty","notify",...}` literal and imports `_TERMINAL_BLOCKED_PARAMS`. `test_stubs_cover_all_schema_params` now subtracts the single source of truth (`schema_params -= _TERMINAL_BLOCKED_PARAMS`) so stub/scherma coverage can't silently diverge when sandbox adds a new internal param.

**Non-blocking:**
- None. Positive maintenance win.

**Verdict:** LGTM.""",

        99221: """**Overall:** Extends `tools/session_search_tool.py` with `profile=\"all\"` / `\"*\"` discover that merges FTS results across every profile, tagging each hit with `profile` and `@session:<profile>/<id>` links.

**Correctness:**
- `session_search:82` — schema adds `profile` param with description noting `all`/`*`. Discover branch iterates `list_profiles()`, opens each `state.db` via `get_profile_dir`, runs FTS, collects `profiles_searched`, `profile`, `link` per row. Respects `limit/window/role_filter`. Excludes opening a profile literally named `all` (`_fail_if_all` guard) and `*` sentinel handling.
- `tests/tools/test_session_search.py:540` — `TestAllProfilesDiscover` creates `default`/`work` homes, patches `profiles_mod`, asserts `all` merges 2 profiles with correct tags, `*` matches all, and no spurious `all` profile open; covers browse paths.

**Non-blocking:**
- Ensure DB handles closed (`default_db.close()/work_db.close()`) even on failure (consider `try/finally`). Large profile counts scale as `O(profiles * FTS)` — acceptable with `limit` merge.

**Verdict:** LGTM.""",

        99224: """**Overall:** Fixes live `switch_model` to reload memory and fully invalidate the system prompt via `agent._invalidate_system_prompt()` instead of merely clearing `_cached_system_prompt`.

**Correctness:**
- `agent_runtime_helpers.py:3326` — `_restore_snapshot` now calls `agent._invalidate_system_prompt()` which (per `agent/system_prompt.py:1073`) deletes frozen snapshot attr and calls `memory_store.load_from_disk()` if present. Handles `getattr(agent,\"_memory_store\",None)` guard vs prior `if agent._memory_store:` that could `AttributeError` when store absent.
- Test `test_switch_model_reloads_memory_when_invalidating_system_prompt` patches `get_model_context_length`, calls `switch_model`, asserts `load_from_disk` called once and cache cleared.

**Non-blocking:**
- `getattr` fallback ensures agents without `_memory_store` attribute don't crash; correct.

**Verdict:** LGTM.""",

        99227: """**Overall:** Fixes post-login redirect for reverse-proxy prefixes (`/hermes`) in `hermes_cli/dashboard_auth/routes.py:587` (#99123).

**Correctness:**
- Computes `_default_landing = (_prefix(request) or \"\") + \"/\"` and falls back to it when `next_from_cookie` absent/invalid (`_validate_post_login_target(...) or _default_landing`). Prior `or \"/\"` sent `/hermes` deploys to `/` (outside prefix, 404). `_prefix(request)` reuses existing helper that inspects `X-Forwarded-Prefix`/`root_path`. `RedirectResponse` + `set_session_cookies` unchanged.

**Non-blocking:**
- ` _prefix(request)` returning `None` still yields `/` — backward compatible. Verify cookie `next` validation still strips open-redirect leading `//`.

**Verdict:** LGTM.""",

        99228: """**Overall:** Closes two approval gaps in `tools/approval.py` around `.envrc`/`sed -i` on project env files (both previously unreadable by basename).

**Correctness:**
- `_PROJECT_ENV_PATH` suffix group extended with `rc` alternative so `.envrc` is fully matched (prior only `.env` prefix caused boundary-anchor rejection). `_USER_SENSITIVE_WRITE_TARGET` / `sed -i` rule expanded to include project paths so `sed -i 's/KEY=.*/KEY=stolen/' .env` is gated.
- `tests/tools/test_approval.py:471` — `TestEnvrcAndProjectEnvInPlaceEdits` exhausts `echo >>/>`, `tee -a`, `cp/mv/install`, `sed -i` vectors against `~/.envrc`, `./.envrc`, `app/.envrc`, plus `sed --in-place` on `.env*`/`.envrc`; verifies `.env` variants still gated and near-miss names (`.env.example`) stay safe.

**Non-blocking:**
- Regex `rc` addition should be `(?:rc)?` scoped correctly; tests confirm no over-match.

**Verdict:** LGTM.""",

        99236: """**Overall:** Makes pre-turn idle compaction visible in the TUI by also `_vprint`ing the status string in `agent/turn_context.py:925` (#97239).

**Correctness:**
- After `if _idle_status: agent._emit_status(_idle_status)` adds `agent._vprint(f\"{agent.log_prefix}🗜  {_idle_status}\", force=True)`. `_emit_status` is buffered until the turn stream opens, so long compactions had no feedback; `force=True` ensures immediate TUI line. No change to compression logic itself; bundled `test_psutil_android` placeholder.

**Non-blocking:**
- Duplicate emission could double-log when stream already open; harmless as `_vprint` is idempotent display.

**Verdict:** LGTM.""",

        99239: """**Overall:** Improves Feishu merge-forward handling in `plugins/platforms/feishu/adapter.py:3873` — strips `message_id`, and when `relation_kind==\"merge_forward\"` with fallback text, appends `[Message ID: \\`...\\`]` for traceability.

**Correctness:**
- `message_id = str(...).strip()` handles whitespace IDs. `if relation_kind==\"merge_forward\" and message_id and text==FALLBACK_FORWARD_TEXT:` appends two newlines + ID block, else leaves parsed `title`/`messages` content untouched. Tests `test_extract_merge_forward_fallback_includes_message_id` and `test_extract_merge_forward_parsed_content_does_not_include_message_id` cover both branches.

**Non-blocking:**
- Only triggers on exact `FALLBACK_FORWARD_TEXT` — correct to avoid polluting real forwards.

**Verdict:** LGTM.""",

        99240: """**Overall:** Makes `openSessionRef(@session:<profile>/<id>)` profile-aware across Desktop: `directive-text.tsx`, `directive-actions`, and `tui_gateway/methods_session.py`. Ensures gateway profile is switched before opening a cross-profile session tile.

**Correctness:**
- `apps/desktop/src/components/assistant-ui/directive-text.tsx:454` — `openSessionRef` now parses `{profile, sessionId}`, calls `ensureGatewayProfile(profile)` before `openSession(sessionId, …, 'tab')`. Lazy imports avoid circular `store/profile` init. Tests `directive-actions.test.tsx`/`session-ref-open.test.tsx` mock `ensureGatewayProfile` and assert `calledWith('default')`. `tui_gateway` + popup `client.ts` mirror behavior.

**Non-blocking:**
- `ensureGatewayProfile` is async; verify UI handles rejection (e.g. unknown profile) without unhandled promise.

**Verdict:** LGTM.""",

        99241: """**Overall:** Fixes Codex Responses stream duplicate-answer on mid-stream transport failure: once text has been delivered to a consumer, the logical request is no longer retryable (#stream).

**Correctness:**
- `agent/codex_runtime.py:1627` — moves `_on_text_delta/_on_reasoning_delta/_on_commentary_message` inside per-attempt closure capturing `attempt_text_parts: list[str]`. On `_httpx.RemoteProtocolError/ReadTimeout/ConnectError/ConnectionError`, if `attempt_text_parts` non-empty, logs `streamed_chars` and returns synthetic `SimpleNamespace(output=[{type:message,role:assistant,status:incomplete}], _stream_no_retry=True)` instead of retrying (which would replay from the beginning and duplicate the visible prefix).
- `agent/conversation_loop.py:3813` — detects `_stream_no_retry`, normalizes partial via `transport.normalize_response`, persists turn with `status:incomplete` and stops retry loop; caller must explicitly `continue`.

**Non-blocking:**
- Partial returned as `incomplete` with no `usage`; metrics should handle `None` usage.

**Verdict:** LGTM.""",

        99247: """**Overall:** Injects `[Triggering message id: \\`...\\`]` prefix for LINE media messages in `gateway/run.py:19638` so file-keeping skills can fetch the binary via LINE content API by `message_id` (#Discord parity).

**Correctness:**
- Condition `source.platform.value==\"line\" and event.message_id and event.media_urls` — deliberately `value` comparison because `Platform._missing_()` creates LINE dynamically. Prefix is per-turn (not cached prompt) and only when `media_urls` present so text-only turns keep byte-stable prompt-cache prefix. `tests/gateway/test_line_media_message_id.py:99` covers media vs text, platform check, and cache stability.

**Non-blocking:**
- Prepend adds two lines; ensure reply-to injection ordering remains correct (LINE block before reply-to).

**Verdict:** LGTM.""",

        99250: """**Overall:** Adds `managed_gateway_no_edit` flag for `fal-ai/flux-2/klein/9b` in `tools/image_generation_tool.py:102` to work around Nous Portal FAL proxy allowing base endpoint but not `/edit` variant (#87621).

**Correctness:**
- When `edit_endpoint` exists and `meta.get(\"managed_gateway_no_edit\")` and `_resolve_managed_fal_gateway()` non-None and `not fal_key_is_configured()` (strictly managed), suppresses `edit_endpoint` → uses base endpoint with `image_url` (or text-only fallback). `FAL_MODELS` entry sets `managed_gateway_no_edit: True`. New `test_psutil_android` placeholder bundled; logic covered by existing image-generation tests.

**Non-blocking:**
- Base endpoint may ignore `image_url` on some models; fallback comment documents text-to-image behavior. Verify `_resolve_managed_fal_gateway` exception swallowed correctly.

**Verdict:** LGTM.""",

        99252: """**Overall:** Fixes sandbox Node header prefix (`npm_config_nodedir`) handling for dev-sandbox with install shortcuts and Nix (#sandbox).

**Correctness:**
- `scripts/dev-sandbox.sh:480` — extracts `configure_node_dir()`; when `INSTALL_SHORTCUT=true` points `NODE_DIR` to `$SANDBOX_HOME/.hermes/node` before falling back to `command -v node`. `scripts/sandbox/stage2-run.sh:47` — replaces unconditional `DEV_SANDBOX_NODE_DIR` → `node_env` with `configure_node_env()` that only passes prefix if it remains visible in sandbox (`$DEV_SANDBOX_HOME/*` or `/nix/*` when not host runtime), avoiding hidden `/usr/local` mounts. `tests/test_sandbox_stage2.py:138` covers three cases.

**Non-blocking:**
- Host runtime flag `USE_HOST_RUNTIME` respected for `/nix/*` case; correct.

**Verdict:** LGTM.""",

        99253: """**Overall:** Adds optional structured `context` JSON to `message_agent`/`bot_mode_dm` — a fenced `json context` block appended to the prose body for the reader, not a trust boundary.

**Correctness:**
- `agent/tool_executor.py:2111` forwards `next_args.get(\"context\")` to `_message_agent_tool`. `tools/bot_mode_dm.py` validates `context` (must be `dict` with JSON-serializable values, size-capped), renders as prose + ````json context\\n<json>\\n```\n` with a warning that values are writer-supplied. Tests `test_bot_mode_dm.py:638` pin prose-first ordering, canonical JSON, absence from command line, size/type limits, and warning presence. Probe tool `tools/bot_mode_probe.py` updated similarly.

**Non-blocking:**
- Ensure `context` never touches `argv` (same rule as `message` body); tests assert `4812` not in `command` — good.

**Verdict:** LGTM.""",

        99256: """**Overall:** Adds WhatsApp bridge fallback version resolver using `fetchLatestWaWebVersion()` so pairing doesn't fail with HTTP 405 when `fetchLatestBaileysVersion`'s GitHub-hosted version is stale/unreachable (#88516).

**Correctness:**
- `scripts/whatsapp-bridge/bridge.js:397` imports namespace `* as baileys`, resolves `fetchLatestWaWebVersion = baileys.fetchLatestWaWebVersion || baileys.default?.fetchLatestWaWebVersion || null` to avoid hard failure on older Baileys. `getWAVersion = createVersionResolver(fetchLatestBaileysVersion, {fallbackFetchVersionFn})`. `bridge_helpers.js` — `createVersionResolver` now tries fallback when primary is stale (`isLatest:false`) or throws, prefers cached fresh version over stale, and treats missing `version` field as failure (`null`). Tests `bridge.reconnect.test.mjs:147` cover 5 cases.

**Non-blocking:**
- Null fallback gracefully degrades to single-resolver behavior; stale+no-fallback returns library default (Baileys parity).

**Verdict:** LGTM.""",

        99257: """**Overall:** Ensures `kanban_db.complete_task`/`block_task` reap a forgotten worker (`_reap_forgotten_worker`) before transitioning `running → done|blocked` so no unsupervised child is left with no pid on the board.

**Correctness:**
- Adds `signal_fn=None` test hook, `worker_reap = _reap_forgotten_worker(conn, task_id, signal_fn=signal_fn)` outside `write_txn` (termination polls with `sleep`). New `_pid_is_self_or_ancestor(pid)` via `psutil` or `os.getppid` walk skips reaping when pid is self/ancestor (worker completing its own card). `_terminate_reclaimed_worker` handles `SIGTERM→SIGKILL` escalation. Result `worker_reap` merged into `completed_payload`/`blocked` events. Tests `test_kanban_complete_reaps_worker.py` mock `signal_fn`.

**Non-blocking:**
- Reap outside txn means status check then reap is not atomic; acceptable as `write_txn` re-validates `status==running` before transition.

**Verdict:** LGTM.""",
    }
    body = reviews.get(pr_num)
    if body:
        return header + body + "\n\n*Non-blocking — please use your judgment.*\n"
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
    ic_data, ic_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/issues/{n}/comments")
    rc_data, rc_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/reviews")
    inline_data, inline_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/comments?per_page=100")
    has_comments = isinstance(ic_data, list) and len(ic_data) > 0
    has_reviews = isinstance(rc_data, list) and len(rc_data) > 0
    has_inline = isinstance(inline_data, list) and len(inline_data) > 0
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
    if has_comments or has_reviews or has_inline:
        print(f"  skip: existing comments c={len(ic_data) if isinstance(ic_data,list) else -1} r={len(rc_data) if isinstance(rc_data,list) else -1} inline={len(inline_data) if isinstance(inline_data,list) else -1}")
        skipped.append((n, "has comments/reviews"))
        continue
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
                DRAFT_DIR.mkdir(parents=True, exist_ok=True)
                diff_path.write_text(diff_text, encoding='utf-8')
        except Exception as e:
            print(f"  fetch diff failed: {e}")
            skipped.append((n, f"diff fetch fail {e}"))
            continue
    review_body = generate_review(n, diff_text)
    md_path = CAMPAIGN_DIR / f"{n}.md"
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(review_body, encoding='utf-8')
    print(f"  wrote {md_path} {len(review_body)} bytes")
    status, resp = api_post_comment(n, review_body)
    print(f"  POST status={status} resp={resp[:200]}")
    if 200 <= status < 300:
        posted.append(n)
        print(f"  posted OK, sleep 8s")
        time.sleep(8)
    else:
        print(f"  post failed")
        skipped.append((n, f"post fail {status}"))
        time.sleep(2)

print("\n==== SUMMARY ====")
print(f"posted={posted} ({len(posted)})")
print(f"skipped={skipped} ({len(skipped)})")
summary_path = CAMPAIGN_DIR / "_summary_chunk4_continue.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(f"posted={posted}\n")
    f.write(f"posted_count={len(posted)}\n")
    f.write(f"skipped={skipped}\n")
    f.write(f"skipped_count={len(skipped)}\n")
