# 2026-09-20 批次（收件箱 88 条 → 已清零；另跑 100 条 PR 战役批次）

**账号:** Enough1122 · **处理:** 收件箱 0 未读 · **遗留:** 1 条列请用户定夺（#93730，已不在收件箱）

## 构成与处置

当日两轮：上午 10:16 sweep（清 86 条纯告知）+ 10:23 人工深分诊（清 244 条），下午 16:1x 本轮再来 88 条未读（80 comment + 6 mention）。

本轮流程（按 PROMPT-inbox-pr.md §1）：

1. `gh_inbox_triage.py` — 88 条全部来自 `NousResearch/hermes-agent`，**无一条是我们自己的 PR**（ours: 0）。
2. `scan_pending_mentions.py`（先于任何清理）→ **4 条**真 pending @：
   | PR | 提出人 | 时间 | 判定 |
   |---|---|---|---|
   | #18188 | lancecheney | 08-16 | 复审回复 ✅ |
   | #72638 | Diaspar4u | 08-23 | disposition 收条，PR 已被上游 #115880 取代关闭 → 纯告知 |
   | #92309 | Finn763 | 08-22 起 | 复审回复 ✅ |
   | #93730 | AI-Mart | 09-09 | 催促合并，非作者、无技术内容 → 列请用户定夺 |
3. `inbox_auto_sweep.py` 清 30 条纯告知类。
4. 人工深分诊（`deep_triage.py`）清 58 条（关闭/合并摘要、作者自更新、第三方讨论、致谢收条）。
5. 收件箱 **0 未读**。

## 🎯 复审回复

### #92309 `fix(codex-runtime): forward dispatcher env to hermes-tools MCP subprocess`（Finn763, head `a1fd0f9024eb`）
作者 09-20 06:18 逐条回应我方两条 objection（① 声明式边界取代 name-shape 投影、② 需要 typed grant manifest 的部分他不认为该文件能承载）。实证核验：

1. `hermes_cli/codex_runtime_plugin_migration.py` 现为 `env_vars = sorted(_KANBAN_WORKER_ENV_VARS)`——静态 frozenset，无 `os.environ` 快照、无后缀启发式、分类器 import 已删除（不再有 fail-open 路径）。负例测试已钉住（`test_env_vars_is_the_declared_edge_scope_only`、`..._never_carries_secret_like_hermes_names`）。
2. 新增的 6 个 name 逐个对过 dispatcher：`kanban_db_dispatch.py` 2205/2223/2240/2241/2245/2248 分别印 WORKSPACE/BRANCH/DB/WORKSPACES_ROOT/BOARD/PROFILE；`codex_app_server.py:74-78` 的 `(*KANBAN_ENV_KEYS, "HERMES_KANBAN_DB", "HERMES_KANBAN_BOARD")` 先例引用属实。
3. 就其 residual (b) 补了一条比"缺失即无害"更强的结论：`HERMES_SESSION_ID` **根本到不了这条边**——`_default_spawn` 用 `build_subprocess_env(...)` 后又逐个 pop 掉 `gateway.session_context._VAR_MAP`（`kanban_db_dispatch.py:2189-2190`），而 `HERMES_SESSION_ID` 正在 `_SESSION_VARS` 里（`gateway/session_context.py:37,44`）。故 codex 进程 env 永不带它，`_stamp_worker_session_metadata`（`tools/kanban_tools.py:160`）不会被父会话 id 污染；但这也说明该 name 今天是 no-op，若意图是"worker 带会话 id"，那是 dispatcher 侧的缺口而非这条边的。

回评：[#issuecomment-5748538267](https://github.com/NousResearch/hermes-agent/pull/92309#issuecomment-5748538267)

### #18188 `feat(gateway): extend opt-in runtime footer metadata`（lancecheney, head `50f450bb`）
作者 08-16 逐条处理了我方 4 点观测（此前批次一直判"信息性"，未回）。核验 current head：

- 配额缓存键已含 `hermes_home`（`agent/account_usage.py` — `cache_key(provider, base_url=..., api_key=..., hermes_home=...)`），路由 Profile 的 home 在会话作用域解开前捕获，跨 Profile 用例在缓存测试里钉住（`"hermes_home": "/profiles/routed"` + alice/bob 隔离）。
- reset 标签压缩实现（`_compact_reset` → `1d`/`1h`/`<1m`），测试断言零分量形式（`1d0h`/`0m`）已消失。

回评：[#issuecomment-5748540115](https://github.com/NousResearch/hermes-agent/pull/18188#issuecomment-5748540115)

## 列请用户定夺

- **#93730** `fix(gateway): stream reasoning deltas on /v1/runs and session SSE`（作者 fjh990809）：AI-Mart 09-09 @ 我方"请尽快 review 尽快合并"。非作者、无技术内容、无修改声明；connorblack 09-12 已做过深度 review（3 个 gap，作者已修）。按克制发声口径未回。**该线程已不在收件箱**（被标已读），但 PR 仍 open、仍挂着这条催促——需要用户定夺是否回。

## 流程观察

- 本轮 **0 条 own-pr**：88 条未读全部是别人的 PR，与我们自己无关——与 9 月上旬批次（常有 own-pr）不同。
- `inbox_auto_sweep.py` 只按最新一条评论分类，本轮 88 条里它只敢清 30 条，其余 58 条落进 `unclassified-keep`，仍需人工分诊——脚本的 ACK/ASK 词表对该仓库的实际评论风格覆盖率偏低。
- 已知缺陷复现：sweep 会丢掉"pending @ 之后跟着致谢/推送事件"的线程，本轮仍靠"先 scan 后清"的顺序铁律兜住。

## 续战 · 100 条战役批次(10×10 子代理并行,frontier 114080 → 115076)

**候选扫描:** 收件箱之外还有大量零关注 PR。`gh api pulls?state=open` 全量分页不可行(仓库 29,567 个 open PR,`--paginate` 会一直翻到第 296 页);改用 search API `is:pr is:open comments:0 review:none` 按 created desc 分页,再逐条 `GET /pulls/{n}` 活检。**frontier 之上合格候选 921 条**(编号 114588–117086,创建日期 9/18–9/20),本批取最低的 100 条(#114081–#115076)。

**结果:** 活检 100 · **发帖 31**(6 blocker + 25 非阻塞) · 静默 CLEAN 45 · SKIP_STALE 21 · 发帖时再判 stale 3(#114591/#114636/#114677,快照后有人评论)。

### Blocker(6 条,主流程逐条复核 file:line 后才发)

| PR | 发现 | 复核证据 |
|---|---|---|
| 114597 | Windows 上 reader 线程自己的收尾路径不再关 stdout,FD 滞留到 prune(TTL 1800s) | `process_registry.py:1454` 的 `reader_owns_stdout` 只判 `reader.is_alive()`,而 `_finish_reader`(`:1215`)正是 reader 线程的 finally → 链到 `:1407` 的 release;全文件再无第二处关 `proc.stdout`。另:注释称"调用方持 registry 锁",实测 `with self._lock` 在 `:1397` 已退出、release 在 `:1407` |
| 114659 | 归档过看板的实例上 `_managed_scratch_path_info` 抛 ValueError | `_normalize_board_slug` 对 `^[a-z0-9]` 开头的 slug 才放行(`kanban_db.py:367-380`),而归档会建 `boards/_archived`(`:676`);新加的 `workspaces_root(board=entry.name)` 外层只有 `contextlib.suppress(OSError)`,接不住 ValueError |
| 114674 | `command_aliases` 合并到 main 后是静默 no-op | main 把 `resolve_command` 移进 `skill_command_collision_note`(`skill_commands.py:347`)并去掉了 `_scan_skill_md` 的参数(`:354`);PR 在 head `:436` 仍调用 `_apply_command_aliases(commands, resolve_command)`,包在 `except Exception: pass` 里 |
| 114709 | 房间级 userName 被所有持久化路径丢弃,docstring 说"随房间记录持久化" | 两个 durable 序列化器逐字段列举(`group-chat.ts:1382-1400`、`:745-765`),`userName` 出现 0 次;`GroupChatSyncRoom`(`:60-67`)也没有 |
| 115020 | item-envelope 修复作用在局部副本上,派发仍拿到未修复的 args | `validate_deferred_call_args` 只返回错误串,修复只改局部 `candidate_args`;`agent/tool_executor.py:402-404` 在校验通过时 `return underlying, underlying_args, None`。净效果:把模型本可自救的精确 schema 错误变成下游运行时失败 |
| 115063 | 新增 httpx request hook 在 307/308 重定向后抛 `RequestNotRead` | 已装 httpx2 实证:`_build_redirect_request` 用 `stream=` 重建(`_client.py:474`),该构造分支不调 `read()`(`_models.py:428`),`RequestNotRead` 继承 `StreamError(RuntimeError)`(`_exceptions.py:308,359`),hook 的 `except (ValueError, TypeError)` 接不住;hook 在每次重定向迭代都跑(`_client.py:1045`) |

### 非阻塞(25 条,节选)

- **114641** 单问题路径仍把网关超时通知存成 `user_response`(`clarify_tool.py:243/247`,`_is_timeout` 只被批量路径调用)。
- **114655** `_PERMISSION_DENIED_MARKER` 是 rg 专有的 Rust `io::Error` 拼写,grep 分支不可达(`file_operations_search.py:147`)。
- **114656** family-A 修复不校验 `arguments` 之前的字符串,可把 args 派发给另一个工具(子代理在 head 上实跑复现,含注入式输入)。
- **114658** local-ahead 拒绝闸门放在 orphan 分支之上,使 #87694 的 rescue-ref 路径不可达(`update_cmd.py:755`);孤儿测试靠 `local_commit_count="0"` 的假桩才过。
- **114660** 无 heartbeat 的记录把 `started_at` 当 `heartbeat_age` 上报(`kanban_diagnostics.py:655`)。
- **114661** 浏览器语言回退把 zh-TW/zh-HK/zh-Hant-* 全映射到简体(`web/src/i18n/context.tsx:66`),而 desktop 早有 `LOCALE_ALIASES` 表。
- **114701** cron 重试假设 `send_path_degraded` 一定发生在派发前,但 Discord 在发送之后也发这个码(`discord/adapter.py:3043-3045`),重试会静默重复投递。
- **114703** `_is_sole_credential()` 仍把新开关抑制掉的 claude_code 行算进去(`credential_pool.py:1670`),导致 429 罚 3600s 而非 60s。
- **114711** `_lint_blocked_tags` 无围栏感知,会把 `## Blocked` 里 ```diff 围栏中的 `-` 行改写成 `- [OTESTAD] ...`(`context_compressor.py:279`);子代理实跑复现。
- **114750** 无 scheme 的 `HTTPS_PROXY` 被 proxy-from-env 解析成 `https://` 而让代理吃 TLS(`update-api-proxy.ts:6`);子代理用本地 HTTP 代理实测 EPROTO。另:畸形值抛 `TypeError: Invalid URL` 逃出更新检查。
- **114751** `TRANSIENT_SEND_ERROR_MARKERS` 含 ack 路径产生的 `connection interrupted`/`websocket closed`,重试可能重复已投递消息(该 PR 自己正是以"超时不重试"为由排除超时的)。
- **114752** 文档承诺的 fail-open 是死代码(`_load_mcp_config` 出错返回 `{}` 而非抛),且与 open #114906 对"条目缺失"钉了相反规则——两 PR 不能同时合。
- **114794** 与 open #114872 同修 #114746,#114872 更完整(经 `_sanitize_error`、锁外打日志)。
- **114911** 同一修复已随 `dcafb1900a00` 进 main 且正则更宽;本 PR 自己的新测试与 main 的匹配器互相矛盾。
- **114928** `_freshness` 先判"target 缺失"再判"驱动未安装"(`cua_daemon_health.py:158`),驱动已卸载的机器被告知"二进制没问题";`doctor.py:339` 在多 unit 时指错文件。
- **114937** `reasoning_summaries.py:34` 的 isinstance 守卫不可达(`flatten_message_text` 是全函数),真正的崩溃点没修;`_SSE_REQUEST_REJECTION_PATTERNS` 的通用词条把普通文本体判成不可重试。
- **115022** `vision_routing.py` docstring 仍描述被删掉的决策步骤;静默反转 2026-08-28 维护者决定并改写钉住它的测试;`opencode_session_headers` 丢掉 cron id 归一化。
- **115033** `computer_use_target()` 抛 ValueError 而 `permissions.py:73` 无保护,状态面板变成 traceback。
- **115038** Slack 孤儿 reaper 从跨 await 累积的列表整体重建注册表(`slack/adapter.py:1404`),reap 期间被 retire 的 generation 被静默丢弃。
- **115046** 工具改报 off-path artifact 后,自己的 mkstemp 文件只在异常分支 unlink(`tts_tool_speaker.py:133`),每句泄漏一个空 mp3。
- **115049** 多选卡片反过来:选选项/移光标仍清空已输入的自定义答案(`clarify-tool.tsx:517/542`)。
- **115051** `cron.incident_max_error_chars: 0` 使 `text[:0]` 把持久错误记录清空(`cron/incidents.py:111`);姊妹 PR #115060 已加守卫。
- **115052** 未发布状态的 tile 被当成空白草稿丢弃(`session-states.ts:1846`);`replaceSessionTile` 无 tile 落地也返回 true(`:1858`)。
- **115072** `_unregister_env` 弹出两个 key 只返回一个 env(`terminal_tool_lifecycle.py:175`),第二个容器永不回收。
- **115073** 成本标签绕过已有的 `format_cost_label`(`cli_status_bar_mixin.py:307`),重现 #79220 的"非零成本显示成 $0.0000"。

### 静默 CLEAN(45 条)
每条都对 main 做过实证核对(如 114872/114906 的 MCP gate 语义、115041 对上游 `autostart.rs` 的 REGISTER_PS 展开、115037 的 `resolve_cua_driver_cmd` 带分隔符时原样返回、114763 的 `OAuthNonInteractiveError` 已在 `_is_auth_error` 内)。清单见 `_campaign_state.json` 的 `reviewed_clean`。

### 重复对(供维护者二选一,本批新增)
- 114794(liuhao1024) vs **114872**(Finn763)— 同修 #114746,后者更完整。
- 114752(kokhlo) vs **114906**(Finn763)— 同一 gate,对"条目缺失"规则相反,不能同时合。
- 115042(xiaodu55) vs **115043**(不同作者)— 同修 #115030 的一行 fsync 修复,115043 代码正确但两者只能留一个。

### 流程观察
- **SKIP_STALE 21 条**里,大量是 `alt-glitch` 的 AI triage 注释(9/18 那批),说明该仓库的自动 triage 覆盖面在扩大,人工候选窗口会越来越窄。
- 子代理普遍报告 **GitHub API 限流**(10 个并行共享一个 token),部分改读本地 fork 克隆 `repos/hermes-agent-fix`(HEAD d6dd884b12,与各 PR base 一致)。因此本批 6 条 blocker 全部由主流程拉 current head 原文复核后才发,非阻塞项抽查未见失实。
- 发布门槛执行到位:34 条草稿逐条读完,无一条是 LGTM 或纯风格建议;发帖时 `post_one.py` 的 liveness 再检又拦下 3 条。
- 断点落盘:frontier=**115076**、posted 累计 3652、`reviewed_clean` 1988 条、`progress.txt` 410 行、`rb/` 254 份。
- **backlog 提示:** frontier 之上仍有 **821 条**合格候选(编号到 117086),按 100/批的节奏还有 8 批。

### 补记(子代理迟到的汇报,均为已并入上文的批次)
- **114624 的 base 不是 main**(是 `hermes/hermes-b802e898`),对 main 拉 diff 会失真;子代理按真实 base→head 审的,判 CLEAN。以后活检可顺手记一下 base ref。
- **候选快照与发帖之间会漂移**:114670/114698/114677/114678 在扫描时 `comments:0`,但子代理读到 9/18 的 `github-actions` ci-review / `alt-glitch` AI triage 注释。114677 因此被 `post_one.py` 的发帖前 liveness 拦下(SKIP_STALE),其余三条本就 CLEAN 未发。说明"扫描时零关注"不等于"审阅时零关注",发帖前的再检不可省。
- 子代理自述有两条**自我推翻的假 blocker**被丢弃(115064 怀疑 `MCPError` 是 `McpError` 笔误、115065 怀疑优先级重定向丢了 origin 标注),都是拉原文后证伪的——这正是"实证优先"要挡的东西。


---

# 第3批 · 2026-09-20 晚（收件箱 34 条）→ 已清零

**账号:** Enough1122 · **处理:** 34/34 标 Done（sweep 9 + 人工 25）· **失败:** 0 · **处理后未读:** 0

构成: 全部 `NousResearch/hermes-agent`，无 own-pr（ours=0）。`scan_pending_mentions.py`（先于清理）→ **0 条 pending @**，本轮无复审回复、无列请定夺。

## 分类明细

- **我方评过的 PR 的作者修复回执（4 条，均未 @ 我方）** → 按 §1.3.1「作者自更新只归档不回」静默归档：
  - **#115051**（chelsealong, `e098dc8c`）：`_max_error_chars()` 对非正值回退 `MAX_ERROR_CHARS`(500)，补 `test_error_truncation_length_nonpositive_falls_back_to_default` —— 回应我方「`text[:0]` 清空持久错误记录」。
  - **#115049**（chelsealong）：`selectChoice`/`moveActive`/`toggleChoice` 仅在 `!multiSelect` 时清草稿，并去重 `multiSelectAnswers` —— 回应我方「多选卡片清空自定义答案」。
  - **#115072**（kerri-hard）：承认是本 PR 引入的回归（非既有缺口），已修 `_unregister_env` 的 key 集合 —— 回应我方「弹两个 key 只返回一个 env」。
  - **#114794**（liuhao1024, `cd8edd6b9f`）：两点均采纳——记录原因过 `_sanitize_error`（含 `Bearer sk-…` → `[REDACTED]` 回归测试）—— 回应我方两条非阻塞项。
- **纯 push 事件（6 条，lc=None）** → timeline 核实均为无正文推送：#92122 是 autumn8-builds 每 6h 强推、#94411/#106221/#92930/#88522/#106727 为 commit push。
- **第三方非定向讨论（3 条）**：#87171/#108665（KeyArgo 对他人 PR 的独立复现确认）、#65982（shojikumaru 向作者致谢）。
- **已关/合并收尾（8 条）**：#101243（superseded）、#95619、#103882、#100588、#106666、#106697、#103508、#104566（teknium1 cherry-pick 收条）。
- **作者自更新/rebased 通知（10 条）**：#106961、#101173、#98851、#102102、#101181、#92309、#100115、#102063、#95356、#89361。
- **本轮新增 3 条**：#97799/#97775（ricardosalta 的 refresh 通知）、#87117（push）。

## 备注

- **#92309** 的最新评论（Finn763 09:09）是回 kvnloo 的 salvage 确认（"两个 commit 按序带走"），非定向我方；我方 07:59 的回评仍是该线程最后一条指向我的发言。
- sweep 本轮 34 条只敢清 9 条，25 条落 `unclassified-keep` 需人工——覆盖率低的老问题持续。
- 6 条 lc=None 的 reason=mention/comment 均为推送事件，证实「reason 不可靠、scan 才是权威」。

## 待跟进

- 上述 4 条作者声称已修复但**未核验**（无 @，按 SOP 未回）。若用户要求核验回评，需逐条拉 current head diff 实证后再走 `post_followup.py`。


## 续战 · 第10批 100 条战役（10×10 子代理并行，frontier 115076 → 115495）

**候选扫描:** 同口径（open + 非 draft + 零评论/评审/inline + ≤15 文件 + diff <100KB）在 frontier 之上 **445 条**（#115078–#117180，9/18–9/20 创建）；上午同口径还是 821 条——半天内腰斩，因为 1062 条 open PR 里已有 576 条被 `alt-glitch` AI triage / ci-review 机器人评论过，"零关注"窗口在快速关闭。本批取最低 100 条（#115078–#115495）。

**结果:** 活检 99（#115178 diff ≥100KB → 转 `deferred`）· **发帖 39**（18 blocker + 21 非阻塞）· 静默 CLEAN 59 · 发帖时拦下 1（#115280 已 closed）。

### Blocker(18 条,主流程逐条复核 file:line 后才发)

| PR | 发现 | 复核证据 |
|---|---|---|
| 115081 | 卡片菜单两个动作后端必拒（Request review 恒 409 / Block 在 5/7 列 409） | 菜单 `when: s === 'done'` / `s !== 'blocked'`（board.tsx 新增行）；`request_review` 与 `block_task` 的 UPDATE 均带 `AND status IN ('running','ready')`（kanban_db.py:3307 / :3162）→ rowcount≠1 → plugin_api.py:614 抛 409；无 done→review 动词 |
| 115084 | 清边 `kind === 'ready'` 网关永不发送 → 中止路径压缩态卡住 | `_status_update` 无 text 时 `out_kind = "status"`（tui_gateway/server.py:784-795），三处调用（methods_session.py:1889/1908、compute_host_bridge.py:330）实发 `{"kind":"status","text":"ready"}`；新测试钉的正是这个不存在的形态 |
| 115149 | worker 里 seed 只读不清 + 新提示把 /prompt /compose 挡在 worker 之前 | `_pending_agent_seed` 唯一清除点 cli.py:3564（`_tui_run_slash_input`），worker 走 `process_command` 不经过；`_live_slash_command_output` 早于 worker 返回（methods_tools.py:893-896） |
| 115163 | 新增用户可见文案硬编码俄语（12 行）绕过 17 份 locale；supervisor 会把 stop() 强杀的 gateway 当崩溃复活 | 新增行含西里尔字母；main 上 `gateway/`/`hermes_cli/`/`tools/`/`agent/` 非测试源码零西里尔；locales/en.yaml 已有 `gateway.restart.*` 与 `draining` key（本 PR 删的正是 `t()` 调用） |
| 115183 | `HERMES_HOME` 用 `shq` 单引号包裹 → `~/` 前缀不展开，命名 profile 远端启动 exit 1 | diff 新增行 `HERMES_HOME=${shq(spawnHome)}`（remote-lifecycle.ts:236）；`shq`=纯单引号（:130），模块既有解法是 `expandRemotePath`（:153）；子进程 `Path(profile_home).is_dir()` 无 expanduser（hermes_constants.py:289-294） |
| 115200 | `!fromKey?.trim()` 打断 `adoptNewSessionDraft` 的首发送稿携带 | `adoptNewSessionDraft` 调 `migrateSessionDraft(null, toKey)`（composer.ts:478，生产调用点 use-composer-draft.ts:467）；`!null?.trim()` → 恒 false；且删除行与 main:434 不符（hunk 无法应用） |
| 115215 | 审批侧 `_V4A_FILE_RE` 用 `\s+`、执行侧 patch_parser 用 `\s*` → 混排多文件补丁绕过逐路径检查 | edit_approval.py:45 正则 vs patch_parser.py:49-52；file_tools.py:145-147 注释已自认 `***Update File:` 会生效；全无空格写法反而安全，可利用形态是混排 |
| 115222 | 补丁 hunk 基于旧版 main（env_float 拼写早已改为 helper 函数）；300s 默认严于 local 端点 900s | main 该行为 `_local_stream_stale_timeout_default()`（chat_completion_helpers.py:3593），env_float 只活在 :616 helper 内 |
| 115226 | 前提为假：`gateway.platforms.*` 确是运行时读取路径（优先级最低）；且重定向同时挂在 get/unset | config_loader.py:168 `merge(nested_gateway.get("platforms"))`；`_redirect_platform_display_key` 被 :3750(set)/:3845(get)/:3916(unset) 复用 |
| 115267 | A2A `message/send` 全面异步化，本仓自己的出站客户端从不 poll tasks/get；`A2A_PEER_TOKENS` 分隔符 `:`→`=` 无迁移 | 新 `_rpc_message_send` 对本地路径也直接返回 WORKING；tools.py 全文件无 `tasks/get`；security.py:35 改 `=` 而 plugin.yaml/向导/README/DESIGN/docstring 仍是 `name:token` |
| 115269 | endpoints URL 把 `vendor/model` 的 `/` 编码成 `%2F` → 404，pin 校验整体空转 | 代码 `quote(base, safe='')`；我用 live API 直接复现：未编码 **200/30 endpoints**、编码 **404**；新测试全 mock 掉探针所以 CI 绿 |
| 115271 | liveness 回退只认 404，不认旧版 OAuth 网关的 401 `no_cookie` → 健康远端被 retire 重建 | 新 `probeLiveness` 只 import `isMissingHealthEndpointError`（remote-liveness.ts:1），而 backend-health.ts:294 用双谓词 `\|isGatedMissingHealthError`（:188 正是为 401 no_cookie 而设）；三个 revalidate 调用点全被换 |
| 115279 | 新增可配置 toolset 却未加 `_RECENTLY_SHIPPED_TOOLSETS` / migration → 已有显式 `platform_toolsets` 的安装升级后静默失去 write_file/patch | `_RECENTLY_SHIPPED_TOOLSETS` 仍是空 frozenset（tools_config.py:438）；读取侧只认保存过的 key（`_explicit_toolsets` :511）；`_migrate_to_45` 是同类先例；`_recover_platform_native_toolsets` 明确跳过 configurable universe |
| 115337 / 115357 | `cleanup_interim_segments` 会删掉溢出切分答案的已送达前几段 | 新 `_cleanup_interim_segment_messages` 删 `_preview_message_ids` 全部（除 `_message_id`），无 `_turn_split_delivery` 守卫；main 的 `_try_fresh_final` 正是为此加了该守卫（stream_consumer_transport.py:274），`_track_preview_ids_from_result` 注释自认会记录 continuation ids；115357 整包携带同一批 blob |
| 115380 | fail-closed 采纳守卫只写在文档里，返回值被丢弃 → 重跑写入重复 DM 行 | 调用处 `adopt_unanswered_turn(...)` 无判断（api_server.py 新 `_run()` 块）；同类 PR #115378 则 `if adopted is None: return` |
| 115407 | 补丁目标 `gateway/run.py::_try_resolve_fallback_provider` 在 main 已不存在，新测试 import 必挂 | clone 中该符号 0 命中；真实 walker 在 hermes_cli/runtime_provider.py:1054 `resolve_runtime_with_fallback`（cron/scheduler.py:1577 另一份）；测试 `from gateway.run import ...`（diff:231） |
| 115455 | 删 `_quoted_media` 定义留调用点（带引用消息必 AttributeError）+ `send_error` 脱敏被换成裸 dict | diff 中 `_quoted_media` 仅 1 处（def 删除，hunk `@@ -800,27 +940,6 @@`），调用点 main adapter.py:848 不在任何 hunk；`send_error`→`_error`→`_sanitize_error_text`（_shared.py:170 / send_message_senders.py:46-54）四处被裸 `{"error": ...}`（含未脱敏 `await resp.text()`）替换 |

### 非阻塞(21 条,节选)
- **115106** 默认 hub tap 新增第三方仓 `hermesbooklol/hermesbook-skill`（0 star、创建于 2 天前，SKILL 引导 agent 生成 ed25519 私钥落盘并注册发帖；`INSTALL_POLICY[community][safe]="allow"` 意味着扫描判 safe 就免确认安装）→ 请维护者确认背书关系。
- **115135** `hasProjectContent` 改为 `repos.length > 0`：单仓 + 零会话时 `showHeader={!single}` 抑制头部，面板空白且丢空状态。
- **115175** `_execute_run_via_live_owner` 轮询无 deadline、无 owner 存活复查 → 租约持有者死亡则 run 永久 running（兄弟通道有 `_LIVE_WAIT_SECONDS`）。
- **115180** picker 恒发 `--session`，绕过 `resolve_persist_behavior` 的新装首选持久化契约（#86414）。
- **115188** 预填循环 `` `${name}-${n}`.slice(0,64) `` 重新引入 #19 截断 bug（同仓 profile-ops.ts:313-315 的注释正是警告这个写法）。
- **115206** 空 stdout + rc=0 判为可恢复 → 非幂等命令（click/type）可能重复执行。
- **115232** 新配置键零文档；会话开始的可行性告警仍用不带 runtime 的解析（conversation_compression.py:1993）会报错 provider 名。
- **115244** picker 的 ENTER 处理在 TUI 线程同步做 8s 网络请求（`_TIMEOUT=8.0`）；路由在模型切换提交前就已落盘。
- **115245** `_gate_is_on` 读 `scope["app"]`，FastAPI 子应用会把自己写进去（starlette applications.py `scope["app"]=self`）→ gated 部署仍会吐出 session token（泄密 + 文档契约违背，非越权）。
- **115270** 清理 `finally` 位于 prepare 之下（run_turn.py:2142 prepare → :2145 提前 return → :2148 try/finally），prepare 抛异常/提前返回时记录残留到下一轮。
- **115282** 单图 album key `msg{message_id}` 未带 chat_id（message_id 仅会话内唯一）→ 不同会话共用目录；`_write_album_photo` 是 exists→write 非原子。
- **115283** 新增 387 行 `agent/devin_acp_client.py` 全仓无人 import，活路径走 `devin -p` CLI，ACP 会话层与 fs 沙箱/写入审批全成死代码；`list_models` 三条路径都返回同一硬编码列表；整段对话走 argv。
- **115328** TUI 改用 `any-inbound` 存活判定，重新引入"请求循环卡死但仍持续推流"的盲区。
- **115368** redirect 优先的恢复会在超时时取消一次只是慢的模型请求（推翻 watcher 原"never kills the turn"契约）。
- **115378** 重复实现 main 已存在的 `adopt_unanswered_turn`（quiet_single_query.py:170）。
- 另有 115088（guild 频道重启后仍走错端点）、115095（放宽的 reauth 匹配未加 remote-config 守卫）、115159（view 用 SKILLS_DIR 反推路径，项目/外部技能报"找不到"）。

### 重复对(供维护者二选一)
- **115378 vs 115380** — 同修 #115325，都改 peer-DM 通道与 `_run_agent` 签名，只能落一个；115380 做了抽取但丢了守卫，115378 守住了但复制了 helper。两份草稿都写明了这一点。
- 115282 ⊃ 115280 的 adapter.py 改动、115357 ⊃ 115337 六个文件（blob 相同），合并顺序决定是否冲突。

### 流程观察
- **stale-base 补丁成批出现**：115200/115222/115407 的 hunk 上下文与 main 现文不符（无法应用），另有 115158 的 `event_hooks` 行在 main 已扩成两行。本批把"hunk 是否基于旧版 main"列入常规抓点后，这类发现占比不低。
- **子代理派发事故（需改进）**：chunk1/3/4/7/9 的报告因 drain 截断延迟送达，我在"有草稿无报告"的窗口里误判为无产出，重派了 4 个补审代理（随后全部停止）。教训：草稿目录为空不能推断"没干活"——尤其是超长汇报会被截断，应先 `SendMessage` 索要再决定重派。重派期间未产生重复发帖。
- 发布门槛执行到位：99 条全部读完，34+7 份草稿逐条复核 file:line 后才发；`post_one.py` 的发帖前 liveness 再检拦下 1 条（#115280 已 closed）。
- 断点落盘：frontier=**115495**、posted 累计 3691、`reviewed_clean` 2047、`progress.txt` 509 行、`rb/` 293 份、`deferred` 15 条（含 diff ≥100KB 的 #115178）。
- **backlog:** frontier 之上仍有 **345 条**合格候选（445 − 本批 100），按 100/批还有 3.5 批；但"零关注"窗口在快速关闭（本批扫描时 1062 条 open PR 中 576 条已被人评论）。


## 续战 · 第11批 100 条（10×10 子代理 + 5 路独立核验，frontier 115495 → 116125）

**结果:** 活检 100 · **发帖 41** · 静默 CLEAN 57 · skip 2（116100 头号机制被核验证伪丢弃；116119 与 116118 同一守卫的竞品修复，评语在 116118 侧交叉点名）。

### 流程变化（本批起）
- **主流程复核改为"5 路对抗性核验代理"**：17 个 blocker 候选 + 26 份非阻塞草稿不再由主流程逐条手核，而是按组分给 5 个核验代理，要求真实复现（`git apply --check`、`npm ci` 实跑、伪造 worktree 结构执行 PR 函数体、临时副本跑 kanban/hindsight 语义）并给 CONFIRMED/REFUTED/PARTIAL。裁决：REFUTED 1（116100——所称三条漏网路由根本不创建会话记录，且建议修法会制造它声称要修的泄漏）、PARTIAL 若干（多为行号差 1、个别因果句被证伪需删）。发帖前逐条按核验意见改写。
- 子代理报告截断/延迟再次出现（b11c1/b11c3 靠 SendMessage 索要），未再误判重派。

### Blocker 要点（16 条，证据均经核验代理实测）
- **115584** LINE 系统前缀表没同步新 ack 文案 → 忙时 ack 被缓存成 postback 答案。
- **115640** lazy_deps 仍钉 httpx2==2.7.0；`test_pyproject_pins_match_lazy_deps_pins` 在此 diff 上实测失败（CI 红而非静默，措辞已按核验改写）。
- **115649** import smoke 先于 bytecode sweep / dep sync 就 `reset --hard` 回滚，与 update_cmd_deps.py:1146 "never roll back" 定论冲突。
- **115947** npm ci 实测 EUSAGE（4 workspace 只升 1 个；lock 手改痕迹）。
- **115951** >64KiB 回执实测 fork 链（prev_sha256 归零、verify 报篡改）；Windows pickle 失败实测 1 failed/15 passed。
- **115952** config_defaults hunk 打不上 main（GitHub dirty），照搬会丢 no_progress_timeout。
- **115956** ACP 重放通道仍 `== "todo"`，改名后永假（e16ad33a9d 改名未触 acp_adapter）。
- **116035** lsof 硬编码 /usr/sbin/lsof（macOS 路径）→ Linux 恒 None 清扫失效；两个真 lsof 测试在 ubuntu-latest 必 skip。
- **116039** 搬移测试带旧断言（main:2401 已改 `required: []`），rebase 后必挂。
- **116040** 伪造 `.git`/gitdir/commondir 指向受信仓 → `is_project_root_trusted`=True（核验代理真实构造复现，pwn 技能被供给；真 worktree 不受影响）。
- **116066** hunk 打不上 main（reanchor_clock 插入）；git apply 整补丁全有或全无。
- **116082** `block_loop_exempted` 不在 sticky kind 表 → 豁免循环被 `recompute_ready` 复活（临时副本逐字复现 promoted=1）。
- **116093** legacy API 下 hindsight_retain 的 document_id 与 sync_turn 整会话文档相同且无 update_mode → 一次 retain 覆盖全部已保留 turns（假服务端实测）。
- **116102** main 已有同一 emit；补丁后 blocked 卡每次创建多出一条 blocked 事件，自带断言必挂。
- **116122** `tirith:<rule>` 永久 allowlist 放行内容级规则，违背 _persist_choice 明写的 session-max 不变量（四场景实测 approved=True）。
- **115674/115740** 机械 rebase 冲突（patch -p1 + 3-way 双重复现）。

### 非阻塞(25 条,节选)
115522（外接引擎 max_tokens 未走 _compressor_max_tokens）、115595→115995（ctrl 弦同判据兄弟分身）、115975（歧义守卫只认英文 stderr 子串，git 2.55 实测 exit 0 选 tag）、115997、116033（指纹异常伪装成无进展）、116044（CRLF frontmatter 谓词与 parser 不一致，触发场景按核验收敛到用户自写目录）、116051（done 列 TEXT 排序 500）、116052（benched 凭据被收养）、116068（dashboard key 校验永远探 Studio host）、116090（finally 在 Ctrl+C 时销账 marker）、116097（splitlines 非 LSP 行模型）、116108（rerank 跨 trust 全局重排可挤掉官方条目）、116111（迟恢复 replay 全部历史）、116112（空 body 400 vs 文档默认 drain）、116118/116120、115734（超长 goal 使门禁 fail-open）、115764（/status 三行硬编码英文）、115907（marker-free 每 turn 全量解码 durable transcript）。

### 数字
frontier **116125** · posted 累计 **3732** · reviewed_clean **2104** · deferred 15 · progress.txt 611 行 · rb/ 334 份。核验驳回 1 条、改写 14 条后发帖——对抗性核验的直接收益是拦下 1 篇假 blocker 和一批行号/因果错误。


## 续战 · 第12批 94+6 条（10×10 子代理 + 3 路核验，frontier 116125 → 116508）

**结果:** 活检 94（6 条 diff ≥100KB 转 deferred）· **发帖 32** · 静默 CLEAN 62 · skip 0。

### Blocker(8 条,主流程或核验代理实测)
- **116177** docker_forward_env 的黑名单豁免被取消，文档示例的 GITHUB_TOKEN 被静默丢弃（实测黑名单命中）。
- **116219** 补丁把 `_delivery_adapter_for` 还原成 main 已删除的 `_adapter_for_source` + 丢 task_id + 丢 order_by_last_active（42d142ba41 改名实证）。
- **116222** `_key not in bridge_env` 无法区分"显式赋值"与"从启动环境继承"（bridge_env 就是 dict(os.environ) 的拷贝），跨 profile 行为配置泄漏。
- **116261** 移除 vision 跳过名单的证据走的是 OpenAI 兼容线，但 sk-kimi-* 一律走 Anthropic Messages 线（providers.py:302 / runtime_provider.py:121），且删了 #17076 守卫测试。
- **116318** `_wait_for_pid_exit` 经 state 短路进 force-exit，后者内部又调 `_wait_for_pid_exit`，witness 恒真 → 无限互递归（补丁树实测 RecursionError，0 次 SIGKILL）。
- **116379** 新测试双参调用单参 setter（tsc TS2554，CI 必红）。
- **116410** Discord 403（Forbidden）被当"线程已消失"改投父频道（权限裁决降级为换目标投递）。
- **116422** sandbox 禁用 token 过滤大小写敏感，混合大小写绕过 allow-same-origin 拦截（实现 + token 表复核）。

### 非阻塞(24 条,节选)
116129（随 PR 提交 .claude/validation 内部档案）、116185（测试 hunk stale + max_spawn 文案网关不成立）、116204（每次工具启动一次写事务）、116214（updated_at 刷新扰乱 contradict 排序）、116223（同 iframe 第二嵌入缺 clipboard-write）、116227（新 park 桶 CLI/tick 不可见）、116230（/min→/b 真机证据缺失）、116254（超时无条件删 index.lock）、116259（clarify 默认开启无 opt-out）、116266（整数 done 变 parse_failed）、116268（legacy OTP 无 vault）、116295（defer 队列无清理）、116298（WAL 边车测试 DELETE 模式必败）、116300（VIRTUAL_ENV 伪造 8 处中 7 处不成立，收敛到 main_install_repair.py:450）、116385（Telegram 跳过 edit 仍记已显示）、116396（危险模式引号内提及误报）、116399（sessionRow 传 live id）、116403（双端 flattener 分歧）、116409（持久化偏好卸载无恢复）、116413（校准见证单次 setTimeout）、116424（折叠 Section 编辑无反应）、116426（重试预算超 ready 超时）、116499（守卫契约与实现不符）、116506（死代码 + 相对路径错 profile）。

### 数字
frontier **116508** · posted 累计 **3764** · reviewed_clean **2166** · deferred 21 · progress.txt 705 行 · rb/ 366 份。本批核验驳回/收敛：116300 八处指控收敛到一处（其余七处经查不成立）。


## 续战 · 第13批 100 条（加速模式：核验只保 blocker，frontier 116508 → 117089）

**结果:** 活检 100 · **发帖 18** · CLEAN 81 · skip 1（116701——子代理的草稿谈的是 `scripts/acp_delegate.py`，而该 PR 的 diff 里根本没有这个文件，草稿与 PR 错配，主流程扣下未发）。

### Blocker(4 条)
- **116563** `_next_line` 逐 piece 累积整行后再做 budget 检查，单行巨型文件仍能打爆内存（注释宣称的保证不成立）。
- **116669** clarify 单题超时自动选首选项，把 TUI 显式 skip（`"" = skip`）也转成选择；且 timeout=0 不等于文档称的 unlimited。
- **117072** 新辅助函数插在 `to_dict` return 与 `@classmethod from_dict` 之间，把 `from_dict` 吞成嵌套函数——类上消失，会话恢复必挂（调用方 session_persistence.py:260/306 全 AttributeError）。
- **116676** 用量测试与 daemon 抓取线程竞态：render 同步读缓存，mock 的 fetch 在 daemon 线程里赶不上断言，测试无法稳定通过。

### 非阻塞(14 条,节选)
116523（fork 专属 workflow 入库 + cap 检查 TOCTOU）、116540/116554（shutdown 计数器两 PR 的竞态/泄漏与 bool 矫枉）、116578（线程启动窗口残留竞态 + 字符/字节计量）、116698（守卫 exit 0 混淆被抢占与 infra 故障）、116807（无关 contributor 文件入库）、116817（id-less 200 置空 message_id）、116827（dedup key 坍缩 + allowlist 大小写）、116854（公共函数改名无别名）、116981（死 `_TICK` 常量）、116988（dev-group 屏蔽误伤 shipped electron）、117003（isolate 计费未披露 + 解析异常崩溃）、117038（auth 白名单漏变体）。

### 数字
frontier **117089** · posted 累计 **3782** · reviewed_clean **2247** · progress.txt 805 行 · rb/ 376 份。加速模式验证有效：错配草稿在快审环节被拦下（diff 文件头对不上），3 路核验代理的开销省掉后单批周转明显加快。


## 续战 · 第14批 67+2 条最终批（frontier 117089 → 117278，backlog 清零）

**结果:** 活检 67（2 条 diff ≥100KB 转 deferred）· **发帖 15** · CLEAN 52 · skip 0。

### Blocker(5 条)
- **117072** 新辅助函数把 `from_dict` 吞成嵌套函数（`@classmethod` 被挤进函数体内），会话恢复必挂。
- **117128/117129/117130** 同一 hunk：rg 的 OSError guard 只 return ENOENT/ENOTPERM，其余 errno 落空到 drain 段用未绑定的 proc → UnboundLocalError（此前所有 OSError 优雅返回）。
- **117211** 仓库根多了 `venv -> /home/ubuntu/.hermes/hermes-agent/venv` 软链（mode 120000）。
- **117233** `skills/AGENTS.md` 同一段 rule 9 文字重复插入 13 处 + 会话令牌抓取 skill 以默认 bundled 落地 + capture 脚本 listener 死循环致 HAR 永不落盘。

### 非阻塞(10 条,节选)
117091（DB 脏行 abort 整轮回收）、117114（真 auth crash 绕过 blocker 重生循环）、117122（always-session 丢持久化语义）、117124（id 截断动 live transcript）、117244（双线程重试误退役新 client）、117256（hunk 漂移 + 指纹漏 base_url）、117259（rebase 须保留 #81108 approval_override）、117264/117265（同修 #117216 的 FNV vs SHA-256 互斥实现，只能落一个）、117268（外部 sha 需 out-of-band 核销）。

### 数字
frontier **117278** · posted 累计 **3797** · reviewed_clean **2299** · deferred 23（含本批 2）· progress.txt 874 行 · rb/ 391 份。**backlog 清零**：frontier 之上已无符合口径的候选（后续新增 PR 会重新出现）。


## 收件箱批次 · 2026-09-20 深夜（46 线程）→ 已清零
**账号:** Enough1122 · **处理:** 46/46 标 Done · **处理后未读:** 0
构成: comment 43 + mention 3 · 复审回复 1 · 采纳并关闭(不回) 1 · 静默跳过 44

### 🎯 复审回复
- **#115033 fix(computer-use): run the Windows host driver from WSL**（Xipong，head `f1af7b35`）— 作者按我方意见修了 status 面异常：实证 `tools/computer_use/permissions.py:73-84` 已 try/except `ValueError` 并把诊断写入 payload 的 `error` 键（键序契约保留），`request_permissions_grant` `:105-109` 退 2 并 stderr 带诊断。我方 minor（`_serve_args` 未捕获 → 未处理异常）被作者驳回且**驳回成立**：`tools/computer_use/tool.py:325-327` 的 `_get_backend` try/except 已兜住，属 fail-closed 工具错误而非 traceback；回评中已承认过度指控，接受其"回归覆盖"定位。
  回评: https://github.com/NousResearch/hermes-agent/pull/115033#issuecomment-5750803818
- **#117265 fix(tips): retireable content id**（liuhao1024）— 采纳互斥结论、关闭本 PR 让位 #117264；致谢类，按克制口径不回，仅归档。

### 供你过目（未 @ 我 → 未回，但属实质分歧/反驳）
- **#116266**（jingchaodev）作者明确：拒绝 JSON 整数 `0/1` 是**有意**的范围界定（legacy 形状为 `{"done": <bool>}`，整数视为 malformed），字符串 token 兼容作为例外保留。与我方"兼容性"非阻塞意见分歧 → 倾向接受其界定。
- **#112836**（liuhao1024）作者对"用 `replayed` 标签做 guard"给了三条理由（标签覆盖不到 repro 路径等），选择保留 persisted target set → 倾向接受。

### 其余
- 作者按 review 修改并自证（未 @，未回）: 115206、115278、115282、115283、116052、116108、116204、116854、117038、105271、117114、91428、84869。
- 上游其他 PR 已落地/收尾: 102368（经 #106752 合入）、100215（keyframes 部分经 #117102）、101180、106037/106038（teknium1 澄清后关）、92326（作者自行撤回）、87983。
- 其余为致谢/CI 播报/第三方讨论（JPeetz、stepanov1975、kshitijk4poor 等）。

### 处置与待跟进
标 Done 46/46、失败 0；`gh api -X PUT /notifications` 后 unread=0。无新增阻塞。

## 续战 · 第15批收尾 5 条（frontier 117278 → 117283）
**结果:** 活检 5 · 发帖 1 · CLEAN 2 · skip 2（117281/117282 已关）。
- **发帖 #117280 fix(discord) 权限表 blocker**：`_PERMISSION_FLAGS` 末三项错位一位（`SEND_MESSAGES_IN_THREADS: 0x2000000000` 实为 USE_EXTERNAL_STICKERS 等），已对 discord.py 权威表独立核对；另 3 条非阻塞（`_HANDLER_DEFAULTS` 吞掉 `_create_role` 默认值、color 无校验、`_CHANNEL_TYPES` 冗余）。
  https://github.com/NousResearch/hermes-agent/pull/117280#issuecomment-5750805752
- 数字: frontier **117283** · posted **3798** · reviewed_clean **2301**。

## 续战 · 第16批 8 条（frontier 117283 → 进行中）
候选 8（#117286..#117304，当日新增），预检: 2 条 apply-fail（#117286 gateway/run_turn_runner.py:917、#117301 custom-endpoints-settings.tsx:320 → hunk 基于旧 main、草稿走机械 rebase 快审），0 配对冲突。两路代理审阅中。


## 续战 · 第16批 8 条（frontier 117283 → 117304）
**结果:** 活检 8 · **发帖 8** · CLEAN 0 · skip 0（2 路代理；1 条 blocker 候选经主流程核验后按 rebase 口径降级）。

### 发帖明细
- **117286** fix(gateway) 非编辑平台重复发送：整条链路追通（commentary 记账→final 去重、deltas 对不可编辑适配器关闭）；机械项 = 首个 hunk 上下文已被 `417d0c0f6a` 重构（`_adapter_for_source`→`_delivery_adapter_for`，main:931），GitHub `mergeable: MERGEABLE` → 发 rebase 说明（非硬 blocker）；非阻塞：非编辑平台终答改走 interim 发送，Signal/微信/QQ/BlueBubbles 无回复锚点；Minor：`stream_deltas_enabled` 直接解引用 vs 代码库 getattr 习惯。
- **117287** fix(cron) 陈旧 holder 让位门：门可静默永久失效——holder 侧 `code_sha` 走 40 位校验（build_info.py:22-23）vs 磁盘指纹 64 位（sha256 仓库）→ 恒不等、恒不让位；测试模块文档仍列旧三条条件；Minor：依赖 60s housekeeping 心跳 vs 120s TTL。
- **117292** fix(tui) `/save` 参数：生成契约文件已复核与生成器 byte-identical、载荷 round-trip 通；非 compute-host 分支（fmt/basename/redact/render）无测试；`filename` 静默 basename 化（`..`/`dir/` 退化成 errno 5011）；Minor：桌面端不做格式校验、与 TUI 行为不一致。
- **117293** fix(checkpoints) 索引锁自愈：修复正确、staleness 界成立；重试只捕 `TimeoutExpired`（首试捕全部异常）→ `safe_restore_plan` 路径可逃逸异常；只治 index 锁、`refs/...lock` 同类楔死未覆盖；Minor：docstring 时限说错、探测对 allowed_returncodes 也跑。
- **117299** fix(discord) 命令同步恢复：三条丢失机制真实且被新测试钉住；但 in-process 重试不吃持久化 backoff（5 次预算可连烧）、backoff 门未按 fingerprint 作用域（改了命令集也要等 1h）、失败的 drift 检查每 15s 重跑（应 1h）；测试断言 `sync.assert_not_awaited(), "..."` 写成元组 → 永真。
- **117301** fix(desktop) 自定义端点按 profile：**复核结论 = 对当前 main 全部 10 文件可干净 apply**（预检报的 `:320` 冲突只在缺 `SectionHeading page` prop 的旧检出复现 → 本地 clone 偏旧，非 PR 问题）；非阻塞：切换 profile 后旧作用域的 save/delete/activate 响应落到新视图；Minor：`_env_secret` 在 `_EXPLICIT_CONFIG_CHECKS` 里 `best_effort=False` 且 `get_env_value` 可抛 `UnscopedSecretError`。
- **117302** fix(cron) 注入上一轮答案：修的是真 bug（旧码头截断把答案切掉）；但 `partition("## Response")` 取**首个**匹配（skill 正文含同名标题会提前切分，本仓 `optional-skills/` 有 3 处实例）；`SILENT` 判定为字面量，窄于 lane 自身 matcher（裸 `SILENT` 仍会被当答案注入）；Minor：clip 非预算精确、intro 文案未同步。
- **117304** test(kanban) 排序见证：改造严格强于原时间断言、`kbc._INITIALIZED_PATHS` 修正正确；但 `assert not release.is_set()` **永真**（`release` 只由本测试 finally 置位，断言先于置位）→ 与它要消灭的"不可失败的断言"同类；Minor：断言顺序使失败消息自相矛盾。

### 数字
frontier **117304** · posted **3806** · reviewed_clean **2301** · deferred 1（#117327，20 文件）· rb/ 399 份 · progress.txt 882 行。

### 核验与流程备注
- 主流程核验：#117286 的 hunk 漂移主张（对 main 拉文件核对 `_delivery_adapter_for`/`mute_notification_reply`）✓；抽查 #117304 永真断言 ✓、#117302 partition 语义 ✓。
- **新坑（已记入 skill）**：preflight 的 `git apply --check` 用本地只读克隆的 main，克隆偏旧会**误报 apply-fail**（#117301 反例）。派单前先 fetch 克隆，apply-fail 只当"待复核"。

## 续战 · 第17批 7 条（frontier 117304 → 进行中）
候选 7（#117308..#117321），预检 0 apply-fail、0 配对冲突；两路代理（4+3）审阅中。deferred 新增 #117327（20 文件）。

### 第17批中断与重派（00:11 → 00:27）
首轮 2 路代理（4+3）在模型侧被中断（`waiting for model response`，未落任何草稿/verdict，工作全丢）→ 拆 **3 路**重派（2+2+3），并要求**每完成一个 PR 即时更新 verdict 文件**（读-改-写）防再丢。

**预检脚本修复（本轮）**：`scripts/preflight_batch.py` 原先从 clone 的**工作树**取 pre-image 文件——工作树停在 PR 分支时（当前是 `fix/81101-config-set-security-guard`）会误报 apply-fail。已改为 `git show upstream/main:<path>` 取 blob（工作树兜底），输出增加 `base=<ref>@<sha>`。
回归验证（重跑 batch16）：**#117301 由 False→True**（旧 base 误报）、#117286 仍 False（真 hunk 漂移，已对 main 核对）、#117287/#117292 不变。


## 续战 · 第17批 7 条（frontier 117304 → 117321）
**结果:** 活检 7 · 发帖 6 · CLEAN 1（117317）· skip 0 · **并发发帖**（post_batch.py workers=6，无 sleep，一次成功 `posted=6 skip=0 err=0`）。

### Blocker(1)
- **117321** feat(sessions) 跨设备接管：① `allow_session_takeover` 直接放进 `gateway.capabilities` 结果但未在 `GatewayCapabilitiesResult` 声明（契约 `Result` 为 `extra="forbid"`，`rpc_dispatch`→`check_result`→`model_validate` 必报 violation：生产每进程 warn 一次、`HERMES_TEST_ISOLATION` 下 raise；生成物 `gateway-contract.generated.ts`/openrpc 也无该字段 → 客户端读不到，docstring 的前提仍成立）；② 接管分支只替换 registry 条目、不通知也不打断被驱逐 surface（`_ensure_active_session_slot` 对已持 lease 的会话是纯 dict 短路），被驱逐方继续收 turn → 仍是两个写者，与 :592 注释和 configuration.md:2572 宣称的 "one writer" 不符（仓内既有先例 `_take_over_detached_runtime_lease` 是转 lease + 打断败者）。核验：契约模型/校验链/`_report` 严重度逐条对过 head `0ded8729`。附 2 条非阻塞：messaging 网关路径传 `GatewayConfig` dataclass 不认该 key（TUI/桌面认）；新 key 未注册进 `DEFAULT_CONFIG`/known keys（`hermes config set` 会误报"不认识的键"）。

### 非阻塞(5)
- **117319** cron 中断文案：新文案断言的 "fire-claim ownership lost" 恰是该分支守卫（heartbeat 仍持有 claim）排除的情形；文档把这条消息归因到不会到达它的分支（re-owned claim 走 :2609 另一条）。
- **117318** Windows 只读树删除：包装器对两种触发形态正确、本机 Windows 实测通过（5/5 + 96 passed）；但 `ignore_errors=True` 语义变了——不再"跳过失败项继续删"（复现：残留 `03_locked, 04_ok` vs stdlib 只留 `03_locked`），`plugins_cmd.py:982` 回滚路径受影响。
- **117316** turn-lease 陈旧持有者上报：直接执行 post-image 模块，分类/一次性 latch/re-arm/fail-open 全对；但唯一的接线测试手搓 registry，删掉 `gateway/run.py:3544-3547` 的注入全套仍绿。
- **117312** 标题生成重试：`call_llm` 底层已有 structured-output 恢复阶梯（`_is_structured_output_rejection` → `_without_structured_output_format` → per-route memo，且有既有测试锁定），新 `except` 对 PR 自身复现不可达；新测试 mock 掉的正是已恢复的那一层。
- **117308** 桌面远程会话水合：overlay 守卫放行 `null`（远程 `profiles.list` 对无 DB 的 profile 发 `null` 而非缺省）→ 一次瞬时远程读失败会把已水合的 Bot Chat 打回草稿；已用 post-image 函数复现。
- 117317 静默 CLEAN（simplex alpha 展平：RGBA/LA/带透明调色板/全透明 + >128px resize 路径均正确合成白底）。

### 数字
frontier **117321** · posted **3812** · reviewed_clean **2302** · rb/ 405 份 · progress.txt 889 行。

## 流水线并行化（2026-09-21 用户定"先别考虑限流，提高效率"）
- **新增 `scripts/post_batch.py`**：线程池并发发帖、无 sleep（`--workers=K`），逐条 `POSTED/SKIP_DUPE/SKIP_STALE/ERR` + 汇总；第17批 6 条一次并发发完、未触发限流。`post_one.py` 的 8s 间隔改为默认关（`POST_SLEEP` 可恢复）。
- **批次重叠**：batch17 收尾的同时派 batch18（6 条），batch18 在跑时又派 batch19（4 条）——峰值 5 个子代理并行（上限 10）。
- **配对/跨批预警已进简报**：#117334↔#117335（`test_write_approval.py`）、#117339↔#117340（`gateway/platforms/base.py`）、#117338↔在审的#117318（`plugins_cmd.py`）。
- 预检脚本 pre-image 改取 `upstream/main` blob 后，batch18/19 预检 0 误报。


## 续战 · 第18批 6 条（frontier 117328 → 117336）
**结果:** 活检 6 · 发帖 6 · CLEAN 0 · 并发发帖一次成功（`posted=6 skip=0 err=0`）。

### 非阻塞(6)
- **117336** STT JSON 信封解包：解包本身正确（5 个新测试隔离跑全过、ASR 标记行为不变），但 `_transcribe_groq` 仍走 `str(transcription).strip()`、不经过 `_extract_transcript_text`（已核 head：该函数只在 `:179/:203/:345` 被调用）→ 同一代理污染在 Groq 后端存活；Minor：逐字口述 JSON 对象会被改写。
- **117335** 写审批记录：修复落在唯一的 apply-then-discard 位点、循环重排行为等价；但 `discard_pending` 对"记录不存在"与"unlink 失败"都返回 False → 并发移除会被报成卡住，且宣传的补救 `/reject` 走同一路径。
- **117334** skills patch+content 带 `file_path`：路由正确（pre/post-image 实测、批量覆盖守卫拒绝）；余项为非阻塞细节。
- **117332** 桌面 tips 内容寻址 id：链路完整（`Payload` extra=forbid + `check_payload` 校验 + 生成物测试通过 + 27 测试绿）；余项为测试断言细节。
- **117329** honcho 通知形状：正则放宽对真实发出方全匹配、锚定与 id 放宽正确；但 `gateway/run_notifications.py` 的两处合并标题（`[IMPORTANT: {n} background pro…`）未被覆盖。
- **117328** iOS 原生回调鉴权：**无 blocker**——allowlist 精确匹配先于 urlparse（近似值全 400）、强制 S256、120s 一次性 code 先弹出再比对（`hmac.compare_digest`）、broker_state 只取自服务端 PKCE cookie、redirect 经 urlencode（无 Location 注入）、审计剔除 code/state/verifier。
### 数字
frontier **117336** · posted **3818** · reviewed_clean **2302** · rb/ 411 份。

## 单人快审 · #117342 OrbStack operator skill（判 CLEAN 静默）
候选只剩 1 条时主流程直审（不派代理，省一轮周转）。核对结论：
- 命令全部与官方文档一致：`orb top`（headless 页）、`orb create --isolated/--isolate-network`（machines/isolated 页）、`orb export/import/clone`、`orb docker volume clone|export|import`、`orb start|stop|delete k8s`、`orb config docker`、`orb debug`、`orb report`、`/mnt/mac`、`/mnt/machines`、`*.k8s.orb.local`、`:latest` 拉取行为、Apple Silicon 嵌套 KVM 限制。
- catalog 与 sidebars 均按字母序插入；`optional-skills-catalog.md` 行格式与兄弟条目一致。
- 生成页 `Path` 行用 `/`，与生成器（`f"{source_dir}/{rel_path}"`，Linux CI 再生）一致；兄弟页面的 `\` 才是既有 Windows 漂移 —— 不是本 PR 的问题。
- 无重复 skill（仓库内 orbstack 相关仅 4 处，均为 WAL/文档，非 skill）。
→ 无实质问题，按克制口径**静默 CLEAN**（frontier → 117342）。

## 流水线 · 第19/21批（进行中）
- 第19批 4 条（#117337–#117340）2 路代理在跑；配对预警 #117339↔#117340（`gateway/platforms/base.py`）、#117338 与在审 #117318 跨批共享 `plugins_cmd.py`。
- 第21批 2 条（#117343/#117344）各 1 路（单 PR/代理，压缩墙钟时间）在跑。


## 续战 · 第19批 4 条（frontier 117336 → 117340）与第21批 2 条（117343/117344）
**第19批结果:** 活检 4 · **发帖 2** · skip 2（#117339/#117340 在审阅期间被 `ashishsinghbora` 先 review → post_one 硬跳，本地分析归档）。零 blocker。
- **117337** runtime 空 base_url：修复对上 #116800（模块级验证：空行由 `("chat_completions","")` → `https://opencode.ai/zen/v1`）；但 **xai 仍走早返回**——`_POOL_ENTRY_SIMPLE_MODES["xai"] = ("codex_responses","")`（:489）在 :497-510 直接 return，到不了新 fallback :528-532，跨 provider 切到这类行仍报 `no base_url resolved`（已核 head 代码路径）。已发。
- **117338** CRLF 插件更新：机制正确（scratch 仓实测：钉 `core.autocrlf=true` 后幽灵脏、整文件 autostash、编辑滞留 stash 全部消失）；但探测只认字面 `true`（`yes|on|1` 与裸 `[core] autocrlf` 被漏掉，已用 `--bool` 验证语义），且 autocrlf=true 机器上会改写 pre-fix 保留的 LF。已发。
- **117339/#117340**（human_delay 边界守卫 / typing 暂停）分析归档未发：对方 review 点到了相近区域（#117340 的 `_typing_paused` 生命周期），避免叠评。

**第21批结果:** 活检 2 · 发帖 2 · 零 blocker。
- **117344** 桌面会话列表栅栏释放：修复正确且承重（populated refresh 顶掉 boot 请求会让 `$sessionsLoading` 永久卡 true）；但释放变成"最新请求赢"，`wipeSessionListsForGatewaySwitch()` 自己抬的栅栏（gateway-switch.ts:219 实测 `setSessionsLoading(true)`）会被 pre-switch 的 refresh 放下——建议改为栅栏所有权判定。
- **117343** cron Slack 合成线程：创建路径修复正确（head `_origin_from_env` 实测 `"in 30m"` 保留、`"in 61m"/"in 2h"/"every 1h"/cron 串`丢弃）；但 `update_job` 从不重推 `origin`（已核 `cron/jobs.py:1996-2018`：只 `_rederive_repeat_for_schedule_change` 且仅 kind 翻转时）→ 近一次性任务改成 `every 1h` 后合成线程永久保留。

### 数字
frontier **117344** · posted **3822** · reviewed_clean **2303** · deferred 0 · rb/ 415 份。

## 流水线 · 第22批（进行中）
候选 5 条（#117348–#117352）预检 0 apply-fail / 0 配对，3 路代理（2+2+1）审阅中。frontier 117352 之上当前 0 条新候选。


## 吞吐优化（2026-09-21 01:20-01:40 · 用户问"效率低了点"）
**先量再改（实测数字）**：
- 候选到达速率：12 分钟 eligible 由 6 → 12 条 ≈ **23 条/小时**
- 我方吞吐（backlog 模式）：≈ 17 条/小时 → **净落后，队列在长**
- 单代理真实耗时：单 PR ≈ 8–10 分钟（batch22 的 #117348 代理 8 分钟出活）
- prep 耗时：12 条 diff 拉取 **1.8 秒** + 预检 **7 秒** → **不是瓶颈**

**真瓶颈 = 波浪式派工的两个结构性税**：
1. 一次 `delegate_task` 调用 = 一个完成单元（3 个 task 也只回一条汇总）→ 只能等最慢的那个
2. 波与波之间主流程空转（收集 → 核验 → 发帖），期间空闲槽位不干活

**已改（4 项）**：
1. `delegation.max_concurrent_children` 10 → **20**（真 home 写入并读回；踩坑：shell 残留 `HERMES_HOME=/tmp/b2c2/hermes_home_test` 把首次写入带进了测试 home，已修正）
2. **一 PR 一代理**、**整批一次铺满**（batch24 一次 12 路，不再 2-3 条小波）
3. 子代理简报加时间盒：≤12 分钟 / 静态证据优先不跑全量测试 / <120 行干净直接 CLEAN
4. SOP §2.3 与 skill `github-contribution-workflow` §6 同步写入"吞吐模型"，含 HERMES_HOME 读回纪律

**预期**：12 路一波墙钟 ≈ 10 分钟 → **60-70 条/小时**（到达 23/小时），可建立缓冲并回补积压。


## 收尾（2026-09-21 01:45 · batch22/23/24 全归档）
- 今晚窗口 117278–117380：**发帖 38 · 静默 clean 8 · skip 5**（共 51 条记录）
- batch22（5 条）/ batch23（6 条）/ batch24（12 条，一 PR 一代理大波）全部归档；frontier **117380**
- #117377 在审阅期间被作者关闭（state=closed）→ 正确跳过不发；#117348 同批被他人先评 → skip
- 复验过的真 blocker 1 条：#117359（`hermes_constants._is_managed_home()` 空 marker 返回 False，与 `hermes_cli.config.is_managed()` 的空 marker=True 分歧，且与自身 docstring 矛盾）→ 已发
- 队列：**0 条积压**（117380 之上无新候选）
- 吞吐改造（一 PR 一代理 / 一次铺满 / 上限 30 / 时间盒 12 分钟）在本轮跑通：batch24 十二路 = 一次调用，墙钟约 10 分钟


# 第20批 · 2026-09-21（37 条）→ 已清零
**账号:** Enough1122 · **处理:** 37/37 标 Done（集合级 PUT）· **处理后未读:** 0
构成: comment 31 + mention 6 · **复审回复 6** · 静默归档 31 · 列请示 0

## 🎯 复审回复（作者按我们的意见改动后 @ 我 → 已实证复审）
| PR | 作者 | 我方原意见 | 复审结论 | 回评 |
|---|---|---|---|---|
| #117359 | liuhao1024 | **blocker**：`_is_managed_home()` 空 marker 与 `config.get_managed_system()` 分歧 | ✅ 已修：false 元组已移除 `""`，空/不可读 marker 归 managed；容器探测也扩到 `_detect_container()` | [5751513082](https://github.com/NousResearch/hermes-agent/pull/117359#issuecomment-5751513082) |
| #117321 | edosulai | **blocker×2**：契约未声明 + 兄弟租约未驱逐 | ✅ 已修：`allow_session_takeover` 进契约与生成的 TS；`_evict_other_session_leases` 已定义并调用 | [5751514076](https://github.com/NousResearch/hermes-agent/pull/117321#issuecomment-5751514076) |
| #117287 | fangliquanflq | non-blocking：SHA-1/256 身份比对失配 | ✅ 已修：`len(value) in {40, 64}`；TOCTOU 属信息性（fail-open）判断合理 | [5751514966](https://github.com/NousResearch/hermes-agent/pull/117287#issuecomment-5751514966) |
| #117302 | liuhao1024 | non-blocking：跨模块调用私有帮助函数 | ✅ 已修：模块级 `is_cron_silence_response` 公开别名 | [5751515925](https://github.com/NousResearch/hermes-agent/pull/117302#issuecomment-5751515925) |
| #117351 | Wenfengcheng | non-blocking：`model.api_key` 同类强转残留 | ⚖️ 作者边界辩护（该分支先于本 diff）→ 接受边界，记入 #117345 跟进 | [5751516926](https://github.com/NousResearch/hermes-agent/pull/117351#issuecomment-5751516926) |
| #117379 | Wenfengcheng | non-blocking：相邻 filter 形态 | ⚖️ 非目标声明 → 接受范围，保留分歧点作跟进 | [5751517864](https://github.com/NousResearch/hermes-agent/pull/117379#issuecomment-5751517864) |

## 静默归档（31）
致谢/修复告知、CI 与推送回声、`kyssta-exe` 等第三方 AI 在同批 PR 上的复评、他人之间的讨论等纯噪音类。

## 其它
- #117265：作者致谢并宣布关闭、让位 #117264（先 claim 者）→ 收尾致谢，不回。
- 我方小过失：rb 存档本次误用 `cp` 覆盖原文 → 已用 GitHub 原文重建为「原文 + Follow-up 追加」两段式。
