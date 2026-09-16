# Inbox 战报 · 2026-08-27

**账号:** Enough1122 · **处理:** 25/25 标 Done · **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 23 + mention 2

## 明细

- **mentions 2 条** 均为作者自述（非定向 @）：
  - #92492 `fix(desktop): confirm guarded model switches`（etzelvon, closed）— 作者自述 PR 描述，`opencode-go` 选 `muse-spark-1.2-contributor` 时 `confirm_required:true` 被忽略
  - #95101 `feat(authority): manifest schema + compiler + conformance harness`（andrexibiza, open）— 首次共享 Authority Policy ABI，重出现（持续订阅），正文为 PR 描述首段

- **正文含 @Enough1122:** 0 条

- **第三方评论 1 条**（非 @）：
  - #71337 `fix(wecom): omit body from heartbeat ping`（ijevin / rihaku899）— `rihaku899` 2026-08-26 对 `main@9aa7530` 的验证更新，`wecom/adapter.py` 仍以 `body:{}` 发心跳，regression 覆盖已验

- **其余 22 条 comment**：作者自更新 14 / 无评论实体 8 / teknium1 收尾 0，均无 @，属订阅噪音

## 处置

- 25/25 标 Done，失败 0，收件箱归零
- 无需逐条回复；第三方 wecom 验证与 2 条 mention 均为信息性归档

## 待跟进

- 无新增阻塞；延续 08-26 第四批待复审：#95418、#94922、#86322、#92730（diff 已拉取，待你确认是否现在出评论）— #94096 已闭环

---

# 第二批 · 2026-08-27 晚间（140 条）→ 已清零

**账号:** Enough1122 · **处理:** 140/140 标 Done（+1 迟到 25305459803）· **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 129 + mention 11

## 关键信息（需关注）

- **#94096 `fix(matrix): add MAS refresh-token` — vlify 现场验证翻车** (`mention` vlify → Sahilvishnaliya)
  2026-08-27 16:19 vlify 对 `35a3cf70` 的活体复测：刷新逻辑本身正确，但 OIDC 发现 URL 写死为 `https://matrix-client.matrix.org/.well-known/openid-configuration` 在 matrix.org 上 **404**（`matrix.org` 同 URL 返回营销页 HTML 导致 JSON 解析失败，`matrix-client.../.well-known/matrix/client` 亦 404，真正可用的是 `https://account.matrix.org/.well-known/openid-configuration` → `token_endpoint https://account.matrix.org/oauth2/token`）。另发现 `_try_mas_oauth_refresh` 用 `urllib.request` 直连、忽略 `MATRIX_PROXY`，经代理 1.8s vs 直连 7s，10s 超时易踩。测试套件 `routed()` 对任意 `openid-configuration` URL 均返回桩数据，未断言具体 URL，故未捕获。此为你此前 review 闭环后新的集成层缺陷，建议：新增 `MATRIX_OAUTH_TOKEN_ENDPOINT`/`MATRIX_OIDC_ISSUER` 配置覆盖，或从 `/.well-known/matrix/client` 的 `m.oauth_metadata` 解析（但该文件同 404，配置覆盖更务实）。

- **#95440 `fix(redact): mask age (filo.io) secret` — pjrobot 致谢你**
  `@Enough1122 — you're right, and thank you: that's a real bug, not a nitpick. The bech32 class [1-9A-HJ-NP-Za-km-z] was wrong in both directions: Excluded 0 and l — both valid bech32 data chars, each occurring at ~1/32 per body position, so the ~97% of real age keys containing at least one was unmasked. 你的 review 指出的脱敏正则漏 `0`/`l` 属实，作者已修。

- **#86322 `feat(a2a): per-peer custom headers` — andrexibiza 最终验收**
  `Final exact-object acceptance receipt for head 7fe503c66d...` — 同步确认 destination-bound credentials、跨域重定向、524 幂等、replay/origin 测试均已闭环。信息性（呼应你 08-26 的 blocker）。

- **#86062 `fix(state): recover from malformed legacy FTS` — Christopher-Schulze 收敛**
  `Convergence follow-up is now on 85283ad57f. Imported @strzhao's 1d0e71e822 content ...` 与 08-26 的 marker-gate 已收敛，信息性。

- **kuehnberger 三连** #87302 / #86612 / #86578 — 均标注 `Enough1122 verified ... now resolved`，将你之前的 AI review 标记为已解决，@teknium1 等待人工复核。信息性归档。

- **第三方评论 11 条抽样（非 @）**：`dokterdok` 在 pierrenode/giaiant/pesho-vsn 三处声明 `draft #95965` 合成 RoomLink 栈并保留原作者署名；`yuzilongleif-collab` 对 locomail 的 auth 隔离复现并提交 `locomail/hermes-agent#1`；`TwoRobotsinaTrenchcoat` 确认 `rainbowgore` 的 plugins 预算可配置改动有真实需求（已关 #95908）；其余如 `seagpt` 补充 Android 渲染、`iyurinok` 指出 Slack 同 `ts` 双写等，均为作者自洽推进，无需回复。

## 明细

- **mentions 11 条**：teknium1 跟踪 #91277（28 PRs 当日合并战报）、fred0m #91374、aryn-lacy/andrexibiza 上述、kuehnberger×3、Christopher-Schulze×1、Wenfengcheng×1、Sahilvishnaliya/vlify 上述、pjrobot 上述
- **正文含 @Enough1122：** 1 条（#95440 pjrobot）
- **第三方评论（pr_user ≠ lc_user）：** 11 条，均为上述 `dokterdok` 合成、跨仓库复现等，无定向提问
- **其余 ~128 条 comment**：作者自更新/无实体/teknium1 收尾，订阅噪音

## 处置

- 140/140 标 Done（+1 迟到），失败 0，收件箱归零
- 关联报告：`_inbox_report_2026-08-27.md`（本文件）已更新

## 待跟进（更新）

- **新增阻塞：** #94096 需追加 `MATRIX_OAUTH_TOKEN_ENDPOINT` 配置覆盖 + 代理透传 + 测试断言精确 URL（vlify 已给修复方向）
- **延续：** #95418、#94922、#86322、#92730 仍待你确认是否现在出评论
- **已致谢：** #95440 收到 pjrobot 致谢，无需回

---

# 第三批 · 2026-08-27 深夜（45 条）→ 已清零

**账号:** Enough1122 · **处理:** 45/45 标 Done（+2 回评发出）· **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 42 + mention 3

## 定向 @Enough1122（2 条）→ 已核验并回评

### #94503 `fix(delegate): report non-retryable child failures accurately`（Wenfengcheng）
作者逐条辩驳 head `6b85acc` 无需 follow-up。**三处引用全部实证核实：**
1. `delegate_tool.py:3050-3056` — `_child_failed = bool(result.get("failed"))` 显式契约,注释明确"completed=False 不等于失败";3 个回归测试钉死三个象限(failed→failed 逐字 error / interrupted 优先于 failed / 预算耗尽带 summary→stays completed+truncated)
2. `delegate_tool.py:3128-3135` — entry 恒含 `"summary": summary`,interrupted 保留 final_response 文本,仅结构化 error 省略(测试断言 NotIn);同意不扩大 #82599 契约
3. `async_delegation.py:859-876` — `_worker()` 单次调用 runner(),仅透传 `result.get("status")` 进 `_finalize`,无重试循环、不读 exit_reason
- 回评:[#issuecomment-5434335399](https://github.com/NousResearch/hermes-agent/pull/94503#issuecomment-5434335399) 接受 as addressed

### #94631 `fix(desktop): preview files only on intentional activation`（Wenfengcheng）
作者辩驳 head `b283a2f`。**核实：**
1. `tree.tsx:327-333` — onDoubleClick stopPropagation + 非 folder/placeholder/renaming 守卫 → onPreviewFile,独立行级路径;移除 Arborist onActivate 只删通用单击/Enter 通道
2. `NodeApi` 直接 import 移除;`treeRef.current?.focusedNode` 使类型经 TreeApi 传递;新 `tree-activation.test.tsx` 钉死"激活不开预览 + Space 开预览"
3. `beginInlineRename` 为模块 import,正确不在 `[onPreviewFile]` 依赖数组;Space 分支先 early-return 保持互斥;capture-phase 保留且现在两个 handler 共享同一抢占需求,合并合理
- 回评:[#issuecomment-5434336492](https://github.com/NousResearch/hermes-agent/pull/94631#issuecomment-5434336492) 接受 as addressed

## 迟到致谢核验（信息性）
- **#94426 `fix(desktop): drop persisted tiles of deleted bots`（Finn763,08-25 评论迟到）** — 致谢并称全部意见已在 `ed3968ea` 修复。轻验 diff 属实:`ownerRoute predates the connectionId` 回归测试存在、`(ownerConnection || 'local')` 归一化存在(5 文件)。无需回复

## 其余 42 条
- 第三方评论 1 条:#feishu lark_oapi WS 隔离(pittosporum-seu PR),zhaomengfan 生产 5-profile 复现背书 `Future attached to a different loop` 崩溃,信息性
- 其余均为作者自更新(lc_user=None 的 PR body 更新 30 条 + 作者自评论 12 条),无 @,订阅噪音

## 待跟进（不变）
- 延续:#95418、#94922、#86322、#92730 待确认是否出评论
- #94096 新缺陷(vlify 发现 OIDC URL 404 + 代理透传)待追加跟进评论

---

# 第四批 · 2026-08-28 凌晨（28 条 + 迟到 1 条）→ 已清零

**账号:** Enough1122 · **处理:** 28/28 标 Done（+1 迟到 25277698974）· **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 27 + mention 1 · 定向 @: 0

## 🎯 实际动作:#92730 复审闭环回评

**#92730 `fix(desktop): prevent cache eviction of optimistic user message`（DavidMetcalfe）**
mention 为作者确认 @MiMoHo 的跨轮回归(08-27 05:34Z,新 head `4534d111a5`)。完整链条:我 08-23 review 揭出 pending 永不清 → warm-cap 泄漏 → 作者首轮 blanket wipe → MiMoHo 复现 blanket wipe 清掉 queued 轮保护 → 作者 scoped 修复。**已对照 `4534d111a5` diff 实证核验并回评:**
1. `use-message-stream/index.ts:725-742` — `boundaryIndex` 取 `prev`(pre-settle)几何,仅 `i < cutoff` 的 user 行退休;无 tracked 行时 cutoff=0 清零不动。pre-settle 修正正确:`assistant-error-*` 伪造 id 与 `streamId: null` append 分支的落点都在 queued 行之后,post-settle 切割不安全
2. 未跟踪失败路径清零 + 延迟到 `finalizeInterruptedMessages` — 一致的设计取舍,非泄漏
3. `scoped-pending-settle.test.tsx` — 4 个 reducer 实驱 spec;mutation 逻辑自洽(blanket wipe 必挂 spec1 的 `userNext.pending === true`)
- 回评:[#issuecomment-5434954593](https://github.com/NousResearch/hermes-agent/pull/92730#issuecomment-5434954593) 接受 as addressed

## 其余 27 条
- 第三方评论 2 条(非 @):G-byNature 验证 fangliquanflq 的 `GET /v1/tools`(隔离克隆 12/12);tadeogutierrez 独立验证 rorsch 的 bot-mode 修复(cherry-pick 干净 + 16/37 测试通过)。均信息性
- 其余 25 条:作者自更新 + 已关 PR 收尾(含此前战役 review 过的 #95327 链 liveness、#95389 SSH profile 等已 merged/closed),无 @,噪音归档

## 待跟进（更新）
- **#92730 已闭环移出**;延续:#95418、#94922、#86322 待确认是否出评论
- #94096 新缺陷(vlify 发现 OIDC URL 404 + 代理透传)待追加跟进评论

---

# 第五批 · 2026-08-28（21 条 + 迟到 1 条）→ 已清零

**账号:** Enough1122 · **处理:** 21/21 标 Done（+1 迟到 24492635289）· **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 19 + mention 1 + state_change 1 · 定向 @: 0

## 🎯 实际动作 2 条回评

### #94096 v2 验证 + 新 nit（Sahilvishnaliya,head `75e388e3`）
vlify 发现 OIDC URL 404 后作者推 v2。**4 项声明全实证:**
1. 三级解析:`MATRIX_OAUTH_TOKEN_ENDPOINT` 直接覆盖(跳过 discovery)→ `MATRIX_OIDC_ISSUER`(issuer host 发现)→ homeserver `.well-known/openid-configuration` → MSC2965 `m.oauth_metadata.issuer` 指针 + 耗尽 hint
2. `MATRIX_PROXY` ProxyHandler(SOCKS 警告忽略)
3. 精确 URL 测试(monkeypatch urlopen 记录 probed 列表断言顺序)— 修掉 v1 的"stub 对任意 URL 返回桩"缺口,共 7 个新测试
4. 附加 `__init__` 分裂修复;我原 nit2 dead fallback 已正确修复(`unrecognized_` 回退 + `!= self._refresh_token` 守卫);`_MAX_REFRESH_ATTEMPTS=8` + Lock double-check
**新发现 nit(#2 功能缺口):`_build_opener()` 只用于 token POST,`_resolve_oauth_token_endpoint` 的两个 discovery fetch(OIDC doc + MSC2965)仍裸 `urlopen` 直连、绕过 `MATRIX_PROXY`** — vlify 数据(discovery 直连 7s vs 代理 1.8s,10s 超时)下 issuer-override/default 链在 proxy-only 网络会超时;建议 hoist 共享 opener 供 discovery 复用(override 模式不受影响)。回评:[#issuecomment-5435753140](https://github.com/NousResearch/hermes-agent/pull/94096#issuecomment-5435753140)

### #96080 自己旧 PR #79340 被捡起(TwoRobotsinaTrenchcoat)
#79340(hooks 四字段透传)系自己 08-21 backlog 清理主动关闭;TwoRobotsinaTrenchcoat 重建为聚焦新 PR #96080 并主动提出加 Co-authored-by 署名。已回评同意署名:[#issuecomment-5435755332](https://github.com/NousResearch/hermes-agent/pull/96080#issuecomment-5435755332)

## 其余 19 条
- 第三方评论 5 条(非 @):Finn763 在 #95327 链补第二台 Win11 复现证据;Finn763 让渡关闭 #96113 予 #85660;kshitijk4poor 告知 #75750 链 cherry-pick 合并署名保留;TwoRobotsinaTrenchcoat 分享跨平台 session remapping fork 经验;alt-glitch 报 SIGUSR2 PR 为 #75750 重复。均信息性
- 其余 14 条作者自更新,无 @

## 待跟进（更新）
- **#94096 待 v2 回应**(nit: discovery fetch 不走 proxy)— 已从"待发跟进评论"转为"已回评等作者"
- 延续:#95418、#94922、#86322 待确认是否出评论
- #96080 关注署名落地(非阻塞)

---

# 第六批 · 2026-08-28（44 条 + 迟到 1 条）→ 已清零

**账号:** Enough1122 · **处理:** 44/44 标 Done（+1 迟到 25303704112）· **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 43 + mention 1 · 定向 @: 0

## 明细

- **mention 1 条:** #85609（paoloantinori,journal_mode=delete 被 WAL 覆盖时告警,已关）— 作者自述 PR 正文,订阅触发,信息性
- **第三方评论 3 条（非 @）:**
  - #87727（derinbarutcu17,kanban 附件预览）— muctobi 独立安全审查跟进:`attachmentFileUrl` 应先拒不支持的路径形态再过 OS bridge(Electron 原生日志护栏之外)
  - #54285（jeeves-assistant,discord auto-thread）— alt-glitch AI triage 注记:本 rebase 版走 config-backed 设计,关联 #27651
  - #94163（ColDSnit,no-first-byte watchdog）— DanBennettUK 提供脱敏实测证据:openai-codex/gpt-5.6-luna 940 次调用,p90 26.1s、11 次 ≥60s、最大 341.7s,支撑 watchdog 必要性
- **issue +1 1 条:** #38007（system tray 需求）— youssefbm2008 Windows 用户 +1 close-to-tray,信息性
- **其余 39 条:** 作者自更新 21 + 无评论实体（PR body 更新）18,含 vKongv 五连 profile 路由系列、Doud-FR 三连、jeeves-assistant 三连、jackulau/teknium1 收尾等,均无 @
- **迟到 1 条:** kshitijk4poor 在 `fix(mcp): harden stdio transport recovery` 的 triage 注记——`_stdio_children_dead` 极性修复已上 main(#94339)、reconnect-on-fast-fail 正被 #96452 打捞,该 PR 剩余独特件为 spawn-lock/PID 归因 + idle-probe 重设计。信息性

## 处置

- 45/45 标 Done,失败 0,收件箱归零;无需逐条回复
- 待跟进 PR 状态核验:五个 head 均未动(95418 `aae50f91` / 94922 `113022e9` / 86322 `7fe503c6` / 94096 `75e388e3` / 96080 `e9bfae5e`),无新变化

## 待跟进（不变）
- 延续:#95418、#94922、#86322 待确认是否出评论
- #94096 等作者回应 proxy-discovery nit
- #96080 关注署名落地(非阻塞)

---

# 第七批 · 2026-08-28:三个待复审 PR 出评完成

**账号:** Enough1122 · 用户确认后发评 3 条 · 依据：当前 HEAD diff 全文实证核验

## 🎯 #95418 codex-runtime TOML 迁移(YusenZhang0601)→ ✅ 接受 as addressed
head `aae50f91ff`。之前 5 点 review **全部核实落地:**
1. bare `[mcp_servers]`/`[plugins]` 仅在段体无 kv 时才剥(单测+e2e 双覆盖)
2. `_update_bracket_depth` 字符串/注释感知的括号深度门控三个扫描器;我原报的 `['write']` 单元行已成回归测试
3. conflict_policy 白名单在任何变更前 fail-fast,测试断言不落盘
4. `\u`/`\U`/`\x` 非法转义和尾点均 `return None`(旧的 raw re-append fallback 已删)
5. tomllib→tomli→None 链式导入,守卫在两者皆无时跳过,不再是最脆弱环节
附非阻塞残留 2 条:多行字符串(`"""`/`'''`)内不平衡括号会使深度追踪失明(fail-closed,被 tomllib 守卫兜住);bare 段内联 server 与 Hermes 同名冲突时报错信息可点名 `preserve_user` 出口。
回评:[#issuecomment-5441234988](https://github.com/NousResearch/hermes-agent/pull/95418#issuecomment-5441234988)

## 🎯 #94922 dashboard secrets 落盘(iborazzi)→ ⚠️ 部分放行,列残留
head `113022e963`。**声明 1-3 实证为真:** PUT 的 `_CONFIG_MUTATION_LOCK`/`_approval_mode_of` 比较/`_broadcast_gateway_session_info()`/to_thread 全部恢复;GET 保持 off-loop 且 `_deep_merge(resolved, raw)` 形状正确;cron drift(`load_config()`→`resolve_cron_model_drift_defaults`)与 `_gateway_fire_endpoint` 均已回 resolved 配置。**声明 4 为假 + 新问题:**
1. ❌ 信号处理/port-bind 注释删除**仍在 diff 中**("rebase 已恢复注释"与树不符)
2. ❌ 新回归测试钉错半侧:mock 双 reader 断言 GET 响应无 secret——该断言 main 上今天也能过(归一化器本就屏蔽);真正的契约(disk 有 `${VAR}` → PUT → disk 仍留占位符)无任何 save_config 驱动
3. ⚠️ tests/test_web_server.py 获 BOM + em-dash mojibake(`â€”`);test_ssh_ownership_endpoint.py 混入无关的 `pytestmark` 全局 warning 抑制
回评:[#issuecomment-5441235403](https://github.com/NousResearch/hermes-agent/pull/94922#issuecomment-5441235403)

## 🎯 #86322 a2a per-peer headers(aryn-lacy)→ ✅ 接受 as addressed
head `7fe503c`。**双 blocker 均真实闭环:**
- Blocker 1(幂等契约空头支票)**以诚实拆除闭环**:524 重试阶梯整体删除→`_A2aIndeterminateError` 单次请求;`idempotency` peer key 不复存在;文档"Hermes peers dedupe"假断言换成明示缺口的段落;陈旧 bare-fetch 注释已删。`Test524Indeterminate` 钉死单请求+零 sleep
- Blocker 2(allowlist 未接 POST):`_send_task` 计算 `allowed` 一次,贯穿 card fetch 与 task POST;`TestSendTaskRedirectAllowlist` 驱动真 `_send_task` 起双 loopback server 双向验证(pinned 收到凭据/unpinned 外站命中 0)
- 复审加固成立:scheme 降级/端口变化非同源、`:0` 不当默认端口、allowlist 原点级匹配(`trusted.evil.example` 拒绝)、CT/A2A-Version dict 序后置不可 clobber、fanout 转发 headers+allowlist
附 note 2 条:524 首投学不到 server task id(#94880 的既有 surface);`register_tools` unwrap 与上游 cefeed4ca 重复建议拆出。
回评:[#issuecomment-5441235768](https://github.com/NousResearch/hermes-agent/pull/86322#issuecomment-5441235768)

## 待跟进(更新)
- **复审积压清零**:#95418/#86322 已闭环,#94922 待作者处理 3 项残留(注释恢复/真回归测试/编码卫生)
- #94096 等作者回应 proxy-discovery nit
- #96080 关注署名落地(非阻塞)

---

# 第八批 · 2026-08-28(99 条)→ 已清零

**账号:** Enough1122 · **处理:** 99/99 标 Done · **处理后未读:** 0
**快照:** `drafts/_inbox_triage.json` · 全部 NousResearch/hermes-agent
构成: comment 94 + mention 5 · 定向 @: 0

## 🎯 实际动作:两条收尾回评(均实证核验后放行)

### #94096 matrix MAS refresh(Sahilvishnaliya,head `9fa494d3`)→ ✅ 闭环 merge-ready
作者推新 head 回应我的 proxy-discovery nit:新增 `_mas_urlopen()` 统一出口(MATRIX_PROXY HTTP/HTTPS 生效,SOCKS 记录后忽略并注明 aiohttp 归属)。**diff 实证:** OIDC doc(`_fetch_well_known`)、MSC2965 matrix/client 指针、token POST 三处 fetch 全部经由 `_mas_urlopen`,resolve 路径已无裸 `urllib.request.urlopen`;override 路径仍零网络短路。vlify 活体复验(discovery 经代理 ~1.1s、override 零网络、伪 token POST 形状不变 invalid_grant)。
回评:[#issuecomment-5447359070](https://github.com/NousResearch/hermes-agent/pull/94096#issuecomment-5447359070)

### #94922 dashboard secrets(iborazzi,head `eb757d01ee`)→ ✅ 闭环 as addressed
作者静默推新 head 处理我提的 3 项残留。**diff 实证:**
- 信号处理/port-bind 注释删除已从 diff 消失(现仅触 web_server.py 的秘密交换面 + 测试),`_loop_factory` 空白 hunk 也已清
- 真回归测试 `test_put_config_preserves_env_var_placeholder_on_disk`:驱动真 `update_config()` 对真 config.yaml,PUT 无关键,断言 `${TEST_OPENAI_SECRET}` 仍在盘上且 resolved 值不落盘——PUT 退回 `load_config()` 即红;`_RAW_CONFIG_CACHE` 清理也正确绕开 (mtime_ns,size) 缓存碰撞
- BOM/mojibake/无关 pytestmark 全部清除,test_ssh_ownership_endpoint.py 不再被碰
回评:[#issuecomment-5447359232](https://github.com/NousResearch/hermes-agent/pull/94922#issuecomment-5447359232)

## 其余 97 条
- **mention 其余 3 条**:#93006 dokterdok、#92122 autumn8-builds(PR body 更新,无评论实体)、#83618 DavidMetcalfe(TomSpoct 第三方复现 sidebar 重命名 Space 缺陷证据)→ 信息性
- **第三方评论 14 条(非 @)**:kshitijk4poor 在 6 个 perf PR(StanleyStetson/peetteerr/Adolanium/SomSamantray/Finn763/fangliquanflq)的 review 跟进、vlify 在 teknium1 pricing PR 的复测、CryptoKylan 评 claude-agent-sdk、Xipong/thinkyhead/eabase/zorroukk×3/jack59873298/donovan-yohan/orcaspainting-dev 等 → 均作者社区自洽推进
- **其余 ~80 条**:作者自更新 + 已关/已合 PR 收尾(含 #95370 cron 已 merged、helix4u 反向代理已 merged),订阅噪音

## 待跟进(更新)
- **复审线全部闭环**:#95418、#86322、#94096、#94922 均无未决项
- #96080 关注署名落地(非阻塞)

---

# 第九批 · 2026-08-28(28 条)→ 已清零

**账号:** Enough1122 · **处理:** 28/28 标 Done · **处理后未读:** 0
构成: comment 26 + mention 1 + ci_activity 1

## 明细

- **mention 1 条(#94922 iborazzi)**:作者回我放行评后 ping @teknium1 请求 maintainer 合入,自述四点(my review 全部 as of `eb757d0` addressed)+ 实 GET→PUT→disk 回归测试 + 卫生清理,与我核验结论一致 → 信息性,需等 maintainer
- **ci_activity 1 条**:自己已关闭的旧 PR #73814(`fix(docker): docker_volumes` 重解析)分支 CI 重跑失败——该 PR 早已关闭,暂不打算重开;失败留档备查,信息性归档
- **其余 26 条 comment**:作者自更新 9 / 无评论实体 6 / 已关 PR 收尾 6 / 第三方评论(均不指向我)。无 @me

## 处置
- 28/28 标 Done,失败 0,收件箱归零;无需逐条回复

## 待跟进
- #94922 等 teknium1 maintainer 复核(我的 acceptance 已在 `eb757d01ee` 落位)
- #96080 关注署名落地(非阻塞)

---

# 第十批 · 2026-08-28(33 条)→ 已清零

**账号:** Enough1122 · **处理:** 33/33 标 Done · **处理后未读:** 0
构成: comment 30 + mention 3 · 定向 @: 0

## 明细

- **mention 3 条**:embwl0x ×2(#83989 body 更新;#82120 冲突刷新发布 `c18f3d85` rebase 现 main,自述保留 connection-owner 路由/transcript hydration)、#92122 autumn8-builds body 更新 → 均信息性
- **第三方评论 2 条(非 @)**:TheSmokeDev 在 #95147 提供 realtime voice 消费侧 field notes(三 provider 已 live-verify);RickTorresJr 在 #92905 呼吁关注 hard context ceiling PR(非定向)
- **其余 28 条**:作者自更新/无实体/已关收尾,订阅噪音

## 处置
- 33/33 标 Done,失败 0,收件箱归零;无需逐条回复

## 待跟进(不变)
- #94922 等 teknium1 maintainer 复核
- #96080 关注署名落地(非阻塞)

---

# 第十一批 · 2026-08-28(28 条)→ 已清零

**账号:** Enough1122 · **处理:** 28/28 标 Done · **处理后未读:** 0
构成: comment 27 + mention 1 · 定向 @: 0

## 明细

- **第三方评论 1 条(非 @)**:tachyon-r 在 #93858(cron execution-ledger 可配置保留上限)贴生产验证:某 profile 单 `*/5` 任务填满 1000 行 ledger(979/1000),仅保 2 次报告执行——佐证 #93616 同型故障,支撑该 PR 必要性 → 信息性
- **mention 1 条**:#92122 autumn8-builds,无评论实体(PR body 更新)
- **其余 26 条**:作者自更/无实体/已关收尾,订阅噪音

## 处置
- 28/28 标 Done,失败 0,收件箱归零;无需逐条回复

## 待跟进(不变)
- #94922 等 teknium1 maintainer 复核
- #96080 关注署名落地(非阻塞)

---

# 第十二批 · 2026-08-28 批量 review 战役 — 500+ PR 并行清场

**战役口径：** 断点 #95521 起（上次 08-26 打到 #95515），open + ≤8 文件 + 无评论 + 无 review + 非 draft，经活检与 diff <60KB 双重闸门，子代理并行，逐条读 diff 实证，单条 sleep 8。

**规模：** 候选 **575**（≤8 文件），**已发 313 条** AI review（本轮新增 260 条，13 个 chunk 并行），剩余 262 为跳过项（>60KB / 已有关注 / 已关 / 404）。收件箱保持归零。

**本轮新增 260 条明细（chunk 1-13）：**

| Chunk | 区间 | Posted | 代表 PR |
|-------|------|--------|---------|
| 1/13 | 95574-95870 | 23 | 95769 lint, 95773 send 5, 95787 skill |
| 2/13 | 95871-96011 | 32 | 95871 credential, 95919 mirror, 96000 profile |
| 3/13 | 96013-96097 | 27 | 96013 auth pool, 96060 clarify 熔断, 96097 flood |
| 4/13 | 96106-96172 | 12 | 96106 Telegram media, 96141 delegate model |
| 5/13 | 96210-96330 | 18 | 96210 group chat, 96314 format |
| 6/13 | 96333-96444 | 23 | 96333 streaming finish, 96444 catalog |
| 7/13 | 96467-96535 | 14 | 96467 transform_llm_output, 96535 Kanban |
| 8/13 | 96549-96622 | 15 | 96549 tuple, 96622 voice |
| 9/13 | 96635-96732 | 18 | 96635 off-loop, 96728 whatsapp |
| 10/13 | 96736-96841 | 19 | 96736 scope 隔离, 96841 whatsapp |
| 11/13 | 96851-96939 | 20 | 96851 ASYNC ratchet, 96939 tokenplan |
| 12/13 | 96940-97032 | 22 | 96940 clippy, 97032 skills |
| 13/13 | 97036-97086 | 17 | 97036 lint, 97086 skills |

**处置：** 全部以 `> AI code review — automated review for reference; please use your judgment.` 开头，基于当前 HEAD diff 发至 `issues/{n}/comments`（201），间隔 8s，已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`。

**待跟进（更新）：**
- 批量 review 战役基本打平，剩余 pending 多为大 diff / 已关 / 404，需人工关注的阻塞已在单条评语中标注 Non-blocking/blocker 分层。

## 待跟进（当前）
- #96080 署名落地（非阻塞）
- 批量 review 剩余跳过项无需行动，已评 PR 等作者/maintainer 响应

---

# 第十三批 · 2026-08-28 (38 条)→ 已清零

**账号:** Enough1122 · **处理:** 38/38 标 Done · **处理后未读:** 0
构成: comment 34 + mention 4 · 定向 @: 1

## 定向 @Enough1122（1 条）

- **#96892 `fix(cli): hermes start/stop/restart root aliases`（Bartok9）** — 回应我对 #96892 的 review：同意保持 root 仅生命周期（start/stop/restart），`hermes gateway …` 仍为完整控制面；CI 已绿，回归测试覆盖 parity 用例。致谢，无需再评。

## mention 其余 3 条

- **#94426 `fix(desktop): drop persisted tiles of deleted bots`（Finn763）** — teknium1 告知已通过 #97069 rebase-merge 合入，我的三 commit 以原作者身份落 main；双删除路径均清 tile bucket 与 Bot tile。信息性，致谢已收。
- #92122 autumn8-builds、#93006 dokterdok — 无评论实体，PR body 更新，信息性。

## 第三方评论 2 条（非 @）

- teknium1 在 #94426 同步上述合入信息（与 mention 重叠）。
- eabase 在 #95147（kvnloo voice session）对 TheSmokeDev 的人文表达诉求，非定向。

## 其余 32 条

- 作者自更新/无实体/已关收尾，订阅噪音。

## 处置

- 38/38 标 Done，失败 0，收件箱归零；无需逐条回复。

## 待跟进（不变）

- #96080 署名落地（非阻塞）
- 批量 review 313 条已发，等作者/maintainer 响应

---

# 第十四批 · 2026-08-28 (15 条)→ 已清零

**账号:** Enough1122 · **处理:** 15/15 标 Done · **处理后未读:** 0
构成: comment 14 + mention 1 · 定向 @: 0

## 明细

- **mention 1 条（teknium1 → #94338，已关）:** #94338 `fix(desktop): drop malformed mcp_servers entries instead of crashing` 已 via #97127 cherry-pick 落 main，署名保留，并补充了 MCP 健康巡检与命令面板经同一 `getServers()` 卡点的 follow-up。信息性致谢。
- **第三方 2 条（重叠上述）:** teknium1 同上；toughCSB 在 #95360（Finn763 Windows SSH 清单）补 E2E 复现证据（macOS → SSH → Windows 后端）。均非定向。
- **其余 12 条:** 作者自更新/无实体/已关收尾，订阅噪音。

## 处置

- 15/15 标 Done，失败 0，收件箱归零；无需逐条回复。

## 待跟进（不变）

- #96080 署名落地（非阻塞）
- 批量 review 313 条等响应

---

# 第十五批 · 2026-08-29 (36 条)→ 已清零

**账号:** Enough1122 · **处理:** 36/36 标 Done · **处理后未读:** 0
构成: comment 34 + mention 2 · 定向 @: 0

## 明细

- **mention 2 条:**
  - #92090 jackulau（fix desktop-entry keep venv Exec）— cosminfuica 按我 review 步骤 3 做的端到端验证（Arch/Hyprland, uv venv, Python 3.11.16，venv 拓扑即该 PR 修复的形态），全部通过 → 我曾要求的可复现验证闭环
  - #92122 autumn8-builds — 无评论实体，PR body 更新
- **第三方 5 条（非定向，重叠上述）：**
  - cosminfuica 同上；evan-bradford 在 #95992/#89736 告知互补分支 #97359（owner 传播重叠）；mateusdka 在 #95899 验证对 main 的回归（10/10 红→绿）；FestoneX 在 #84681 确认发现点位置。均信息性。
- **其余 29 条:** 作者自更新/无实体/已关收尾，订阅噪音。

## 处置

- 36/36 标 Done，失败 0，收件箱归零；无需逐条回复。

## 待跟进（不变）

- #96080 署名落地（非阻塞）
- 批量 313 条等响应

---

# 第十六批 · 2026-08-29 续战 — 沿上次 review 位置继续（97087-97397）

**口径：** 上次打到 #97086，本批新开 **97087-97397**（最新 PR #97397），open + ≤8 文件 + 无评论 + 无 review + 非 draft，经活检与 diff <60KB 闸门，子代理 5 路并行（各 25，按编号序，单条 sleep 8）。

**规模：** 新候选 **125**（>97086），**已发 123 条**（skipped 2：97129 已有评论 / 97395 已关），全部以 `> AI code review — automated review for reference; please use your judgment.` 开头。

**明细（chunk 1-5）：**
- 1/5 97087-97145：24 发（97087 bot-mode resume, 97100 macOS libpython, 97140 gateway public replies 等）
- 2/5 97146-97214：25 发（97146 toolset, 97183 kanban, 97201 kanban claim 等）
- 3/5 97215-97265：25 发（97220 Schedule 误杀 allowlist, 97226 worktree 等）
- 4/5 97269-97326：25 发（97270 approval explicit, 97326 group-chat cap 等）
- 5/5 97328-97395：24 发（97328 credential-pool, 97392 SSH 等；97395 已关跳过）

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`，POST 201。

## 待跟进（更新）

- 批量累计 **436 条**（575 + 125 新候选）已发，剩余跳过项均为大 diff/已关/404/已有评论，无新增阻塞
- #96080 署名落地（非阻塞）

---

# 第十七批 · 2026-08-29 (108 条 + 迟到 2 条)→ 已清零

**账号:** Enough1122 · **处理:** 108/108 标 Done（+2 迟到 25225103031/25109949515）· **处理后未读:** 0
构成: comment 98 + mention 9 + subscribed 1（含 killop/anything_about_game 1 条跨仓库订阅）

## 🎯 定向 @Enough1122（3 条）→ 实证核验后 2 条回评

### #96414 credential-pool 429 hot-loop（olopez25）
作者 head `1bf7f29e` 重核我 review：one-shot marker 仅在阳性 probe 后设置、用后续 429 更新 `last_status_at` 防重新信任、真实 cooldown 到期清 marker；回归测试覆盖保留首 retry/池保持空/下个窗口恢复。**无 action 项，留实现不变** → 我的 review 本就是确认性质，无需回评。

### #97307 Linux desktop entry（kasimali59）→ ✅ 回评接受
我提的相对 `sys.executable` 处理。head `fd7ccd3f` 实证：`_interpreter_path()` 对相对路径走 `.resolve()` 兜底（测试钉死），绝对 venv 路径保留 venv 身份（`sys.prefix != sys.base_prefix`）；附带 `_rebuild_desktop_after_update` 在 build 已新时也重注册 desktop entry（自愈陈旧 wrapper）。回评：[#issuecomment-5460075384](https://github.com/NousResearch/hermes-agent/pull/97307#issuecomment-5460075384)

### #97207 neuralmind catalog（dfrostar）→ ✅ 回评接受
我指出"no network calls"为不可验证的错误主张。head `bccabd67` 实证 manifest 重写：点名 `neuralmind/onnx_embedder.py` 为调用者（非依赖）、明示一次性 HTTPS GET 拉 SHA256-pinned MiniLM 模型、文档化 `NEURALMIND_ONNX_MODEL_DIR` 预置、把断言范围缩到 server 而非 machine、并明说"CI 不验证此项"。诚实精确。回评：[#issuecomment-5460076063](https://github.com/NousResearch/hermes-agent/pull/97207#issuecomment-5460076063)

## 其余 105 条

- **mention 其余 6 条**:#96921 helix4u 截图、#74424/#92122/#93993/#93006 无实体 body 更新、#94321 semirkabir ping teknium1(Photon 批量)、#97307 重叠、#97207 重叠、#96414 重叠 → 信息性
- **跨仓库 1 条**:killop/anything_about_game GameFrameX 仓库迁移订阅
- **其余 ~98 条**:作者自更新/无实体/已关收尾/helix4u perf 桌面系列自更，订阅噪音

## 处置

- 110/110 标 Done，失败 0，收件箱归零；无需逐条回复（2 条 @me 已回评闭环）。

## 待跟进（不变）

- 批量累计 436 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第十八批 · 2026-08-29 续战（97520-97632）→ 50 条并行

**口径：** 上次打到 #97395，本批新开 **97520-97632**（最新 PR #97636），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **50**，3 路子代理并行（17/17/16，按编号序，单条 sleep 8）。

**结果：** **50/50 全部 posted**（skipped 2 大 diff：97525 139KB、97528 1.2MB）。

**明细：**
- 1/3 97520-97559：17 发（97520 holographic 实体提取、97537 背景 topic 源、97558 multiplexer satellite 等）— 注意 97537 的 `gateway/slash_commands.py` 在 diff 中呈二进制（行尾重写），已提示确认是整文件 churn 而非意外
- 2/3 97566-97598：17 发（97576 Gemini 后端、97578 source-scope 路由、97582 OpenCode TTL 等）— 97582 的 regex 源码形状测试被指出违反"测试不读源码"反模式；97589 冗余 no-op for 循环
- 3/3 97599-97632：16 发（97610 buzz 遥测、97615 reaction busy ack、97632 context length 热重载保留 等）

**处置：** 全部 `> AI code review — automated review for reference; please use your judgment.` 头，非阻塞分层，已落盘 diff 与评语。

## 待跟进（更新）

- 批量累计 **486 条** 已发（575 + 125 + 50），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第十九批 · 2026-08-29 (26 条)→ 已清零

**账号:** Enough1122 · **处理:** 26/26 标 Done · **处理后未读:** 0
构成: comment 24 + mention 2 · 定向 @: 0

## 明细

- **mention 2 条:** #92122 autumn8-builds（无评论实体，body 更新）；#93396 saforem2（已关，petdex Kitty 图 CLI 自述，含 after_render 帧同步细节）→ 信息性
- **其余 24 条:** 作者自更新/无实体/已关收尾（含 leighton-tidwell 三连、Doud-FR 三连、TurgutKural 三连），订阅噪音

## 处置

- 26/26 标 Done，失败 0，收件箱归零；无需逐条回复

## 待跟进（不变）

- 批量累计 486 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十批 · 2026-08-29 续战（97634-97689）→ 16 条并行

**口径：** 上次打到 #97632，本批新开 **97634-97689**（最新 PR #97689），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **16**，2 路子代理并行（8/8，按编号序，单条 sleep 8）。

**结果：** **16/16 全部 posted**（97641 anthropic 标量 whitespace 消毒、97649 desktop /background 回源、97663 TUI Windows ConPTY inline、97673 模型路由确认门、97675 MCP 写工具重连安全 等）。跳过 0（另 16 个 >97632 的候选已被他人评/已关/draft/超限）。

**处置：** 全部 `> AI code review — automated review for reference; please use your judgment.` 头，非阻塞分层，已落盘 diff 与评语。子代理另核对本地代码库事实（97673 的 shell word 语义、97675 的 readOnlyHint/熔断、97677 的 SSRF client）。

## 待跟进（更新）

- 批量累计 **502 条** 已发（575 + 125 + 50 + 16），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十一批 · 2026-08-29 (26 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 26/26 标 Done（+1 迟到 25358104848）· **处理后未读:** 0
构成: comment 20 + mention 6 · 定向 @: 0

## 明细

- **mention 6 条:** 全部无评论实体（PR body 更新）：dokterdok ×5（#93223/93224/93007 等）+ #93993 → 信息性
- **第三方 7 条（非定向）:**
  - kvnloo 在我近期 review 的 3 个 PR 上补充审查：#97587（tombstone 清除顺序与中途异常导致身份复活）、#97585（skills-guard 动态 key 豁免漏洞）、#97580（0 字节 state.db 并发启动竞态）——值得留意，说明我 review 的 PR 有人跟进
  - Gabrielvon 评 #87613（banner/废弃 env 警告）、jimmyjonezz 提 #92187 per-session random_seed、kshitijk4poor 两个 Pattern-D 验证（#92253/#89792）→ 均社区自洽
- **其余 13 条:** 作者自更新/已关/已合收尾（含 #96777 teams 已 merged），订阅噪音

## 处置

- 27/27 标 Done，失败 0，收件箱归零；无需逐条回复

## 待跟进（不变）

- 批量累计 502 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十二批 · 2026-08-29 (49 条)→ 已清零

**账号:** Enough1122 · **处理:** 49/49 标 Done · **处理后未读:** 0
构成: comment 44 + mention 5 · 定向 @: 0

## 明细

- **重要跟进：我 review 过的 2 个 PR 已被 salvage 合并，署名保留**
  - **#97582** `fix(cache): OpenCode Go 1h TTL` — kshitijk4poor 经 #97708 rebase-merge 落 main（commit `d51d66e8`，署名保留），salvage 时把我提的 regex 源码形状测试收成了行为断言。呼应我 97582 review 的反模式提示 ✅
  - **#97618** `fix(caching): prompt cache 空白块` — 经 P0 批量 #97704 salvage 落 main，署名保留
- **mention 5 条:** #92316 kshitijk4poor（watchdog 冲突按我映射解析，loop_watchdog_probe 与 startup_watchdog 双保留）、#86272 vollegrewar 已关自述、#93224/#93223/#93007 无实体 → 信息性
- **第三方 5 条（非定向）:** andrexibiza 在 #87530 澄清拓扑归并、fred0m 给 #89294 补 reasoning delta 守卫建议、ahliweb recheck #92336、kshitijk4poor 上述 2 条 → 社区自洽

## 处置

- 49/49 标 Done，失败 0，收件箱归零；无需逐条回复

## 待跟进（不变）

- 批量累计 502 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十三批 · 2026-08-29 (59 条 + 迟到 4 条)→ 已清零

**账号:** Enough1122 · **处理:** 59/59 标 Done（+迟到 4 条）· **处理后未读:** 0
构成: comment 59 · 定向 @: 0

## 明细

- **第三方 10 条（非定向）：**
  - lucywildea 在 #89129 引 #97907 的 OpenRouter preset 自定义名输入
  - KeyArgo 在 #95181 佐证 #97910（kanban_request_review 无 reviewer 缺陷，与我 review 同向）
  - foras910521-lab ×3：#69005 Feishu WS 凭据 URL 日志、#83954 auto_prune 提示、#92934 update_receipt 保护模块
  - YannZhou 在 #94051 第二环境（Ubuntu KDE）复现确认 venv Exec
  - lpbaril 在 #91289 补 compact 案例矩阵、alt-glitch ×2（#54285/#92419 AI triage 注记）、monerostar 在 #97536 原生 Win11 验证
- **其余 49 条:** 作者自更新/无实体/已关/已合收尾（含 huklaa 桌面已 merged），订阅噪音
- **迟到 4 条:** 我 review 过的 #97660/#97667 body 更新 + leighton-tidwell 订阅 → 信息性

## 处置

- 63/63 标 Done，失败 0，收件箱归零；无需逐条回复

## 待跟进（不变）

- 批量累计 502 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十四批 · 2026-08-29 续战（97697-97933）→ 84 条并行

**口径：** 上次打到 #97688，本批新开 **97697-97933**（最新 PR #97933），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **85**（skip 1 大 diff：97735 74KB），5 路子代理并行（各 17，按编号序，单条 sleep 8）。

**结果：** **84 posted / 1 skipped**（97933 已有 alt-glitch AI triage 评论）。

**关键发现（需作者关注）：**
- **#97798** `fix(update): 技能同步失败原因` — `seed_profile_skills` 返回契约变更漏掉一个新建 profile 调用点 → 失败会被误报 "0 skills synced" ⚠
- **#97775/#97799** 同作者同函数同 hunk → 合并冲突风险（已在 #97799 标注）
- **#97834/#97840** 重叠（同修 #97791 同文件）、**#97837/#97839** 重叠（同修 OpenRouter 路由后缀）→ 均提示择一合并
- **#97842** `_clean_stale_site_packages_physical_copies` 按通用顶层名 rmtree site-packages → 误删第三方同名包风险；`ensure_editable_finder_health` 疑似死代码
- **#97766** 续跑无绝对上限（仅 no-progress 触发）→ 病态 provider 可烧尽整个 max_iterations 预算
- **#97736** docstring 声称 kill-switch 全层禁用，实际只接 pre-agent auth 一处，且未识别配置 fail-open
- **#97925** 同级未修复路径 `approval_callback` 同样读写 `_approval_deadline` 但无 None/≤0 处理 → 会立即超时拒批

## 待跟进（更新）

- 批量累计 **586 条** 已发（575 + 125 + 50 + 16 + 84），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十五批 · 2026-08-30 (50 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 50/50 标 Done（+1 迟到 24678199390）· **处理后未读:** 0
构成: comment 46 + mention 4 · 定向 @: 1

## 🎯 定向 @Enough1122（1 条）→ 实证核验后回评

### #95447 `fix(slack): per-turn native stream keying`（SilverNine, head `cd2ee18bf`）
回应我对 #95447 的 3 点 review。作者已 rebase 到现 main 并推送修正：**点 1 same-thread 残留**由 `draft_id` 单调顺序收窄（`>= draft_id` 跳过，仅封更老段，docstring 诚实说明剩余 same-thread 先发仍可被封的残留，指向 gateway 需稳定 per-turn id 的远期合约）；**点 2 abandoned reaper**新增 `_STREAM_ABANDON_SECONDS=1800` + `_reap_abandoned_streams()` 且在读 slot 前执行（回归测试 sabotage-checked，错序会挂 `Expected chat_appendStream to not have been awaited`）；**点 3 嵌套前缀**文档化为启发式局限，指向 `send()` 缺 turn 身份的根因。**均实证落在当前 head**，回评已发：[#issuecomment-5463668762](https://github.com/NousResearch/hermes-agent/pull/95447#issuecomment-5463668762)

## 其余 49 条

- **mention 4 条:** #92316 kshitijk4poor（watchdog 冲突双保留）、#86272 vollegrewar 已关自述、#93223/93224/93007 无实体 → 信息性
- **salvage 合并 2 条:** #96939 TokenPlan、#96381 4-PR 簇胜出，经 rebase-merge 署名保留
- **其余 ~43 条:** 作者自更新/无实体/已关/已合收尾（含 #97707 neuralmind、#96777 已 merged），订阅噪音
- **迟到 1 条:** #24678199390 codex azure reasoning replay ids → 信息性

## 处置

- 51/51 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 586 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十六批 · 2026-08-30 (174 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 174/174 标 Done（+1 迟到 25109226181）· **处理后未读:** 0
构成: comment 164 + mention 10 · 定向 @: 3

## 🎯 定向 @Enough1122（3 条）→ 实证核验后 3 条回评

### #93730 `fix(gateway): stream API reasoning deltas`（fjh990809, head `f10a4b849b`）
我提的 6 点观测（Responses `reasoning_item` 引用共享、空 delta 过滤、`_extract_reasoning_text` 部分流+最终增强的 dedupe、`_thinking` 合成工具的 breaking change、per-step content-parts 丢失 等）。作者在新 head **全部闭环**：live 推理 delta 权威且 finished payload 仅 fallback（回归用例钉死 augmented 最终载荷）、`features.reasoning_streaming` 能力探测与三通道文档化、空推理 delta 在四条面（Chat Completions/Responses/Runs/Session SSE）一致过滤。回评接受：[#issuecomment-5467414339](https://github.com/NousResearch/hermes-agent/pull/93730#issuecomment-5467414339)

### #97317 `feat(simplex): edited inbound as correction`（DavidMetcalfe, head `b300eda6e9`）
我把 `newChatItems` 路径误标为 edit。作者正误：仅 `chatItemUpdated` 分支设 `metadata={"is_edit": True}`（adapter.py:676-677, 以 `is_edit` 入参门控），普通 inbound 仅得 `message_id`。实测 gateway 的 supersede 逻辑以 `is_edit + message_id` 为键，普通消息不受影响。回评更正致谢：[#issuecomment-5467415016](https://github.com/NousResearch/hermes-agent/pull/97317#issuecomment-5467415016)

### #94243 `fix(usage): DeepSeek pricing`（Parker-Fawcett, head `a80882b2e5`）
我把定价刷新与 hindsight 后台线程修打包评议。作者澄清：本 PR 为 **定价-only**，hindsight 修复在 #93028；off-peak floor（`deepseek-pricing-2026-08-offpeak`）有意保留以永不夸大账单，峰值 2× 的 UI caveat 可后续经 `CostResult` 补；debug-log vs warning 亦沿用我此前对多路复用关闭时 debug 级别的指导。回评接受：[#issuecomment-5467415623](https://github.com/NousResearch/hermes-agent/pull/94243#issuecomment-5467415623)

## 其余 171 条

- **mention 其余 7 条:** #18188 lancecheney rebase 7-commit、#72638 Diaspar4u head `8346b58` 验证、#94102/#93208 无实体、#96914 SayHell0W0rld 请求 review（小自洽 PR）、#92211 skbotoc1-web 共享预算验证 等 → 信息性
- **第三方 25 条（非定向）:** egilewski 在 #96886/#96911 判 mergeable（loulanyue state 零字节、kl0i 横幅）、foras910521-lab 验证等 → 社区自洽
- **其余 ~139 条:** 作者自更新/无实体/已关/已合收尾，订阅噪音
- **迟到 1 条:** #25109226181 acp memory commit on session/close → 信息性

## 处置

- 175/175 标 Done，失败 0，收件箱归零；3 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 586 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十七批 · 2026-08-30 续战（97934-98427）→ 114 条并行

**口径：** 上次打到 #97931（前批续战尾），本批新开 **97934-98427**（最新 PR #98427），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **115**（skip 1 大 diff：97947 83KB → 已过滤），5 路子代理并行（23+23+23+23+22，按编号序，单条 sleep 8）。

**结果：** **114 posted / 1 skipped**（98418 live 阶段新增 liyangbing 评论，SOP 跳过）。

**关键发现（抽样）：**
- **#98031** per-task model 需加 profile 名路径穿越校验（`Path / profile_name`）
- **#97998** ⚠ `seed_profile_skills` 契约变更漏掉新建 profile 调用点 → “0 skills synced” 误报（与前批同型）
- **#98018** `make_targz` 原子化、`#98024` marker 先清、`#98046` openai-ads 8 文件新技能 等均非阻塞

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`，POST 201。

## 待跟进（更新）

- 批量累计 **700 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十八批 · 2026-08-30 (34 条)→ 已清零

**账号:** Enough1122 · **处理:** 34/34 标 Done（+2 回评）· **处理后未读:** 0
构成: comment 31 + mention 3 · 定向 @: 2

## 🎯 定向 @Enough1122（2 条）→ 实证核验后回评

### #96168 `feat(skills): grimdall-guard skill`（grimdalltech, head `993143bc46`）
回应我 3 点 skill-authoring checklist：author 已改为 human-first（`Aniket (@grimdalltech, Grimdall Tech)`，标准 4）、新增 `tests/skills/test_grimdall_guard_skill.py`（discoverability contract：frontmatter/描述≤60/period/category/security/命令与配置路径），`related_skills` 已去掉。**均实证落在当前 head**，回评接受：[#issuecomment-5468464073](https://github.com/NousResearch/hermes-agent/pull/96168#issuecomment-5468464073)

### #98398 `fix(scheduler): log cron.max_parallel_jobs`（Halldrix, head `61ff3475e2`）
我提的 INFO volume（每 tick 一条）。作者确认 **有意为之**：按 #98338 可观测性诉求，仅“有 due jobs 的 batch”才发一条 INFO，idle tick 无日志（网关 `verbose=False` 也需可见）。回评接受：[#issuecomment-5468464798](https://github.com/NousResearch/hermes-agent/pull/98398#issuecomment-5468464798)

## 其余 32 条

- **mention 1 条:** #93007 dokterdok 无实体 body 更新
- **第三方 3 条（非定向）:** wormi4ok 在 #89996 补 profile export `No such device` 报错、dokterdok 在 #96162 复现 Bot Mode refactor 遗漏、liyangbing 在 #98141 验证 `force_interactive_oauth` 边界 → 社区自洽
- **其余 28 条:** 作者自更新/无实体/已关/已合收尾，订阅噪音

## 处置

- 34/34 标 Done，失败 0，收件箱归零；2 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 700 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第二十九批 · 2026-08-30 续战（98430-98538）→ 48 条并行

**口径：** 上次打到 #98427（前批续战尾，本批新开 **98430-98538**，最新 PR #98538），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **48**，3 路子代理并行（16/16/16，按编号序，单条 sleep 8）。

**结果：** **48/48 全部 posted**（98430 dashboard-auth、98435 lmstudio、98476 semantic BGE、98538 absorbed_into 等）。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`，POST 201。

## 待跟进（更新）

- 批量累计 **748 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十批 · 2026-08-30 (10 条)→ 已清零

**账号:** Enough1122 · **处理:** 10/10 标 Done · **处理后未读:** 0
构成: comment 10 · 定向 @: 0

## 明细

- **第三方 1 条（非定向）:** daerias 在 #97768 `fix(backup): bound incomplete snapshot retention` 上复审我曾 review 过的 PR（肯定“按需保留可恢复源”的方向，补细节）→ 社区跟进
- **其余 9 条:** 作者自更新/无实体/已关收尾（含 #97768、#97707 等），订阅噪音

## 处置

- 10/10 标 Done，失败 0，收件箱归零；无需逐条回复

## 待跟进（不变）

- 批量累计 748 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十一批 · 2026-08-30 续战（98541-98575）→ 11 条并行

**口径：** 上次打到 #98538（前批续战尾，本批新开 **98541-98575**，最新 PR #98575），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **11**，2 路子代理并行（6/5，按编号序，单条 sleep 8）。

**结果：** **11/11 全部 posted**（98541 plugin context、98553 croniter IANA、98555 TTFB hook、98572 MoA excluded_providers 等）。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`，POST 201。

## 待跟进（更新）

- 批量累计 **759 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十二批 · 2026-08-31 (117 条)→ 已清零

**账号:** Enough1122 · **处理:** 117/117 标 Done（+2 回评）· **处理后未读:** 0
构成: comment 113 + mention 4 · 定向 @: 2

## 🎯 定向 @Enough1122（2 条）→ 实证核验后回评

### #98411 `test: cover webhook CLI error paths and HMAC test command`（DavidMetcalfe, head `c5c1ca99f3`）
我在覆盖率补齐中提 `_REAL_IS_WEBHOOK_ENABLED` 捕获的脆弱性。作者澄清：捕获在**模块导入时**（fixture 之前），`pytest` fixture 按 test 执行，顺序不影响，且 `test_webhook_cli.py:20-22` 已有解释性注释。回评接受：[#issuecomment-5472543655](https://github.com/NousResearch/hermes-agent/pull/98411#issuecomment-5472543655)

### #98430 `feat(dashboard-auth): add truncated User-Agent device id to REFRESH_FAILURE`（Halldrix, head `292af0a111`）
我提 header 大小写与截断（字节 vs 字符）。作者确认：Starlette `Headers` 大小写不敏感；cap 是审计字段字符长度而非 wire 字节限。回评接受：[#issuecomment-5472544585](https://github.com/NousResearch/hermes-agent/pull/98430#issuecomment-5472544585)

## 其余 115 条

- **mention 2 条:** #94102/#92122 无实体 body 更新
- **第三方 6 条（非定向）:** DesarrolloProsis 在 #94391 补 Scheduled Task 证据、liuhao1024 在 #92625 补 Qwen3.5 2B/4B echo 样本、Sravanjangam 在 #97217 注明 #98837 为 superset、vinz3434 在 #94084 对齐 launchd 去重、mgonto 在 #86015 场测 Zoho MCP refresh_token、teknium1 在 #98125 提示 #98628 已合并使半边 patch moot → 社区自洽
- **其余 109 条:** 作者自更新/无实体/已关/已合收尾，订阅噪音

## 处置

- 117/117 标 Done，失败 0，收件箱归零；2 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 759 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十三批 · 2026-08-31 续战（98576-98986）→ 161 条并行（+1 跳过）

**口径：** 上次打到 #98575（前批续战尾，本批新开 **98576-98986**，最新 PR #98986），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **162**，6 路子代理并行（27*6，按编号序，单条 sleep 8），中途服务重启，幂等去重。

**结果：** **161 posted / 1 skipped**（98986 已有 alt-glitch 评论 `Duplicate of #98967`，SOP 跳过；其余 22 条重启前已发，续跑复核跳过，合计 161 新发 landed）。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`，POST 201；98986 本地 md 仍生成但未投递。

## 待跟进（更新）

- 批量累计 **920 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十四批 · 2026-08-31 (146 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 146/146 标 Done（+1 迟到 25077406413 补清 +2 回评）· **处理后未读:** 0
构成: comment 138 + mention 7 + subscribed 1 · 定向 @: 2

## 🎯 定向 @Enough1122（2 条）→ 实证核验后回评

### #94096 `fix(matrix): MAS OAuth2 refresh for matrix.org`（Sahilvishnaliya, head `9fa494d3`）
我当初提 nit 3（`_MAX_REFRESH_ATTEMPTS=8` 限连续失败）。vlify 32h 现网复现：当前实现为 **lifetime** 累计（`_refresh_access_token:1472` 每次调用 `+1`，`_apply_refresh_response` 成功不归零，docstring 写 “total tries”），MAS 4h 过期下 32h 耗尽预算，`giving up … after 8 attempts` 在发请求前触发，手动 POST 同 refresh_token 仍 200 证明链有效。**均落在当前 head**，回评支持其一键修复：在 `_apply_refresh_response` 成功路径 `if not new_access: return False` 后 `self._refresh_attempts = 0`，并补 “成功→后续过期→再刷新” 用例：[#issuecomment-5478282629](https://github.com/NousResearch/hermes-agent/pull/94096#issuecomment-5478282629)

### #97317 `feat(simplex): treat edited inbound as correction`（DavidMetcalfe, head `b300eda6e9`）
前次回评后作者澄清 `is_edit` 仅 `chatItemUpdated` 分支打标、无关消息不受 gateway supersede 影响，并说明三点非阻塞均按设计。回评接受：[#issuecomment-5478284601](https://github.com/NousResearch/hermes-agent/pull/97317#issuecomment-5478284601)

## 其余 144 条

- **mention 3 条:** #92122 无实体、#94096 vlify 同上、#97317 同上（已计入 @）
- **mention 2 条新增:** #94503 Wenfengcheng（delegate 子进程 401 误判为 completed）、#72014 Kyzcreig（修复 `self._client is None` 语义回退）→ 信息性
- **第三方 16 条（非定向）:** #98657 kuehnberger 补 #98649 后半、#96333 chriskosys 双 `continue` 独立复现、#98154 meviusisback Arch 验证 venv Exec、#89581 84dnnvbdvp-debug 探 live-session probe 合约、#90600 TomassonJW 去重 #99318、#83516 teknium1 指 Tavily 已移除（#99199）、#89201 klokie 已开 lsshawn/hermes-agent#1、#97536 alt-glitch 指 #95122 重复、#92270 rongyu945 实测 `search_projection` WAL、#91215 teknium1 指 #98982 已升 spectrum-ts 12.7、#96414 raffieeey 现网 Codex `additional_rate_limits` 100% 误判、#65982 luccapinto Claude Team 冷启动 bug、#97007/#97090 oga35767-eng 标记、#88450 xmhuangzhijun-hue 并档 #98001 → 社区自洽
- **其余 ~128 条:** 作者自更新/无实体/已关/已合收尾，订阅噪音（含 killop/anything_about_game 1 条非 hermes）
- **迟到 1 条:** #25077406413 slack Socket Mode rebuild → 补清

## 处置

- 147/147 标 Done（含迟到），失败 0，收件箱归零；2 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 920 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十五批 · 2026-08-31 续战（98989-99384）→ 151 条并行

**口径：** 上次打到 #98985（前批续战尾，本批新开 **98989-99384**，最新 PR #99384），open + ≤8 文件 + 无评论 + 无 review + 非 draft，diff <60KB。候选 **157**（skip 6 大 diff：99002 88KB/99005 152KB/99025 141KB/99034 89KB/99085 66KB/99345 81KB），6 路子代理并行（26/26/26/26/26/21，按编号序，单条 sleep 8），重启期并发双发 11 条（99228 等）已 DELETE 去重。

**结果：** **151/151 全部 posted**（17+26+26+26+26+21；其中 9 条首批并发抢发跳过计入，99135 等双发已清理）。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`，POST 201；重复 11 条已删至单评。

## 待跟进（更新）

- 批量累计 **1071 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十六批 · 2026-08-31 (41 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 41/41 标 Done（+1 迟到 24992959504 补清 +3 回评）· **处理后未读:** 0
构成: comment 37 + mention 4 · 定向 @: 2

## 🎯 定向 @Enough1122（2 条）→ 实证核验后回评

### #97090 `fix(discord): preserve native thread rename contract`（LuisMunozVillarreal, head `864e5c91`）
我提 relay 分支无测试、connector 默认值。作者澄清：relay 路径已有 `test_sibling_threads_in_one_channel_each_rename_to_own_thread` / `test_title_rename_waits_for_feedback_that_arrives_late` 覆盖 `prefer_connector_created=True` + `parent_chat_id` 直达 `rename_thread` 且落盘为 `only_if_connector_created`，`only_if_current_name=None` 与 connector 默认一致，docstring 已载明优先级。回评接受：[#issuecomment-5479254285](https://github.com/NousResearch/hermes-agent/pull/97090#issuecomment-5479254285)

### #97198 `fix(browser): merge Hermes node dir into PATH in _build_browser_env`（Synxneuos, head `9acd423c`）
我提测试未断言 node dir、冗余手动 merge 残留。作者已在 9acd423 强化 `test_browser_env_path.py` 断言 PATH 前缀/去重/幂等，并清理 `tools/browser_tool.py` 冗余手动合并，逻辑收口至 `_build_browser_env()`。回评接受：[#issuecomment-5479257070](https://github.com/NousResearch/hermes-agent/pull/97198#issuecomment-5479257070)

**附带：** #94096 `fix(matrix): MAS refresh` 作者已推 7aabd795 将 `_apply_refresh_response` 成功路径 `self._refresh_attempts = 0`（consecutive 语义修正），已补评：[#issuecomment-5479259609](https://github.com/NousResearch/hermes-agent/pull/94096#issuecomment-5479259609)

## 其余 39 条

- **mention 1 条:** #84962 david-igou fork 周更
- **第三方 2 条（非定向）:** teknium1 在 #96211 指 #99376 已合（含 #97199 DELETE 扩展）、oga35767-eng 在 #99313 标记 `fix/gateway-total-ceiling-lease-release` → 社区自洽
- **其余 36 条:** 作者自更新/无实体/已关/已合收尾，订阅噪音
- **迟到 1 条:** #24992959504 `feat(tools): compose deferred tools` → 补清

## 处置

- 42/42 标 Done（含迟到），失败 0，收件箱归零；2 条 @me +1 附带已回评闭环

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十七批 · 2026-08-31 (76 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 76/76 标 Done（+1 迟到 25376782398 补清）· **处理后未读:** 0
构成: comment 73 + mention 3 · 定向 @: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 3 条:** #83846 ArcGG33 issue（ZIP fallback 删桌面 App 不重建）、#96886 Agi-Asi（关闭，SQLite NULL SystemError 归 salvage 线）、#99496 teknium1 CI bot OSV 警告 → 信息性
- **第三方 13 条（非定向，teknium1 salvage/triage 扫为主）:** #95106 simonvanlaak 催合、#99265 P1 compression-wedge 现网验证 endorse、#99236 三竞修复比选 salvage #97253、#98020 指 #99502 类修复、#92489 署名保留 cherry-pick 至 #99496、#99496 CI OSV、#94595 判“方向对但不合现状保留改”、#97063 现网验证 premise 成立、#97835 alt-glitch 归档 #98018 superset、#98691 P1 fd-leak 现网 A/B、#97580 kshitijk4poor cherry-pick 合入 #98017、#90234 Liuzikaii 拆分协调、#93452 teamster22 Honcho 现场报告 → 社区自洽
- **其余 ~60 条:** 作者自更新/无实体/已关/已合收尾（salch-cred 14 个 import 测试 PR 关闭、anhtahaylove 系列 chore 等），订阅噪音
- **迟到 1 条:** #25376782398 compression timeout PR → 补清

## 处置

- 77/77 标 Done（含迟到），失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十八批 · 2026-09-01 (241 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 241/241 标 Done（+1 迟到 25302147384 补清 +2 回评）· **处理后未读:** 0
构成: comment 214 + mention 27 · 定向 @: 12（实质跟进 2 + 感谢类 10）

## 🎯 定向 @Enough1122（12 条）→ 实证核验后回评（2 条实质，10 条感谢）

### #83463 `feat(gateway): announce a deliberate /model or /reasoning switch`（Kyzcreig, head `56e7fcd9`）→ 已回评
我提 point 1 hardcoded `"medium"` 提供方默认假设。作者反思后采纳：`_resolved_effort_label` 在 `resolve_reasoning_config` 返回 None 时改为显式 **unknown**，任一侧为 unknown 即抑制 announce（无公告优于错误公告），并预留 per-provider default resolver hook。回评接受：[#issuecomment-5488427934](https://github.com/NousResearch/hermes-agent/pull/83463#issuecomment-5488427934)

### #84210 `fix(telegram): retry transient media downloads`（Kyzcreig, head `9b00755b`）→ 已回评
我提 point 1 adapter 调用 `gateway.run._is_transient_network_error` 私有 helper 的耦合。作者采纳：classifier 提升至共享可导入位置，run.py 与 adapter 共同消费，用真实 telegram 异常类型测试（改类名会 fail loudly 而非静默停 retry）；点3 trailing raise 标 defensive，点2 circuit breaker 暂缓（有界、仅失败路径）。回评接受：[#issuecomment-5488429147](https://github.com/NousResearch/hermes-agent/pull/84210#issuecomment-5488429147)

**感谢类 10 条**（无需回评）: Sravanjangam ×4（98839 checkpoint atomic / 98898 单源 cap / 98900 dead-branch / 98913 key_cmd provenance）、Synxneuos ×2（97226 worktree anchor / 97258 mcp ping 分类 + 97198 前述已闭环）、DavidMetcalfe ×2（99009 delenv 引用已核 / 99008 58 missed lines 系 `__main__` demo 有意跳过 + 99001 纯增量 55c7aaa）、MrTheSoulz（96852 plugin 词汇已 8e2e516 收口）

## 其余 229 条

- **mention 无实体 10 条:** 84236/92440/87264/91234/72638/92122/84962 等 → 信息性
- **第三方 ~20 条（非定向，teknium1/kうら salvage/triage 为主）:** #92316 startup-liveness salvage、#97307 alt-glitch 归档重复 #99755、#83989 rahulbhuva tmpfs 附带、#87490 P1 阈值-floor 现网 bug 确认 + salvage、#84495 getUpdates 池、#96911/#65084/#92448 chef-merged 署名保留、#98121 维护者拍板不采纳、#98455/#98876 supersede → 社区自洽
- **其余 ~190 条:** 作者自更新/无实体/已关/已合收尾（andrexibiza 大量 refactor 切片保留、桌面/cli/state 大量合并线），订阅噪音
- **迟到 1 条:** #25302147384 `fix(hermes_time): log silent config-read failures` → 补清

## 处置

- 242/242 标 Done（含迟到），失败 0，收件箱归零；2 条 @me 实质跟进已回评闭环

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第三十九批 · 2026-09-01 (4 条)→ 已清零

**账号:** Enough1122 · **处理:** 4/4 标 Done · **处理后未读:** 0
构成: comment 4 + mention 0 · 定向 @: 0

## 明细

- **@me: 0 条**（无需回评）
- **#99264** `fix(import): keep restored scripts executable`（fangliquanflq）— 作者回覆已核实 `umask=None→0o600` fallback + `&0o111` 仅合执行位，非 Unix 无贡献，现有目标绕过；与我 LGTM 的 NB 点一致，无需改码 → 信息性
- **#94500** `fix(agent): keep marker-merged rows addressable`（liuhao1024）— zengzheqing 现网复现两形态（plain `user;user` 无 marker、纯 marker 对）本 PR 无法触及，作者 7c89d199 已补 `display_kind` 双 marker 有意 scope + `prev.pop()` 活引用不变式注释，双方案均认同需更深层 resolution 层解法 → 非定向技术讨论，信息性
- **#98096** `feat(tts): openai_compatible streaming`（narigondelsiglo）— 作者自跟进 68c02ff/c9515b33ab/ac9c69b3d6：`available()` 门控镜像 `stream()` 的 `OPENAI_COMPATIBLE_TTS_BASE_URL` 环境变量 + 非流式 mp3 provider，33/33 绿 → 信息性
- **#95992** `fix(desktop): navigate to branched session route`（mashenchina-max）— hutao562 通报已以 59fe527 cherry-pick 至 #98025（tail-dropping 重做），`tsc --noEmit` 绿，着陆顺序无关 → 社区自洽

## 处置

- 4/4 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第四十批 · 2026-09-01 (42 条)→ 已清零

**账号:** Enough1122 · **处理:** 42/42 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 37 + mention 4 + author 1 · 定向 @: 1

## 🎯 定向 @Enough1122（1 条）→ 实证核验后回评

### #84210 `fix(telegram): retry transient media downloads`（Kyzcreig, head `b3d7af9`）→ 已回评
前次我提 point 1 私有 helper `gateway.run._is_transient_network_error` 的 call-time import 耦合，作者按方案落地 `b3d7af9`：classifier 提升至 `gateway/platforms/helpers.py: is_transient_network_error`（公共 helper，12+ adapter 已复用，无环 import-light），`gateway.run` 保留 thin delegating re-export 并以 contract test 锁死不二次膨胀，adapter 改为 module-scope import 使重命名在 import 时 loud 失败而非在 `except Exception` 中静默降级。细节到位：PTB 22.x `BadRequest ⊂ NetworkError` 子类陷阱改名匹配为正确判据，`telegram.error` 真实继承图 + `httpx` 直抛，AST 巡检的 `test_transient_network_error_import_contract.py` 7 用例对三档 mutation 6/2/1 失败并在恢复后 7 pass；549（telegram 族）+123（helpers 消费者）+ ruff clean。回评接受：[#issuecomment-5491052486](https://github.com/NousResearch/hermes-agent/pull/84210#issuecomment-5491052486)

## 其余 41 条

- **跨仓 1 条:** farion1231/cc-switch author 事件 → 非本仓，信息性
- **mention 无实体 3 条:** 90744/72637/92122 → 信息性
- **第三方 2 条（非定向）:** #96492 xiaomukaka88 GBK 复现、#96260 girishmithran SSH 单引号目录树 → 社区自洽
- **其余 35 条:** 作者自更新/无实体/已关收尾（oferlaor slack 族、0xble gateway 族、desktop/kanban 等），订阅噪音

## 处置

- 42/42 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第四十一批 · 2026-09-01 (16 条)→ 已清零

**账号:** Enough1122 · **处理:** 16/16 标 Done · **处理后未读:** 0
构成: comment 16 + mention 0 · 定向 @: 0

## 明细

- **@me: 0 条**（无需回评）
- **第三方 3 条（非定向）:** #94697 kudapara P1 bump（Bot Mode 长转驻留承诺）、#87629 kshitijk4poor salvage via #100142（positional-prune 重做后二提交已 cherry-pick 署名保留）、#83294 KeyArgo #100147 复现确认（`dashboard_auth` 缺 `access_type=offline`）→ 社区自洽
- **其余 13 条:** 作者自更新/已关收尾（Navlem security gate×2、gateway/memory、cli/skills 等），订阅噪音

## 处置

- 16/16 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第四十二批 · 2026-09-01 (35 条)→ 已清零

**账号:** Enough1122 · **处理:** 35/35 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 31 + mention 4 · 定向 @: 1

## 🎯 定向 @Enough1122（1 条）→ 实证核验后回评

### #99287 `feat(providers): recognise llmman as a local runner alias`（ericcurtin, head `f730eb51`）→ 已回评
我前次 LGTM（`llmman`→`custom` 单别名，无模型覆写，非阻塞）。作者问是否 blocking/可否触发 build。回评澄清非阻塞、build 由 maintainer 触发：[#issuecomment-5494044570](https://github.com/NousResearch/hermes-agent/pull/99287#issuecomment-5494044570)

## 其余 34 条

- **mention 无实体 1 条:** #92122 → 信息性
- **mention 有实体 2 条:** #18188 lancecheney `18a76be1→a2584f27` 7 提交重基绿、`#97307` kasimali59 已关 → 信息性
- **第三方 4 条（非定向）:** #84954 caya8205-2 multiplex 日志隔离现网复现、#96040 dai428 Zhipu `glm-5.3` 现网验证、#97214 gerdosi macOS context breakdown 复现、#98106 AlejandroAkbal detached turns 场景补充 → 社区自洽
- **其余 27 条:** 作者自更新/已关收尾（salch-cred preview 绑定、gateway/telegram、desktop 等），订阅噪音

## 处置

- 35/35 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第四十三批 · 2026-09-01 (21 条)→ 已清零

**账号:** Enough1122 · **处理:** 21/21 标 Done · **处理后未读:** 0
构成: comment 20 + mention 1 · 定向 @: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条:** #84415 xiaoyaner0201 已关（Codex Images endpoints）→ 信息性
- **第三方 2 条（非定向）:** #93117 open-Ide2 macOS preview 子帧 `did-fail-load` 独立复现、#90885 kik369 Windows 11 `HERMES_DELEGATED_CHILD_CONTEXT=1` 现网验证 → 社区自洽
- **其余 18 条:** 作者自更新/已关收尾（kanban、gateway、desktop、cli 等），订阅噪音

## 处置

- 21/21 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1071 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）


# 第四十四批 · 2026-09-01 (8 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 9/9 标 Done · **处理后未读:** 0
构成: comment 7 + mention 2 · 定向 @Enough1122: 2 条（均实证回评）

## 定向 @Enough1122 明细（2 条，均为复审请求）

| PR | 作者 | 请求 | head SHA（实证核验） | 处置 |
|----|------|------|---------------------|------|
| #97222 feat(agent): post-execution tool result validation | thewulf7 | `@Enough1122 review again please` | `0976fead3fa60f43f7651585a2873ecb26be8680` | 已复审回评 · Verdict **LGTM** |
| #97224 feat(agent): checkpoint strategy and streaming heuristics | thewulf7 | `@Enough1122 review again please` | `4efccf922e15d413746f503fd966a0f5de1a736b` | 已复审回评 · Verdict **Request changes** |

两条此前（08-31）均已评过，因 `comments>0` 未进批量候选池；作者主动请求复审，按 inbox SOP 实证核验 head SHA 后基于当前 diff 重评。

**#97222 复审要点** — 上轮两个功能性质疑均已解除：`middleware_trace` 确为外层作用域局部变量（`tool_executor.py:1224` 循环变量、`:1403` 重绑定），无 NameError；异常日志已由 debug 升为 warning。剩余为卫生问题：`ToolResultValidationError`(:64) 与 `get_result_preview`(:165) 在 head 中各仅出现 1 次即定义处，为死代码；`TestWiringContract` 测试的是自建镜像而非真实 wiring；未排除 `blocked`/`dispatched`（base `:1447` 已有现成守卫）。

**#97224 复审要点（Request changes）** — 上轮"完全未接线"的结构性问题已部分解决（checkpoint 半已接入 `_execute`，`should_stream_tool` 不再按工具名硬编码）。但新发现两处**相对既有逻辑的行为回归**：
1. 工作目录解析与既有 pre-execution checkpoint 冲突：既有 `_ensure_file_checkpoint`(`tool_executor.py:85-101`) 走 `_resolve_path_for_task → get_working_dir_for_path`，且 `:93-96` 注释明确警告"session cwd 可能与 Hermes 进程 cwd 不同（Docker 尤其）"；新代码 `function_args.get("workdir") or os.getcwd()` 对 `write_file`/`patch`（参数是 `path` 而非 `workdir`）必然回落到进程 cwd——Docker 下会把 checkpoint 写到错误的项目根。
2. 移除 `terminal` 的破坏性命令闸门：既有 `:1084-1095` 仅在 `_is_destructive_command(command)` 为真时 checkpoint，新策略把 `terminal` 无条件列入 `_DESTRUCTIVE_TOOLS`，`ls`/`git status`/`cat` 等只读命令每次都会触发快照。
另：`agent/streaming_results.py` 仍完全未接线；`CheckpointStrategy.SMART` 在唯一调用点硬编码，另 3 个枚举值与 `CheckpointManager` 生产环境不可达；失败被 `logger.debug` 吞掉；新引入 worker 线程并发 `ensure_checkpoint`。

## 其余 7 条

- **mention 无实体 0 条**
- **第三方 6 条（非定向，作者自述/回复）:** #92096 systemINTERNET 已关（Russian locale）、#93815 cxxCoolStar 已关（Bedrock redacted reasoning）、#98555 overtoneblue 已关（TTFB hook）、#92981 xxbwx888（CLI prompts 路由）、#95926 fangliquanflq（unresumable sessions，作者逐条回应无需改码）、#85514 SHAREN（Russian Kanban，已推 `d0194184d`）→ 社区自洽/已收尾
- **迟到 1 条:** "pm: unified package manager"（comment，非定向）→ 已补标 Done

## 处置

- 9/9 标 Done（8 首批 + 1 迟到），失败 0，收件箱归零
- 2 条 @me 均已实证核验 head SHA 后回评闭环

## 待跟进

- 批量累计 1071 条已发（本次 2 条为 inbox 复审，不计入批量池）
- #97224 等作者回应两处 checkpoint 回归

# 第四十五批 · 2026-09-01 续战（99385-100453）→ 313 条并行

**口径：** 上次打到 #99384（前批续战尾），本批新开 **99385-100453**（最新 PR #100453 `ci: re-enable the Desktop E2E lane`），open + ≤8 文件 + 无评论 + 无 review + 非 draft + 无内联评审评论 + diff <60KB。search `is:pr is:open comments:0` 按 created 分片拉取 **476** 条，活检筛后候选 **317**（skip 159：comments 82 / changed_files 56 / draft 11 / reviews 10），diff 60KB 再筛 4（99828/99921/99922/100214 超限），应用户要求补筛"已有人审核"（pulls/comments 内联 + reviews + issues/comments 全零核验）→ 最终 **313**。

**执行：** 6 路子代理并行（26/26/26/26/26/26… 按编号序，单条 sleep 8，统一 `post_review.py` 幂等去重），中途重启续跑（块文件被外部改动，以 API 实证重扫重分块）。

**结果：** **313/313 全部 posted**，双发 **0** 条需清理，0 失败。API 全量核验 `POSTED(>=1)=313, DUP(>1)=0`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 1071→1384`、`max=100448`。

**本轮要点（Request changes 摘录）：** #99617 `_on_unit_timeout` 中 `_fleet_snapshot is None` 潜在 TypeError、#100115 孤立 `)` 疑致构建破坏、#100363 hermes-docs MCP skill snippet 列索引错误 + pyproject 构建后端疑无效、#99771 latest.json 可能卡 pending、#99817 `mkdir_under_hermes_home` 在吞异常 try/except 内导入需核实。

## 待跟进（更新）

- 批量累计 **1384 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

# 第四十六批 · 2026-09-02 续战（100454-100544）→ 32 条并行

**口径：** 上次打到 #100448（第 45 批尾），本批新开 **100454-100544**（最新 PR #100544），open + ≤8 文件 + 无评论 + 无 review + 无内联评审评论 + 非 draft + diff <60KB。search 拉取 **49** → 活检筛 32（skip 17：comments 11 / changed_files 6）→ diff 全过（32/32，无超限）。

**执行：** 2 路子代理并行（16/16，按编号序，单条 sleep 8，`post_review.py` 幂等去重）。

**结果：** **32/32 全部 posted**，双发 0，失败 0。API 全量核验 `posted=32, dup=0, missing=[]`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 1384→1416`、`max=100543`。

**本轮 Request changes 摘录：** #100467（mount-time pet reset 回归）、#100482（`profiles/` 审计分类过宽）；#100542 已实证核验 `detail` 控制流安全（无需改）。

## 待跟进（更新）

- 批量累计 **1416 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

# 第四十七批 · 2026-09-02 (95 条)→ 已清零

**账号:** Enough1122 · **处理:** 95/95 标 Done · **处理后未读:** 0
构成: comment 90 + mention 5 · 定向 @Enough1122: 1 条（实证回评）

## 定向 @Enough1122（1 条）→ 实证核验后回评

### #100421 `fix(aux): shape-aware preview in _validate_llm_response error`（Halldrix, head `c9c1a54df7`）
我上轮提"object 分支 `items = ", ".join(f"{k}={v!r}"...)` 只限字段数、不限每个值 repr 大小"（auxiliary_client.py:9347-9348）。作者在 `c9c1a54df7` 修复：新增 `_format_response_preview()`（`agent/auxiliary_client.py:9299-9344`），每项 `f"{k}={v!r}"[:budget]` + 6 字段上限，dict/str/None 分支均预算封顶，并补 `TestFormatResponsePreview` 回归测试。已实证核验 diff 后回评接受（附非阻塞提示：repr 中间截断可能留下未闭合引号片段，结构化日志场景建议按 token 边界截断）：[#issuecomment-5502803870](https://github.com/NousResearch/hermes-agent/pull/100421#issuecomment-5502803870)
（首条评语因 shell 反引号转义污染已 DELETE 重发，无残留）

## 其余 94 条

- **mention 4 条（非定向）:** #90206 riique（native audio routing 描述）、#92122 autumn8-builds（.desktop Exec，无最新评论实体）、#94411 MrTheSoulz（已 rebase 至 main `82e6c46b94` 解冲突）、#100242 salch-cred（#90835 Telegram 日志幻象 triage 确认）→ 信息性
- **第三方/作者自述 ~90 条:** liuhao1024 系列 20+（tools/cli/memory/photon/cron 修复）、Kyzcreig 3 条、tachyon-r 系列、benjaminbrumbaugh、chelsealong 等，多为作者自更新/新 PR 描述 → 订阅噪音

## 处置

- 95/95 标 Done（+迟到 0），失败 0，收件箱归零
- 1 条 @me 实证核验 head SHA 后回评闭环

## 待跟进（不变）

- 批量累计 1416 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

# 第四十八批 · 2026-09-02 续战（100545-100833）→ 87 条并行

**口径：** 上次打到 #100543（第 46 批尾），本批新开 **100545-100833**（最新 PR #100833 `fix: improve _validate_llm_response error preview`），open + ≤8 文件 + 无评论 + 无 review + 非 draft + 无内联评审评论（pulls/comments 零核验）+ diff <60KB。search `is:pr is:open comments:0` 按 created 分片拉取 **169** → 活检筛 **87**（skip 82：comments 60 / changed_files 15 / draft 4 / reviews 3）→ diff 60KB 全过（87/87 无超限）。

**执行：** 4 路子代理并行（26/26/26/9，按编号序，单条 sleep 8，统一 `post_review.py` 幂等去重）。

**结果：** **87/87 全部 posted**，双发 **0** 条需清理，0 失败。API 全量核验 `POSTED(>=1)=87, DUP(>1)=0`。另对上一轮遗留的 block01 区域（100546-100604 声称已发但未入账）连同本批做全窗口实测：区间 100544-100833 共 **119** 条已发并入账（= 本批 87 + 遗留 32），0 双发。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 1416→1535`、`max=100833`、`frontier=100833`。

**本轮 Request changes 摘录：** #100659（签名钩子功能无效——密钥每次新建未持久化、guardclaw 未声明依赖、测试断言可空过）、#100695（`status.py` 中 `field(default_factory=set)` 误作普通函数默认参数的真 bug）、#100629（微任务竞态使 4401 分支实际不可达）、#100650（仓库根目录混入德文临时测试文件）、#100699/#100745（URL 精确匹配、并发写入边界）。

## 待跟进（更新）

- 批量累计 **1535 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

## 第四十八批补充 · 新窗口 100834-100846（9/2 晚）→ 2 条

第 48 批收口时新窗口已入窗（最新 PR #100846 `fix: prevent disabled_toolsets from stripping kanban worker`）：区间 13 条活检，仅 **2 条**合格（#100839、#100843），其余 11 条剔除（已 review 2 / 404 不存在 4 / draft 1 / changed_files 超限 3 / 已有评论 1）。1 路子代理发布，**2/2 posted，0 双发**；API 核验 `{100839:1, 100843:1}`。state：posted 1535→**1537**、max/frontier=**100846**。要点：#100839（wire bytes 落盘时纯空白 content 仍会被存为 sidecar，建议补测试）、#100843（restore 先于 handoff 驱动判断，可能注入重复 user 行）。

## 待跟进（更新）

- 批量累计 **1537 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

# 第四十九批 · 2026-09-02 (14 条)→ 已清零

**账号:** Enough1122 · **处理:** 14/14 标 Done · **处理后未读:** 0
构成: comment 13 + mention 1 · 定向 @Enough1122: 3 条线程（实证核验后回评）

## 定向回评（3 条）→ 实证核验后回评

### #100421 `fix(aux): shape-aware preview in _validate_llm_response error`（Halldrix, mention）
作者认同我上轮非阻塞提示（per-item slice 会在 `repr(v)` 中间截断、>budget 字段可能留下未闭合引号），确认无 over-budget 测试覆盖，标为 known follow-up debt 并给出 minimal fix（token 边界截断 + 显式省略号 + 回归测试）。我回评确认闭环，并补一条 budget<=1 时 `s[:budget-1]` 为空、输出坍缩为 `"…"` 的边界建议（非阻塞）：[#issuecomment-5503711824](https://github.com/NousResearch/hermes-agent/pull/100421#issuecomment-5503711824)

### #100554 `fix(approval): honor unattended policy for API sessions`（fangliquanflq）
作者按我上轮 review 点跟进：补 default-deny 路径无 pending 断言的显式断言、解释 synthetic `is_gateway=True` 测试不可达（`_is_gateway_approval_context()` 对 `_UNATTENDED_APPROVAL_PLATFORMS` 恒 False）、保留 `HERMES_EXEC_ASK` 为进程级提示（guard 只做本地决策）。**已核实最新 head**：`and not is_gateway` 确已删除（我落盘的旧 diff 滞后），守卫为 `if _is_unattended_platform_approval_context(): is_ask = False`。回评接受 + 非阻塞建议：互斥契约（gateway 集合 ∩ unattended 集合 = ∅）目前只靠注释维持，建议加不变式测试固化：[#issuecomment-5503713274](https://github.com/NousResearch/hermes-agent/pull/100554#issuecomment-5503713274)

### #100543 `fix(gateway): hide provisional tool-failure status when interim is off`（sake303）
作者报告 issue reporter **live Discord 实测 not passed**（head `1e9167097`）：`display.interim_assistant_messages: false` 时仍可见 `tool_call: "mcpmercurylistTransactions"` + 韩语 `최신 조회 실패`（"latest lookup failed"）。定位：`_PROVISIONAL_TOOL_STATUS_RE` 仅匹配英文 token（`lookup|query|tool...failed`），韩语不命中 → `_looks_like_provisional_tool_status()` 返回 False → warn 门不触发。回评建议：①源头结构化标记而非文本正则（可抗本地化/截断/文案变更）；②保留 matcher 则补 i18n 覆盖 + 确认该状态确以 `event_type=="warn"` 到达（若是 info/tool 则英文也漏）；另提示 tool_call 行属另一类事件，不在本过滤路径：[#issuecomment-5503714587](https://github.com/NousResearch/hermes-agent/pull/100543#issuecomment-5503714587)

## 其余 11 条

- **作者感谢/确认我们的 review:** #100754 liuhao1024（确认 whitespace 只是 re-close 表达式 fallout）、#100774 cez0060405（确认 1500ms 重验窗口是有意为之）→ 信息性
- **第三方对话:** #99940 DavidMetcalfe 回复 @alt-glitch、#96260 SZWzz 回复 @girishmithran → 噪音
- **作者自述/确认:** #99919 salch-cred（承认 #100445 持久化方案更优）、#100567 mrkillbob（报告不可复现）、#94611 huklaa（旧 PR 描述）→ 噪音
- **实体评论即我们自己的 AI review**（latest_comment 解析为空、无作者新回复）: #100253、#95281、#100546、#83606 → 信息性

## 处置

- 14/14 标 Done（+迟到 0），失败 0，收件箱归零
- 3 条定向线程实证核验 head/最新评论后回评闭环（#100421 接受闭环 / #100554 接受 + 互斥契约建议 / #100543 指出 localization 缺口，作者已知待修）
- 新增工具 `post_followup.py`：第二条评论直发通道（内容级判重，避免误重发）

## 待跟进（不变）

- 批量累计 1537 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十批 · 2026-09-02 续战（100847-100853）→ 4 条

**口径：** 上次打到 #100846（第 48 批补充尾），本批新开 **100847-100853**（最新 PR #100853 `fix(gateway): allow receipt readback after restart`），open + ≤8 文件 + 无评论 + 无 review + 无内联评审评论 + 非 draft + diff <60KB。search `is:pr is:open comments:0` 按 created 分片拉取 **5** → 活检筛 **4**（skip 1：changed_files/comments 等）→ diff 全过（4/4，无超限）。

**执行：** 单路直发（4 按编号序，单条 sleep 8，`post15.py` 幂等去重 + 实时 has_ai 核验）。

**结果：** **4/4 全部 posted**，双发 0，失败 0。API 核验 `posted=4, dup=0`：
- #100850 `fix(streaming): fall back on HTTP 405` → https://github.com/NousResearch/hermes-agent/pull/100850#issuecomment-5503764023
- #100851 `fix(agent): prevent null auxiliary model from becoming "None" string` → https://github.com/NousResearch/hermes-agent/pull/100851#issuecomment-5503765682
- #100852 `feat(mattermost): separate DM and channel reply modes` → https://github.com/NousResearch/hermes-agent/pull/100852#issuecomment-5503767464
- #100853 `fix(gateway): allow receipt readback after restart` → https://github.com/NousResearch/hermes-agent/pull/100853#issuecomment-5503769054

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 1537→1541`、`max/frontier=100853`。本轮均为 LGTM，无 Request changes。

## 待跟进（更新）

- 批量累计 **1541 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十一批 · 2026-09-02 (112 条)→ 已清零

**账号:** Enough1122 · **处理:** 112/112 标 Done（+2 回评）· **处理后未读:** 0
构成: comment 107 + mention 5 · 定向 @Enough1122: 2 条（实证核验后回评）

## 定向 @Enough1122（2 条）→ 实证核验后回评

### #97882 `docs(mcp): document MEDIA: attachments`（Dhi13man, head `8483e8bd`）→ 已回评
纯文档 `MEDIA:`/`[[as_document]]`/`[[audio_as_voice]]`，我 08-29 已 LGTM（路径解析在 gateway host、code fence 排除等）并提 traceability 非阻塞。作者 @ 提请再看，无新增改动，回评确认仍 LGTM：[#issuecomment-5507390919](https://github.com/NousResearch/hermes-agent/pull/97882#issuecomment-5507390919)

### #100764 `feat: native audio and voice routing`（riique, head `20ae14f0`）→ 已回评
我提 4 点：(1) 音频全失败时图像被吞、(2) 转码失败仍发 ogg 致 400、(3) 远端 http(s) 静默丢弃、(4) 25 MiB 未计 base64 膨胀。作者在 `20ae14f0` 全量修复：混排无 media 时回落 image-only 且 marker 仅在 `input_audio` 存活时写入、转码失败跳过而非重发原格式、Gemini-native 明确仅 `data:` URI 且不打 URL 日志、25 MiB 在编码后重检并覆盖转码输出；新增回归，27 专项 + 143 扩展绿。回评接受：[#issuecomment-5507392710](https://github.com/NousResearch/hermes-agent/pull/100764#issuecomment-5507392710)

## 其余 110 条

- **mention 无实体 1 条:** #92122 autumn8-builds → 信息性
- **mention 已关 1 条:** #97258 Synxneuos `ping` 静默丢包（#97245）已关 → 信息性
- **issue mention 1 条:** #82874 imapotato123 `shutdown_mcp_servers` 阻塞剩余缺口说明（#99675 已修主腿）→ 信息性
- **第三方 20+ 条（非定向，teknium1 归档/合并为主）:** #87980 #99622 #84006 #86622 #100234 等 salvage/merges 署名保留、#84626/#84665/#85352 #100967 护栏全量说明、#100485 ocuclaw hybrid 扫描等 → 社区自洽
- **其余 ~87 条:** 作者自更新/已关收尾（liuhao1024×6、Doud-FR、686f6c61×5、desktop/cron/agent 等），订阅噪音

## 处置

- 112/112 标 Done，失败 0，收件箱归零；2 条 @me 实证核验 head SHA 后回评闭环

## 待跟进（不变）

- 批量累计 1541 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十二批 · 2026-09-02 (18 条)→ 已清零

**账号:** Enough1122 · **处理:** 18/18 标 Done · **处理后未读:** 0
构成: comment 17 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条:** #86183 strzhao 已关（FTS5 引擎变更自修复，已关）→ 信息性
- **第三方 1 条（非定向）:** #100253 monerostar Native Win11 `OpenProcess/GetExitCodeProcess` 实测评论 → 社区自洽
- **其余 16 条:** 作者自更新/已关收尾（chrisyoung2005×4、Doud-FR×2、liuhao1024×2 等），订阅噪音

## 处置

- 18/18 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1541 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十三批 · 2026-09-02 续战（100854-101262）→ 117 条并行

**口径：** 上次打到 #100853（第 50 批尾），本批新开 **100854-101262**（最新 PR #101261 `fix(desktop): Bot Mode tabs caption` / 实发尾 #101262），open + ≤8 文件 + 无评论 + 无 review + 无内联评审评论 + 非 draft + diff <60KB。search `is:pr is:open comments:0` 按 created 分片拉取 **962 去重→202 >frontier** → 活检筛 **117**（skip 85：comments/review/inline/changed_files/draft）→ diff 60KB 全过（117/117，无超限）。

**执行：** 6 路子代理并行（20/20/20/20/20/17，按编号序，单条 sleep 8，统一 `post_review.py` 幂等去重，首轮 120s 超时后二轮续传）：
- chunk1 20/20（100861-100974）
- chunk2 20/20（100975-101031，首轮 9+二轮 11）
- chunk3 20/20（101045-101103，首轮 8 已发+二轮 12 新发，去重 8）
- chunk4 20/20（101108-101168，首轮 9+二轮 11）
- chunk5 20/20（101170-101221，首轮 9+二轮 11，去重 9）
- chunk6 17/17（101222-101262，首轮 9+二轮 8）

**结果：** **117/117 全部 posted**，双发 **0** 条需清理，0 失败。API 全量核验 `ai==1` 117 条（抽检 100861/100865/101258/101259/101262 均为 1，missing 0/dups 0）。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 1541→1658`、`max/frontier=101262`。本轮均为 LGTM 细节（示例：100865 BrowserUse daemon 回收、100877 cost-footer、101066 HTTPS MCP OAuth、101220 matrix E2EE 等）。

## 待跟进（更新）

- 批量累计 **1658 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十四批 · 2026-09-02 (102 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 102/102 标 Done（+1 迟到 25416695903 补清 +1 回评）· **处理后未读:** 0
构成: comment 97 + mention 5 · 定向 @Enough1122: 1 条（实证核验后回评）

## 定向 @Enough1122（1 条）→ 实证核验后回评

### #100589 `fix(retry): exponential backoff for upstream-capacity 429s`（elcoosp, head `64e527a9`）→ 已回评
我提 off-by-one（`retry_count` 0-based 传入 1-based `upstream_capacity_backoff`，致 `-1` 索引取 300s）及宽泛 429 检测致 provider failover 被误禁。作者在 `64e527a9` 修复：调用处改 `retry_count+1` + `max(0, …)` 防负索引，`is_upstream_capacity_error` 收敛至精确短语 `"temporarily at capacity upstream"`，`_is_upstream_capacity` 同 except 块内赋值/使用无 UnboundLocalError。回评接受：[#issuecomment-5510579242](https://github.com/NousResearch/hermes-agent/pull/100589#issuecomment-5510579242)

## 其余 101 条

- **mention 无实体 1 条:** #92122 autumn8-builds → 信息性
- **mention/issue 2 条:** #100764 riique 已回评前置、#96897 AronAxe browser 已关 → 信息性
- **第三方 10+ 条（非定向，teknium1 归档/合并为主）:** #101081 kshitijk4poor 合并署名保留、#99538 MaciejNaerion SSH 目录遍历待修复提醒、#94598 teknium1 410 签名等 → 社区自洽
- **其余 ~88 条:** 作者自更新/已关收尾（liuhao1024×6、helix4u×4、fangliquanflq、desktop/cron 等），订阅噪音
- **迟到 1 条:** #25416695903 `fix(desktop): merge primary chat across zones` → 补清

## 处置

- 103/103 标 Done（含迟到），失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 1658 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十五批 · 2026-09-03 (270 条 + 迟到 9 条)→ 已清零

**账号:** Enough1122 · **处理:** 270/270 标 Done（+9 迟到补清，两轮核验归零）· **处理后未读:** 0
构成: comment 244 + mention 26 · 定向 @Enough1122: 10

## 定向 @Enough1122（10 条）→ 实证核验后回评（均已 POST，不重发）

| PR | 作者/状态 | 要点 | 回评 |
|----|-----------|------|------|
| #95243 `fix(plugin-guard)` | tuancookiez-hub · closed | `(?!=>)` 回溯缺陷未修，作者建议关闭重提 | [5519244978](https://github.com/NousResearch/hermes-agent/pull/95243#issuecomment-5519244978) |
| #89649 | LeonardoLGDS · closed | 两提交已 via #93615 落地，terminal guard hoist 后续 | [5519246193](https://github.com/NousResearch/hermes-agent/pull/89649#issuecomment-5519246193) |
| #89265 | LeonardoLGDS · open | `_normalize_preset` 空串/None 回退语义澄清 | [5519247428](https://github.com/NousResearch/hermes-agent/pull/89265#issuecomment-5519247428) |
| #89138 | LeonardoLGDS · open | retitle + 子 agent 上下文覆盖已补 | [5519248606](https://github.com/NousResearch/hermes-agent/pull/89138#issuecomment-5519248606) |
| #92164 | kshitijk4poor · merged `8b681f70ea` | UTF-8 seam 点成立，原样合并 | [5519249837](https://github.com/NousResearch/hermes-agent/pull/92164#issuecomment-5519249837) |
| #92228 | kshitijk4poor · merged `4a17802280` | 缓存键 + 陈旧单测已清 | [5519251076](https://github.com/NousResearch/hermes-agent/pull/92228#issuecomment-5519251076) |
| #93342 `feat(mcp-oauth)` | Elliot-Construct · open | 纯 ping，无新 diff；旧三点留待更新 | [5519252321](https://github.com/NousResearch/hermes-agent/pull/93342#issuecomment-5519252321) |
| #93344 `fix(mcp-oauth)` | Elliot-Construct · open | 纯 ping，无新 diff；旧三点留待更新 | [5519253591](https://github.com/NousResearch/hermes-agent/pull/93344#issuecomment-5519253591) |
| #100765 `fix(desktop): Wayland clipboard` | MrTheSoulz · open `c00d51dae` | rebase 解冲 + 参数类型 + wl-paste 逐候选兜底，27 测绿 | [5519254780](https://github.com/NousResearch/hermes-agent/pull/100765#issuecomment-5519254780) |
| #100626 `fix(desktop): merge primary chat` | MrTheSoulz · open `1876668bf4` | 全 TileDock 通用 + 空组剪枝 + it.each 回归 11/11 | [5519255931](https://github.com/NousResearch/hermes-agent/pull/100626#issuecomment-5519255931) |

## 其余 260 条

- **mention 无实体 4 条:** 93006/95359/86062/92122 → 信息性
- **mention 有实体:** #87302 kuehnberger 重基 72 测绿、#96936 spiky02plateau `GLM_BASE_URL` 旁路复现、#99287 ericcurtin PTAL、#100583/#100582 kiwipaulrob 重基已修、#84962 djdanielsson +1 → 信息性/社区自洽
- **已关/已合 mention:** #89649/#91157/#95160/#93517/#101599/#101598/#85806（LeonardoLGDS/kshitijk4poor 归档线）→ 信息性
- **第三方 30+ 条（非定向，teknium1/kshitijk4poor 归档/合并为主）:** #92164/#92228/#92413/#92217 等 salvage 署名保留、#84626/#84665/#85352 #100967 护栏说明、#100714 tornado 无 floor 提醒、#99538 SSH 敏感路径后置提醒、#99953 压缩钳制剩余需求、#101053 kmccammon 现网佐证 → 社区自洽
- **其余 ~200 条:** 作者自更新/已关收尾（Christopher-Schulze ~40、multiplex 归档群、desktop/cron/agent 等），订阅噪音
- **迟到 9 条:** tts/a2a/telegram/raft/multiplex 归档 + skill signing + #100765/#100626 mention → 补清

## 处置

- 279/279 标 Done（含 9 迟到；中途两次服务端重启，小批量幂等补删，两轮核验归零），失败 0，收件箱归零；10 条 @me 已回评闭环（POST 201，不重发）

## 待跟进（不变）

- 批量累计 1658 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十六批 · 2026-09-03 (9 条)→ 已清零

**账号:** Enough1122 · **处理:** 9/9 标 Done · **处理后未读:** 0
构成: comment 8 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条:** #93007 dokterdok（bot-mode unread，无最新评论实体）→ 信息性
- **其余 8 条:** 作者自更新/无实体（andrexibiza file-ceiling、ibaldr89 delegation、shali10、jonpol01、x7peeps×2、fangliquanflq、Tracyyy-s），订阅噪音

## 处置

- 9/9 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1658 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十七批 · 2026-09-03 (38 条)→ 已清零

**账号:** Enough1122 · **处理:** 38/38 标 Done · **处理后未读:** 0
构成: comment 36 + mention 2 · 定向 @Enough1122: 1（感谢类，无需回评）

## 明细

- **@me 1 条（感谢类，无需回评）:** #99992 DevEverything01（pre-save sign-in 隔离修复，LGTM 已收；作者认同 NB 点并向 kshitijk4poor 求 salvage）→ 信息性
- **mention 1 条:** #92122 alt-glitch AI triage（launcher cluster 选型说明）→ 信息性
- **第三方 7 条（非定向）:** #101085 kshitijk4poor salvage #101736、#85773 pymq beam_size +1、#100098 JuizSpeaking 现网复现确认、#76931 JIRBOY v0.20.6 复现、#94091 iiai-lab Orca EINVAL 现场证据、#81760 ciphercommand 双机实测、#99992 同上 → 社区自洽
- **其余 29 条:** 作者自更新/已关收尾（desktop/cron/agent/buzz 等），订阅噪音

## 处置

- 38/38 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1658 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十八批 · 2026-09-03 (38 条)→ 已清零

**账号:** Enough1122 · **处理:** 38/38 标 Done · **处理后未读:** 0
构成: comment 37 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条:** #72638 Diaspar4u 自述（Responses verbosity `94aa19aa` 72 验证）→ 信息性
- **第三方 3 条（非定向）:** #56521 zionzangar 捷克语母语审校、#91224 29206394 Ghostty 修饰键独立验证、#100423 nolan-shen systemd 生产确认 → 社区自洽
- **其余 34 条:** 作者自更新/已关收尾（jonpol01×6、eventh0riz0n×4、will-lynas×5、M7MMAD-OMAR×3 等），订阅噪音

## 处置

- 38/38 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1658 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第五十九批 · 2026-09-03 (17 条)→ 已清零

**账号:** Enough1122 · **处理:** 17/17 标 Done · **处理后未读:** 0
构成: comment 16 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条:** #75212 nimitbhardwaj 自述（himalaya v2 三周 silence check-in，CONFLICTING 待重基）→ 信息性
- **第三方 1 条（非定向）:** #91423 teknium1 FYI（#102032 schema v30 subagent 排除说明）→ 社区自洽
- **其余 15 条:** 作者自更新/已关收尾（chrisyoung2005×4、eventh0riz0n×2、fangliquanflq×2 等），订阅噪音

## 处置

- 17/17 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1658 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十批 · 2026-09-04 (50 条)→ 已清零

**账号:** Enough1122 · **处理:** 50/50 标 Done · **处理后未读:** 0
构成: comment 46 + mention 4 · 定向 @Enough1122: **4 条（全部实证回评）**

## 明细

定向 @me 4 条（按“全线程扫描”判定，非仅看 `reason` 字段）：

- **#83513 thatssoheil**（9/3，回应我 8/16 的三点）
  - 1 测试导入重量：作者维持与既有 CLI 行为测试一致的放置 → 认可，交 maintainer
  - 2 粘贴守卫：**撤回我的建议**。实证 `_apply_bracketed_paste_timeout_patch`（cli.py:3554+）：`_in_bracketed_paste` 为真时字节全进 `_paste_buffer`，最终以单个 `BracketedPaste` 事件交付（收到 `ESC[201~` 或 2s 超时冲刷），键绑定永远看不到内层字节；0x1A 能作为普通键进入解析器的唯一路径是 `ESC[200~` 起始标记丢失——正是我的守卫（靠观察起始标记布防）永不触发的场景。且守卫会误吞粘贴完成后不久的真实 Ctrl+Z。净负收益，作者判断正确
  - 3 恢复后重绘：**核实成立**。venv 锁定 prompt_toolkit 3.0.52，`application/run_in_terminal.py` 的 `in_terminal` 上下文 `finally`（L106-117）确为 `renderer.reset()` → `_request_absolute_cursor_position()` → `_redraw()`，与作者引用逐行吻合
- **#85365 PRATHAMESH75**（8/16 漏网，本次补回）：三项转义全部核实通过（`xml.sax.saxutils.escape` + `xml.dom.minidom` 解析断言、`_systemd_env_value_escape` 反斜杠→引号→`%%` 顺序正确、`_bundled_resource_env_pairs()` 单一卡口）。**新增两条非阻塞跟进**：① 区块在渲染时从 `os.environ` 派生，而 `generate_launchd_plist()` 被 `launchd_start()`(5788)/`launchd_install()`(5739)/`refresh_launchd_plist_if_needed()`(5525) 调用，plist 在**每次 start 都会重写**；若重写时环境里没有 wrapper 导出的 `HERMES_BUNDLED_*`（直连 venv python、桌面/GUI 启动、supervised 重启），区块会被静默剥离，#85357 复发 ② 新 helper 可一行套用到仍裸插值的 `HERMES_HOME`/`VIRTUAL_ENV`/`PATH`
- **#100547 michaelknowles**（9/2，回应我 9/2 的 Request changes）：**撤回两条、自我更正一条**
  - 持久化顺序：撤回。`_persist_live_session_system_prompt()` 存 `agent._build_system_prompt(None)`（server.py:5901），而 `agent/system_prompt.py:483` 明确不含 `ephemeral_system_prompt`
  - busy submit：**我原来写的“等当前轮跑完”是错的**。`_handle_busy_submit` 仍调 `_interrupt_busy_session`（server.py:10695-10696），该调用**不受 `extra_system` 门控**，interrupt 模式照旧硬打断；差异只是 redirect-in-place vs interrupt-then-drain。残留建议：RPC 响应从 `{"status": "redirected"}`(10664) 变为 `{"status": "queued"}`(10697)，依赖该字段的客户端会走另一分支，建议在 `prompt.submit` 契约上写明
  - `session.info`：撤回。`_session_info()`（server.py:7709+）只取 `session["personality"]`，从不读 overlay；且 `_emit_settled_session_info()` 在 14247、晚于 14180 的恢复
  - agent swap（走本轮 local `agent` 绑定）/ 锁范围（revision 自增、overlay 写入、marker append 已并入同一个 `history_lock`）→ 接受
  - 校验收紧：核实通过（独立校验、JSON `null` 与非字符串均拒、不再从无效 `system_message` 落到 `instructions`、4004 指明别名）
  - **Verdict 由 Request changes 改为无阻塞**
- **#73861 Skrypt**（8/21 漏网，French locale 八合一帖）：复核我旧评三项于当前 head `31950ba28715` —— 遗留英文 token（`CHANGED`/`item/items`/`node/nodes`/frame）**已清零**；`mcp.testOk` 复数一致**已修**（fr.ts:1304-1305 现按 count 拼 `outil(s)` / `disponible(s)`，含 count===0 取复数）；**弯撇号仍未统一**（fr.ts:484/1472/1474/1484/1517 五处用 `’`，其余为直 `'`）

- 迟到 1 条：#101344（扫描无定向 @me → 信息性）
- 其余 45 条：作者自更新 / 第三方对话 / 自己 review 实体 → 订阅噪音

## 处置

- 4 条定向回评全部走 `post_followup.py` 发布（内容级判重）：83513 / 85365 / 100547 / 73861 → **POSTED 4/4，0 双发 0 失败**
- 全量 `PUT /notifications` 标已读 → 205，**剩余未读 0**

## 方法论沉淀

- **`reason == mention` 不等于需要回评**：#92122 标为 mention，但最新是 bot triage 且我早已表态。判定标准应改为「全线程扫描：晚于我最后一条回复、且正文含 @Enough1122」，而非 `reason` 字段
- 本批据此捞出两条漏网（#85365 挂 19 天、#73861 挂 14 天），说明历史批次按 mention-only 判定存在系统性漏检，后续批次一律用全线程扫描

## 待跟进

- 批量累计 1658 条已发，frontier=**101262**；最新 open PR 已到 **#102401**，新窗口 101263-102401（约 1139 个编号）未扫
- #96080 署名落地（非阻塞）

---

# 第六十批 · 2026-09-03/04 续战（101263-102373）→ 307 条并行

**口径：** 上次打到 #101262（第 53 批尾），本批新开 **101263-102373**（最新 PR #102373 `fix(desktop-update): stop Windows hand-off hanging on gateway pipe chatter`，另注意到 #102401 在途未入本批）。search 按 created 日切片拉取 **949 去重→457 >frontier**，加新窗口 **74**（102242-102373）→ 合计 531；chunk3 先落地 **44**；剩余 487 活检筛 **270 合格**（skip 217：comments 148 / files>8 36 / reviews 18 / draft 12 / closed 3）→ diff 60KB 再筛 4（101474/102037/102078/102171 超限）→ **266 待发**。

**执行：** 6 路子代理并行（45/45/45/45/45/41，按编号序，单条 sleep 8，发前二次活检 + 幂等去重）：
- chunk1 45/45（101268-101469， Doherty 22 篇被 quarantine 误伤中断后恢复补发）
- chunk2 45/45（101471-101815；发现 #101505/#101522 同组 memory 默认值文本冲突，已互注；#101809 空提交如实 no-op）
- chunk3 44（101630-1017xx，首批落地）+ 本批续发（101820-101985 段）
- chunk4（101987-102128）、chunk5（102130-102285，102246 `str/str` 真 bug、102237 `__init__` 内定方法已标出）
- chunk6 38/41（102286-102373；102298 `split(/[?#]/,1)` no-op、102355 标题与 diff 不符、102356 `args[3]`/level 错位、102373 PID 复用竞态已标出）
- 主控收尾 22 复检全跳过（19 已有我方 AI 评论 + 3 第三方评论），0 重复发布

**结果：** **307/310 已 posted**（266 中 263 + chunk3 首批 44），**3 正确跳过**（102354 andrexibiza 人工 review / 102365、102370 alt-glitch triage + 0xble 人工），0 双发。核验链：首轮 API 全量核验 266（posted 244 + missing 22，dup 0 err 0）→ 22 闭环（19 chunk6 URL + 3 第三方）→ 配额恢复后 89 条慢速复核全过（posted 263，missing 恰为上述 3 个正确跳过，dup 0）。收尾阶段 GitHub API 用户级 403 限流（6 并行×8 线程触发滥用防护）已恢复，不影响结论。

**事故：** 某子代理的清理脚本把 campaign/ 下 1619 个 .md 移入 `quarantine_badlines/`（含历史已发评语，头均正常系误伤）。已全部恢复原位（1424 移回 + 129 相同删除 + 66 双版本保留 top 版），各 chunk 幂等续跑不受影响，0 双发。后续禁全目录清理脚本，只允许 chunk 内文件操作。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`（未发的 102354/102365/102370 三篇草稿已删，保持 md=已发不变式）；campaign_state.json 更新 `posted 1658→1965`、`max/frontier=102373`。

## 待跟进（更新）

- 批量累计 **1965 条** 已发，等作者/maintainer 响应；89 条复核已补跑全过，无需再核
- 新窗口 102374-102401（约 27 个编号）未扫
- #96080 署名落地（非阻塞）

---

# 第六十一批 · 2026-09-04 (76 条)→ 已清零

**账号:** Enough1122 · **处理:** 76/76 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 71 + mention 5 · 定向 @Enough1122: 2（1 实质 + 1 感谢）

## 定向 @Enough1122（2 条）

### #102162 `fix(gateway): suppress hygiene turnhold_deferred`（tuancookiez-hub, head `b46a4246`）→ 已回评
我提重复 ~40 行冷却检查块抽 helper + None 路径 debug 日志。作者 amend 落地：`_cooldown_is_active()` 模块级（1 定义 + 2 调用），fail-open 保留，debug 日志在位，Path 1 即时记录加 fence 门，67/67 绿。已实证核验 diff 后回评接受：[#issuecomment-5534388239](https://github.com/NousResearch/hermes-agent/pull/102162#issuecomment-5534388239)

### #96783 `fix(desktop): group member lights Active Now`（tuancookiez-hub）→ 感谢类，无需回评
作者确认无 action items，待 review/merge → 信息性

## 其余 74 条

- **mention 无实体 3 条:** 85744/94411/84869 → 信息性
- **第三方 6 条（非定向）:** #100215 jerrygooch rAF 暂停计时勘误、#100585 Enferlain sealed 追问、#91197/#87499 yuzilongleif-collab 双独立验证、#85893 CSEliot 追问、#102200 leejoonhwanusa Windows 打包复现 → 社区自洽
- **其余 ~65 条:** 作者自更新/已关收尾（benjaminbrumbaugh×5、liuhao1024×9、JPeetz×4、Halldrix×3、fangliquanflq×2 等），订阅噪音

## 处置

- 76/76 标 Done，失败 0，收件箱归零；1 条 @me 实证核验后回评闭环

## 待跟进（不变）

- 批量累计 1965 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十二批 · 2026-09-04 (43 条)→ 已清零

**账号:** Enough1122 · **处理:** 43/43 标 Done · **处理后未读:** 0
构成: comment 43 + mention 0 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评；#102024 最新是我方 AI 评论，无作者新回复）
- **第三方 12 条（非定向，jerrygooch desktop 验证 sweep 为主）:** #102297/#98644/#96722/#101480/#100665（dim/grayscale、compositing、console flash、keep-alive、todo flash 逐个验证通过）、#100317 cozcc 路由变体 + #102628、#92204 bykim0119  clarify 去重说明、#97547 freqyfreqy 时序勘误、#101849 jasonswinney7466 Win10 端到端确认、#99278 nateEc 关重、#102200 leejoonhwanusa 同上 → 社区自洽
- **其余 31 条:** 作者自更新/已关收尾（nateEc×7、ericmaddox×4、686f6c61×2、Halldrix×2、fangliquanflq×2 等），订阅噪音

## 处置

- 43/43 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1965 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十三批 · 2026-09-04 (35 条)→ 已清零

**账号:** Enough1122 · **处理:** 35/35 标 Done · **处理后未读:** 0
构成: comment 32 + mention 3 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评；#97224/#97222 mention 无实体，为我前次复审线程）
- **mention 有实体 1 条:** #94411 MrTheSoulz 自述（`32a3e70ef` 纯 rebase，树与 merge 版一致，typecheck + 17/17 vitest 关门）→ 信息性
- **第三方 1 条（非定向）:** #98505 zkkk9555 已提 #102774 补全 salch-cred `-NoAutoStart`（署名保留）→ 社区自洽
- **其余 33 条:** 作者自更新/无实体（FalconOrtiz×8 desktop 族、nateEc×2、686f6c61×2、Halldrix×2、fangliquanflq×2、ericmaddox×4 等），订阅噪音

## 处置

- 35/35 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 1965 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十四批 · 2026-09-04 续战（102374-102813）→ 135 条并行

**口径：** 上次打到 #102373（第 60 批尾），本批新开 **102374-102814**（最新 PR #102814 `fix(cron): sanitize API keys/tokens`），open + ≤8 文件 + 无评论 + 无 review + 无内联 + 非 draft + diff <60KB。search 按 created 日切片拉取 **517 去重→243 >frontier** → 活检筛 **141**（skip 102：comments 62 / files>8 18 / reviews 16 / draft 6）→ diff 60KB 再筛 5（102506/102522/102637/102648/102650 超限）→ **136 待发**。

**执行：** 4 路子代理并行（34×4，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理脚本）：
- chunk1 34/34（102376-102463；发现 102378 vs 102393 互斥剪枝、102394 vs 102396 同 issue 两写法只能合一，均已互注）
- chunk2 34/34（102464-102559）
- chunk3 34/34（102561-102684）
- chunk4 33/34（102685-102813；102814 有 1 评论正确跳过）

**结果：** **135/136 已 posted**，1 正确跳过（102814），0 双发。主控慢速单线程全量核验 `posted=135, missing=[102814], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 1965→2100`、`max/frontier=102813`（102814 有评论未入）。

## 待跟进（更新）

- 批量累计 **2100 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十五批 · 2026-09-04 (91 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 91/91 标 Done（+1 迟到 25438793844 补清 +3 回评）· **处理后未读:** 0
构成: comment 81 + mention 10 · 定向 @Enough1122: 3

## 定向 @Enough1122（3 条）→ 实证核验后回评

### #102109 `fix(aux): vision fallback chain`（ziuus）→ 已回评
两 nit 闭环：失败项 debug 日志后续 commit 跟进、UI 顺手改认账并承诺分 PR。LGTM 维持：[#issuecomment-5543677002](https://github.com/NousResearch/hermes-agent/pull/102109#issuecomment-5543677002)

### #101833 `fix(agent): cross-turn no-progress guard`（ziuus）→ 已回评
阈值理由接受（跨 turn 突发为目标，小时级误伤待真实 case 再议）+#85352 已加 cross-link。LGTM 维持：[#issuecomment-5543679160](https://github.com/NousResearch/hermes-agent/pull/101833#issuecomment-5543679160)

### #102607 `feat(desktop): reasoning typography tokens`（seb-almeida, head `46a2437c`）→ 已回评
4 点全评估：2 落地（tautology 行删除、docs 重组）+ 2 按我原评估 no-action（`:has()` 开销有界、Tailwind 耦合由编译测试兜底），contract 4/4 + thread 186/186 绿。接受：[#issuecomment-5543681357](https://github.com/NousResearch/hermes-agent/pull/102607#issuecomment-5543681357)

## 其余 88 条

- **mention 无实体 5 条:** 85744/94411/98417/98398/86825（多为我已表态线程）→ 信息性
- **mention 有实体 2 条:** #84409 abhinavmanocha Win11 Job-Object repro、`#100764` riique 已关 → 信息性
- **第三方 10+ 条（非定向）:** #102779 eseppy 关重、#91981 Guitaraholic Docker 边界、#99947 tutan0558 Windows 现网、#102394/#102395 alt-glitch triage、#94180 rudawilczyca-coder 独立验证、#77953 Ramesh-X +1 → 社区自洽
- **其余 ~70 条:** 作者自更新/已关收尾（garadice×4、KeyArgo×4、Halldrix×5、YuYigeng×5、chrisyoung2005×4、fangliquanflq×3 等），订阅噪音
- **迟到 1 条:** #25438793844 lazy installs UV 隔离 → 补清

## 处置

- 92/92 标 Done（含迟到），失败 0，收件箱归零；3 条 @me 实证核验后回评闭环

## 待跟进（不变）

- 批量累计 2100 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十六批 · 2026-09-04 续战（102814-103042）→ 64 条并行

**口径：** 上次打到 #102813（第 64 批尾），本批新开 **102814-103042**（最新 PR #103043 `fix(security): upgrade vulnerable Python dependencies` 未入），open + ≤8 文件 + 无评论 + 无 review + 无内联 + 非 draft + diff <60KB。search 日切片拉取 **260 去重→133 >frontier** → 活检筛 **74**（skip 59：comments 35 / reviews 11 / files>8 11 / draft 2）→ diff 60KB 再筛 1（103043 93KB 超限）→ **73 待发**。

**执行：** 3 路子代理并行（25/25/23，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 25/25（102816-102881）
- chunk2 22/25（102882-102965；102952/102959/102961 发前新增 review 正确跳过）
- chunk3 17/23（102966-103042；103041 初检即有 review + 103007/103021/103023/103036/103038 发布中途新增 review 拦截；发现 103013 vs 103040 同 token 重复 PR 已互注、103021 夹带无关 kill 变更）

**结果：** **64/73 已 posted**，9 正确跳过（他人 review 先到），0 双发。主控全量核验 `posted=64, missing=9（上之）, dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2100→2164`、`max/frontier=103042`。

## 待跟进（更新）

- 批量累计 **2164 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十七批 · 2026-09-05 (15 条)→ 已清零

**账号:** Enough1122 · **处理:** 15/15 标 Done · **处理后未读:** 0
构成: comment 12 + mention 3 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 3 条，均无实体:** #84409/#92122/#93756 → 信息性
- **其余 12 条:** 作者自更新/无实体（soroush5×6 kill-all/cli/gateway 系列、realAbitbol、astraltrekkin、misstyka、ethernet8023、TurgutKural、jakubrojewski），订阅噪音

## 处置

- 15/15 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2164 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第六十八批 · 2026-09-04 续战（103043-103060）→ 7/7（新规则）

**规则变更（用户 2026-09-04）：** 取消文件数/diff 大小限制。新口径：**open + 非 draft + 零评论/零 review/零内联 + 编号>前沿**。已写入 `campaign_state.json:rule`。

**执行：** 上批 7 候选中 2 已发（103052/103060），剩余 5 按新规则补评，直发（sleep 8，发前二次活检）：
- #103043 `fix(security): upgrade vulnerable Python dependencies`（93KB, 3f: cryptography→48.0.1/Pillow→12.3.0/multipart/mcp/starlette + discord voice extra 拆分钉 PyNaCl 1.6.2）→ [5544050737](https://github.com/NousResearch/hermes-agent/pull/103043#issuecomment-5544050737)
- #103045 `feat(web): Last 5 Models strip`（18f: 17 i18n catalog + ModelsPage，纯增量）→ [5544052728](https://github.com/NousResearch/hermes-agent/pull/103045#issuecomment-5544052728)
- #103046 `feat(gateway): mcp_http platform`（12f 新建：bearer 鉴权/回环绑定/入站过滤/审计 + 55s 长轮询）→ [5544054671](https://github.com/NousResearch/hermes-agent/pull/103046#issuecomment-5544054671)
- #103048 `feat(providers): quota-reset auto-resume`（11f 新建 `quota_resume.py` 三源 deadline + 26h 上限 + 372/289 行测试）→ [5544056549](https://github.com/NousResearch/hermes-agent/pull/103048#issuecomment-5544056549)
- #103057 `feat(openai): GPT-6 Astra baseline`（16f：aux 路由 effort + sanitizer-last + 定价/窗口 + 7 测试文件）→ [5544058580](https://github.com/NousResearch/hermes-agent/pull/103057#issuecomment-5544058580)

**结果：** **7/7 posted**（2+5），0 双发。`posted 2164→2171`、`frontier=103060`。

## 待跟进（更新）

- 批量累计 **2171 条** 已发，等作者/maintainer 响应
- 新规则已生效，后续批次不再限大小/文件数
- #96080 署名落地（非阻塞）

---

# 第六十九批 · 2026-09-04 (11 条 + 迟到 3 条)→ 已清零

**账号:** Enough1122 · **处理:** 11/11 标 Done（+3 迟到补清）· **处理后未读:** 0
构成: comment 11 + mention 0 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **第三方 1 条（非定向）:** #103060 alt-glitch triage（指与 #86420 重复，供 maintainer 判定；我评语已发 LGTM，无需动作）→ 信息性
- **其余 10 条:** 作者自更新/无实体（potatosalad、salch-cred×2、keeltrace、benjaminbrumbaugh、TurgutKural、v2v21、Halldrix、BananaLoaf、realAbitbol），订阅噪音
- **迟到 3 条:** compression fallback、serve live token×2 → 补清

## 处置

- 14/14 标 Done（含迟到），失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2171 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十批 · 2026-09-05 (138 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 138/138 标 Done（+1 迟到补清）· **处理后未读:** 0
构成: comment 125 + mention 13 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 13 条:** 92122 alt-glitch triage 修正、86578/87302 kuehnberger 可合/重基、96852/94411/100626 MrTheSoulz 三连 rebase、100583/100582 kiwipaulrob 拆分关并、89142 PRATHAMESH75 salvage、65514/92590/100547/92267 无实体 → 信息性
- **第三方 12 条（非定向）:** #97931 Glucksberg 开 #103337、#99847 Alorse VPS 复现、#103013 GPT-6 macOS/SSH 复现、#101433 bitbite0 `oneOf` 根因、#101976 AkiYamaa 同求、#90888 miggitty 生产确认、#102454 JoaoMarcos44 协作说明、#95105 ramgendeploy Linux 确认、#103086/#103088 alt-glitch 去重 triage、#92088 同上 → 社区自洽
- **其余 ~113 条:** 作者自更新/已关收尾（liuhao1024×10、salch-cred×5、PRATHAMESH75×6、chrisyoung2005×4 等），订阅噪音
- **迟到 1 条:** compression tool-id 补清

## 处置

- 139/139 标 Done（含迟到），失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2171 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十一批 · 2026-09-05 续战（103061-103089）→ 19/19（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。25 候选 → 活检 **19**（6 有评论跳过：103064/103072/103073/103076/103079/103082）→ diff 全收（最大 103KB）。

**执行：** 2 路子代理开局即撞模型限流，主控接手：
- chunk 2/2 的 9 个（103078-103089）子代理已发（ai=1 确认），但限流致 state 未入账 → 本批补入账
- chunk 1/2 的 10 个主控直发（sleep 8，发前二次活检）：103061 or-True 断言转正 / 103065 `logging.disable` 改 console-mute（agent.log 复活）/ 103066 WSL shim 拒收 / 103067 env-source 补种 / 103069 real-profile 浏览器选择 / 103070 Responses 原生压缩归一 / 103071 平台配置落位修复 / 103074 provider timing 能力 / 103075 profile pin 只收窄 / 103077 verifier 40-turn 默认

**结果：** **19/19 posted**（9+10），0 双发（发前复检全零）：
- 103061 [5549040428](https://github.com/NousResearch/hermes-agent/pull/103061#issuecomment-5549040428) · 103065 [5549041443](https://github.com/NousResearch/hermes-agent/pull/103065#issuecomment-5549041443) · 103066 [5549042377](https://github.com/NousResearch/hermes-agent/pull/103066#issuecomment-5549042377) · 103067 [5549043321](https://github.com/NousResearch/hermes-agent/pull/103067#issuecomment-5549043321) · 103069 [5549044337](https://github.com/NousResearch/hermes-agent/pull/103069#issuecomment-5549044337) · 103070 [5549045330](https://github.com/NousResearch/hermes-agent/pull/103070#issuecomment-5549045330) · 103071 [5549046205](https://github.com/NousResearch/hermes-agent/pull/103071#issuecomment-5549046205) · 103074 [5549047193](https://github.com/NousResearch/hermes-agent/pull/103074#issuecomment-5549047193) · 103075 [5549048325](https://github.com/NousResearch/hermes-agent/pull/103075#issuecomment-5549048325) · 103077 [5549049311](https://github.com/NousResearch/hermes-agent/pull/103077#issuecomment-5549049311)

**处置：** 已落盘 `drafts/_campaign/{n}.diff`；campaign_state.json 更新 `posted 2171→2190`、`max/frontier=103089`。

## 待跟进（更新）

- 批量累计 **2190 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十二批 · 2026-09-05 (34 条)→ 已清零

**账号:** Enough1122 · **处理:** 34/34 标 Done · **处理后未读:** 0
构成: comment 32 + mention 2 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 无实体 2 条:** #92122/#85996 → 信息性
- **第三方 8 条（非定向）:** #101372 ackellerman 现网复现确认、#102562/#102993 3x3xX3N0N 双评审、#90121 donald2008 现网复现、#98526/#100249 zengzheqing diff 精读、#101554 AaaCabbage 复现证据、#103057 unsupportedpastels 追问 900k opt-in（指向作者）→ 社区自洽
- **其余 24 条:** 作者自更新/已关收尾（keeltrace×4、MikeGibbsOnyx×2、james47kjv×4、salch-cred×2 等），订阅噪音

## 处置

- 34/34 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2190 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十三批 · 2026-09-05 续战（103090-103441）→ 115 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **464 去重→214 >frontier** → 活检筛 **118**（skip 96：comments 75 / draft 17 / reviews 4）→ diff 全收（含 8 个>60KB，最大 173KB）。

**执行：** 4 路子代理并行（30/30/30/28，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 30/30（103090-103180；103095 173KB 大 PR 完整审）
- chunk2 29/30（103182-103268；103185 发前被他人评论，正确跳过）
- chunk3 29/30（103275-103376；103289 作者 force-push 更新说明，diff 陈旧未发）
- chunk4 27/28（103377-103441；103440 有 1 评论跳过）

**结果：** **115/118 已 posted**，3 正确跳过（103185/103289/103440，均他人评论先到），0 双发。主控慢速单线程全量核验 `posted=115, missing=[103185,103289,103440], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2190→2305`、`max/frontier=103441`。

## 待跟进（更新）

- 批量累计 **2305 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十四批 · 2026-09-05 (64 条)→ 已清零

**账号:** Enough1122 · **处理:** 64/64 标 Done · **处理后未读:** 0
构成: comment 62 + mention 2 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 无实体 2 条:** #92122/#85365 → 信息性
- **第三方 6 条（非定向）:** #93938/#102918 monerostar Win11 双验证、#97547 chenlichao 现网验证、#103424 PRATHAMESH75 autotriage、#101801 YFF05200 cwd 补充、#103057 同上（900k 追问归档）→ 社区自洽
- **其余 56 条:** 作者自更新/已关收尾（liuhao1024×8、tachyon-r×9 等），订阅噪音

## 处置

- 64/64 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2305 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十五批 · 2026-09-05 续战（103442-103578）→ 55 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **187 去重→95 >frontier** → 活检筛 **58**（skip 37：comments 35 / draft 2）→ diff 全收（含 4 个>60KB，最大 290KB）。

**执行：** 3 路子代理并行（20/20/18，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 20/20（103443-103488）
- chunk2 20/20（103489-103536；103516 夹带根目录 scratch 文件、103520 疑似缺 import、103505 hook 归因漏报、103524 key 优先级已标出）
- chunk3 15/18（103537-103578；103537/103580 首检即有 review + 103573 发前新增 2 评论拦截，103573 md 留存未发）

**结果：** **55/58 已 posted**，3 正确跳过（103537/103573/103580），0 双发。主控全量核验 `posted=55, missing=[103537,103573,103580], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2305→2360`、`max/frontier=103578`。

## 待跟进（更新）

- 批量累计 **2360 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十七批 · 2026-09-06 续战（103579-103805）→ 66 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **262 去重→127 >frontier** → 活检筛 **69**（skip 58：comments 43 / draft 9 / reviews 6）→ diff 全收（含 4 个>60KB，最大 330KB）。

**执行：** 3 路子代理并行（23/23/23，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 23/23（103582-103680；发现 103663/103652 同改 `auth_native_refresh` 需统一、103624 VBS 子串与 103582 同类）
- chunk2 20/23（103682-103753；9 已发后续跑，幂等靠线上标记）
- chunk3 20/23（103754-103805；103754 AlexxRussell 新增评论拦截未发、103816/103817 首检有评论跳过）

**结果：** **66/69 已 posted**，3 正确跳过（103754/103816/103817），0 双发。主控全量核验 `posted=66, missing=[103754,103816,103817], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2360→2426`、`max/frontier=103805`。

## 待跟进（更新）

- 批量累计 **2426 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十九批 · 2026-09-06 续战（103806-103867）→ 23 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **280 去重→34 >frontier** → 活检筛 **23**（skip 11：comments 9 / draft 1 / reviews 1）→ diff 全<60KB。

**执行：** 2 路子代理并行（12/11，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 12/12（103830-103844）
- chunk2 11/11（103848-103867；首轮 `@($null).Count` 误报已纠正）

**结果：** **23/23 已 posted**，0 跳过，0 双发。主控全量核验 `posted=23, missing=[], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2426→2449`、`max/frontier=103867`。

## 待跟进（更新）

- 批量累计 **2449 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十一批 · 2026-09-06 续战（103868-104047）→ 69 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **383 去重→117 >frontier** → 活检筛 **71**（skip 46：comments 27 / reviews 11 / draft 8）→ diff 全收（含 7 个>60KB，最大 287KB）。

**执行：** 3 路子代理并行（24/24/23，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 24/24（103872-103952；103934 删文档节待确认、103896 权限隔离 6 消费点已标出）
- chunk2 24/24（103953-104017）
- chunk3 21/23（104020-104047；104048/104049 首检有评论跳过）

**结果：** **69/71 已 posted**，2 正确跳过（104048/104049），0 双发。主控全量核验 `posted=69, missing=[104048,104049], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2449→2518`、`max/frontier=104047`。

## 待跟进（更新）

- 批量累计 **2518 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十三批 · 2026-09-06 续战（104048-104200）→ 53 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **146 去重→91 >frontier** → 活检筛 **54**（skip 37：comments 30 / reviews 5 / draft 2）→ diff 全收（含 1 个 214KB）。

**执行：** 3 路子代理并行（18/18/18，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 18/18（104053-104101；首轮 120s 超时后幂等续跑 9 个）
- chunk2 18/18（104107-104144）
- chunk3 17/18（104146-104200；104166 发前被 roli-lpci maintainer review 抢先，正确跳过，评语留存未发）

**结果：** **53/54 已 posted**，1 正确跳过（104166 第三方 review 先到），0 双发。主控全量核验 `posted=53, missing=[104166], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2518→2571`、`max/frontier=104200`。

## 待跟进（更新）

- 批量累计 **2571 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十四批 · 2026-09-06 (60 条)→ 已清零

**账号:** Enough1122 · **处理:** 60/60 标 Done（含 1 条 ours state_change）· **处理后未读:** 0
构成: comment 59 + state_change 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **ours 1 条:** #81108 state_change（我自己的 PR 状态变更，无评论实体）→ 信息性
- **第三方 14 条（非定向）:** #89996 jonfriesen debian 复现、#95171/#92707 ForaDoPadraoYT Win E2E、#92622 andrexibiza 转交说明、#99305 ChengZiiii vLLM 确认、#97212/#83589 andrexibiza 协调、#100249 zengzheqing #104295、#91823 strzhao salvage 成稿、#96260/#104146/#104189 alt-glitch triage、mrkillbobbot 批量 → 社区自洽
- **其余 45 条:** 作者自更新/已关收尾（Christopher-Schulze×6、mrkillbob×8、kyssta-exe×12 等），订阅噪音

## 处置

- 60/60 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2571 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十五批 · 2026-09-06 (3 条)→ 已清零

**账号:** Enough1122 · **处理:** 3/3 标 Done · **处理后未读:** 0
构成: comment 3（均无最新评论实体，描述更新类）· 定向 @Enough1122: 0

## 处置

- 3/3 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2571 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十二批 · 2026-09-06 (65 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 65/65 标 Done（+1 迟到补清 +1 回评）· **处理后未读:** 0
构成: comment 62 + mention 3 · 定向 @Enough1122: 1

## 定向 @Enough1122（1 条）→ 实证核验后回评

### #104011 `feat(desktop): controls for goals/criteria/loops/Heartbeats`（jerrygooch, head `283fa972`）→ 已回评
我提 dispatch-loss 边角。作者先修 claim 消费后 `_emit` 失败不回绕（`51df1ed4`），再发现首个回滚 guard 与 pause/resume/clear 的 read-check-write 竞态，推 `283fa972` 统一 manager 锁 + 原子 before/after + 确定性 pause-wins 回归 5x + 61 绿。回评接受：[#issuecomment-5558462860](https://github.com/NousResearch/hermes-agent/pull/104011#issuecomment-5558462860)

## 其余 64 条

- **mention 3 条:** #85744 无实体、#98106 BearHuddleston 已关、#104011 同上 → 信息性
- **第三方 20+ 条（非定向，mrkillbobbot 批量为主）:** base-refresh/codex 触发×8、kshitijk4poor 落地 4 条（#102357/#97547/#93869/#102677）、benjaminbrumbaugh 比选、JoaoMarcos44 前向移植、94809 shostako WSL2 数据、93753 rodrigogs 致谢、75824 rodrigogs 复现、93785/93754 ci 修复报告、100567 等 → 社区自洽
- **其余 ~40 条:** 作者自更新/已关收尾（tachyon-r×9、Christopher-Schulze×5、mrkillbob×10 等），订阅噪音
- **迟到 1 条:** deja docs 补清

## 处置

- 66/66 标 Done（含迟到），失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 2518 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十批 · 2026-09-06 (59 条)→ 已清零

**账号:** Enough1122 · **处理:** 59/59 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 52 + mention 7 · 定向 @Enough1122: 1

## 定向 @Enough1122（1 条）→ 实证核验后回评

### #103838 `fix(agent): emit recovered response before stream close`（0xalydev, head `b3764800`）→ 已回评
我提 printer 异常静默 + double-print 两点。作者在 `b3764800` 加 `logger.debug`、论证两分支均在无输出后 + 立即 break 不可能 double-print，5 测绿。回评接受：[#issuecomment-5556899250](https://github.com/NousResearch/hermes-agent/pull/103838#issuecomment-5556899250)

## 其余 58 条

- **mention 7 条:** #86198/#87264/#92440/#91234 Diaspar4u 重基系列、#92122/#74424 无实体、#103838 同上 → 信息性
- **第三方 14 条（非定向）:** mrkillbobbot×6 codex/@codex 触发、#87028 rodrigogs Bedrock 复现、#85818 skylight96 独立验证、#102098  bored-verify、#101924 foma-agent 负例、#103057 convernaticspeter 跟进、#83324/#91224 alt-glitch+despotak triage → 社区自洽
- **其余 ~37 条:** 作者自更新/已关收尾，订阅噪音

## 处置

- 59/59 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 2449 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十八批 · 2026-09-06 (20 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 20/20 标 Done（+1 迟到补清 +4 回评）· **处理后未读:** 0
构成: comment 15 + mention 5 · 定向 @Enough1122: 4（Halldrix 全回复）

## 定向 @Enough1122（4 条）→ 回评（均为设计确认，无代码变更）

- #103674 dashboard-auth breaker：offset-aware 确认 + last-failure 跟进 + 20/h 默认 → [5554409021](https://github.com/NousResearch/hermes-agent/pull/103674#issuecomment-5554409021)
- #103652 refresh 分类限流：最小永久集 + Lock 对等 + 10/min 自愈 → [5554409834](https://github.com/NousResearch/hermes-agent/pull/103652#issuecomment-5554409834)
- #103624 VBS spawn：作用域 pid + fail-open + Quit 0 + 字符串断言 → [5554410658](https://github.com/NousResearch/hermes-agent/pull/103624#issuecomment-5554410658)
- #103685 Codex 重试：显式链边角跟进 + pre-stream 门 → [5554411520](https://github.com/NousResearch/hermes-agent/pull/103685#issuecomment-5554411520)

## 其余 16 条

- **mention 无实体 1 条:** #92122 → 信息性
- **第三方 1 条（非定向）:** #102867 plcunha 移植 #103846 → 社区自洽
- **其余 14 条:** 作者自更新/已关收尾，订阅噪音
- **迟到 1 条:** compression re-arm 补清

## 处置

- 21/21 标 Done（含迟到），失败 0，收件箱归零；4 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 2426 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第七十六批 · 2026-09-06 (117 条)→ 已清零

**账号:** Enough1122 · **处理:** 117/117 标 Done · **处理后未读:** 0
构成: comment 110 + mention 7 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 7 条:** #18188 sfire123 重审无阻塞、#84962 jonpol01 k8s 用例 +1、#92122/#84869/#84236/#85943/#103444 无实体 → 信息性
- **第三方 10 条（非定向）:** #103080 sdjaime VPS 复现、#84183 ForaDoPadraoYT Win11 复现、#65982 CryptoKylan 分支、#101460 Chukwuemeka001 测试跟进、#103373 strzhao 机制验证 + 不变量缺口、#93884/#103350 kshitijk4poor 落地通知、#90800 ktchan3 排水确认 → 社区自洽
- **其余 ~100 条:** 作者自更新/已关收尾（evgyur×8、liuhao1024、kyssta-exe×12、PRATHAMESH75×5 等），订阅噪音

## 处置

- 117/117 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 2360 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十六批 · 2026-09-06 续战（104201-104307）→ 34 条并行（新规则）·注记

> 注：此前数批 edit 锚点撞到重复块，致 76–85 批在文件中乱序（内容无缺失）。本批起固定缀尾；待跟进以本节为准。

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **194 去重→64 >frontier** → 活检筛 **35**（skip 29：comments 25 / reviews 4）→ diff 全收（含 4 个>60KB，最大 230KB）。

**执行：** 2 路子代理并行（18/17，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 18/18（104203-104270）
- chunk2 16/17（104271-104307；104295 发前新增 Sinojen 人类实质讨论，正确跳过，评语留存未发；发现 104278 锁顺序、104290 任意路径读取、104301 世代竞态、104304 CLI 收紧已标出）

**结果：** **34/35 已 posted**，1 正确跳过（104295），0 双发。主控全量核验 `posted=34, missing=[104295], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2571→2605`、`max/frontier=104307`。

## 待跟进（更新）

- 批量累计 **2605 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十七批 · 2026-09-07 (213 条 + 迟到 3 条)→ 已清零

**账号:** Enough1122 · **处理:** 213/213 标 Done（+3 迟到补清 +3 回评）· **处理后未读:** 0
构成: comment 200 + mention 13 · 定向 @Enough1122: 3（DavidMetcalfe 全回复）

## 定向 @Enough1122（3 条）→ 实证核验后回评

- #103968 i18n：pt 坍缩有意 + 下划线超集确认 → [5563834606](https://github.com/NousResearch/hermes-agent/pull/103968#issuecomment-5563834606)
- #103958 win CA bundle：进程级 memo 有意 + 纯证书确认 + sys.path 作用域 → [5563835552](https://github.com/NousResearch/hermes-agent/pull/103958#issuecomment-5563835552)
- #104022 launchd：kickstart 双变体已覆盖 + urlopen 已 with + 1/3 已落地 → [5563836512](https://github.com/NousResearch/hermes-agent/pull/104022#issuecomment-5563836512)

## 其余 210 条

- **mention 13 条:** 86198/87264/92440/91234 Diaspar4u 重基系列、92122/74424/96913/86062/92590/90078/102666/72637 无实体、102162 已关 → 信息性
- **第三方 20+ 条（非定向）:** kshitijk4poor 落地 8 条（#103397/#104039/#103740/#86184/#102503/#103577/#103680/#102454）、mrkillbobbot 批量、73433 clkaobot 重基等 → 社区自洽
- **其余 ~180 条:** 作者自更新/已关收尾（Christopher-Schulze×40、KhanCold×9、liuhao1024×8、rodrigogs×7 等），订阅噪音
- **迟到 3 条:** feishu×2 + state 自愈补清

## 处置

- 216/216 标 Done（含迟到），失败 0，收件箱归零；3 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 2605 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十八批 · 2026-09-07 (101 条 + 迟到 3 条)→ 已清零

**账号:** Enough1122 · **处理:** 101/101 标 Done（+3 迟到补清 +7 回评）· **处理后未读:** 0
构成: comment 89 + mention 12 · 定向 @Enough1122: 7

## 定向 @Enough1122（7 条）→ head-SHA 核验后回评

- #104345 thought_signature（0xMoat, head `3d7071f6`==所援 fix commit）：extra_content/google 保留 + 嵌套元数据变更修复 + 13 用例回归 → [5568054962](https://github.com/NousResearch/hermes-agent/pull/104345#issuecomment-5568054962)
- #104585 kanban board 定向（bunnyfu）：target_conn try/finally 全路径 + 跨板 root 留痕设计 + dest/幂等位同意 → [5568057075](https://github.com/NousResearch/hermes-agent/pull/104585#issuecomment-5568057075)
- #104685 capabilities 注册表（DavidMetcalfe, head `33e3cbd9`==所援 test-only commit）：换行 + 双关系型 tripwire（mutation 双向验证）→ [5568059274](https://github.com/NousResearch/hermes-agent/pull/104685#issuecomment-5568059274)
- #104573 cron `all` 投递（DavidMetcalfe, head `725e8469`==所援 help commit）：fire 路径先存 + 零通道 live 探针 → [5568061424](https://github.com/NousResearch/hermes-agent/pull/104573#issuecomment-5568061424)
- #104611 Write Gate 重登（DavidMetcalfe）：全仓调用点清扫验证 → [5568063695](https://github.com/NousResearch/hermes-agent/pull/104611#issuecomment-5568063695)
- #104510 model 搜索折叠（DavidMetcalfe, head `2b6b58f7`==所援回归 commit）：downloads 漏网已补 + spellcheck 有意 → [5568065848](https://github.com/NousResearch/hermes-agent/pull/104510#issuecomment-5568065848)
- #103560 CI approval 请求（Wjavan）：无权触发，需 maintainer → [5568068151](https://github.com/NousResearch/hermes-agent/pull/103560#issuecomment-5568068151)（如实拒，非 ack）

## 其余 94 条

- **mention 12 条去向：** 7 条即上（@me 同体）、99992 ping kshitijk4poor、93730 fjh990809 重基、104580/104697/85744 无实体 → 信息性
- **第三方（非定向，抽样）：** teknium1×2（#104439/#104456）、alt-glitch、hyeonsang010716、blpsnvlt 等 → 社区自洽
- **其余：** 作者自更新/已关收尾（AlexxRussell×3、Finn763×8、nateEc×6、liuhao1024×9、fangliquanflq×4 等），订阅噪音
- **迟到 3 条：** test pinning×3 补清

## 处置

- 104/104 标 Done（含迟到），失败 0，收件箱归零；7 条 @me 已回评闭环

## 待跟进（更新）

- 批量累计 **2605 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第八十九批 · 2026-09-07 续战（104308-104686）→ 141 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **348 去重→206 >frontier** → 活检筛 **141**（skip 65：comments 45 / draft 11 / reviews 9）→ diff 全收（含 18 个>60KB，最大 614KB）。

**执行：** 4 路子代理并行（36/35/35/35，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 36/36（104313-104394）
- chunk2 35/35（104397-104497）
- chunk3 35/35（104501-104597）
- chunk4 35/35（104598-104686；104669 relay `fromisoformat` ImportError 已标首要修复）

**结果：** **141/141 已 posted**，0 跳过，0 双发。主控全量核验（chunk1/3 子代理自报 + chunk2/4 全量复核 `posted=70, missing=[], dups={}`）。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2605→2746`、`max/frontier=104686`。

## 待跟进（更新）

- 批量累计 **2746 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十批 · 2026-09-08 (199 条 + 迟到 2 条)→ 已清零

**账号:** Enough1122 · **处理:** 199/199 标 Done（+2 迟到补清 +2 re-review）· **处理后未读:** 0
构成: comment 184 + mention 15 · 定向 @Enough1122: 2（均为“再看一眼”请求）

## 定向 @Enough1122（2 条）→ 增量 re-review 已发

- #93949 Google OAuth 看板（kozliatko，先前 4 点已在 `6f8e9e15`/`858c4a0f` 落地）：head diff 全量核验 4 点闭环 → 先误转义（pwsh 反引号污染，已 DELETE 5576905899）→ 重发干净版 [5576911130](https://github.com/NousResearch/hermes-agent/pull/93949#issuecomment-5576911130)
- #97224 checkpoint 策略（thewulf7，09-01 复评后新 commit `9318d80`）：增量 diff 10KB 精读，terminal 降级为命令级门控 + cwd 经 `_resolve_path_for_task` + 策略可配置 + hook 失败提级 warning → 同上转义事故（DELETE 5576907102）→ 重发 [5576912841](https://github.com/NousResearch/hermes-agent/pull/97224#issuecomment-5576912841)
- **教训：** `python -c` 双引号内写 review 正文必被 pwsh 反引号转义；此后正文一律先落 `.md` 文件再 POST（本次已执行）

## 其余 197 条

- **mention 15 条：** 2 条即上（@me 同体）、104585 bunnyfu fork-CI 收据（我 ack 的 head 的佐证，无需回）、103560 alt-glitch triage 注记、104510 已关、85791 已关、102109 已关、92122/104697/84409/104580/96913/97222/84962 无实体、92267 ogrrd 重基说明 → 信息性
- **其余：** 作者自更新/已关收尾（jerrygooch×5、liuhao1024 系、0xble×4、lorencato23×4、teknium1 系终审等），订阅噪音
- **迟到 2 条：** cron bot-chat×2 补清

## 处置

- 201/201 标 Done（含迟到），失败 0，收件箱归零；2 条 @me 已 re-review 闭环

## 待跟进（不变）

- 批量累计 2746 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十一批 · 2026-09-08 续战（104687-104885）→ 54 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **429 去重→103 >frontier** → 活检筛 **54**（skip 49：comments 39 / draft 6 / reviews 4）→ diff 全收（含 3 个>60KB，最大 296KB）。

**执行：** 3 路子代理并行（18/18/18，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 18/18（104692-104752）
- chunk2 18/18（104756-104830）
- chunk3 18/18（104835-104885，主控独立复核通过）

**结果：** **54/54 已 posted**，0 跳过，0 双发。主控全量核验（`c30_c12: posted=36` + `c30_c3: posted=18`，`dups={}`）。另 2 条 re-review（#93949/#97224）补入 posted 集合做去重。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2746→2802`（54 批量 + 2 re-review 补录）、`max/frontier=104885`。

## 待跟进（更新）

- 批量累计 **2802 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十二批 · 2026-09-08 (118 条)→ 已清零

**账号:** Enough1122 · **处理:** 118/118 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 103 + mention 15 · 定向 @Enough1122: 1

## 定向 @Enough1122（1 条）→ head-SHA 核验后回评

- #105000 project marker rename/move（Halldrix, head `bb76d210`）：5 点逐项回应（heal-on-read 即 feature、未知 id fail-open、marker I/O 永不抛、32-stat 非热路径 + 排版同意），无代码变更 → 接受闭环 [5581954315](https://github.com/NousResearch/hermes-agent/pull/105000#issuecomment-5581954315)

## 其余 117 条

- **mention 15 条：** 97222/97224 thewulf7 请 teknium1 复审（非定向）、92440/72638/87264 Diaspar4u 重基系列、102840/84409 Halldrix 致谢与复现确认、102675 mannsion 询问、96080 TwoRobotsinaTrenchcoat 重基（署名 PR 本体，非阻塞跟进不变）、105000 同上、91234/86198/18188/92122 无实体、82874 issue 部署侧已关 → 信息性
- **第三方 10 条（非定向）：** 94262 npm audit 佐证、105141 ppuksi 下游复现、104134 友好 ping、104534/103999 flyover bot、97902 gaoanze888 关重保主、105390 关联工作、88320 指向说明、52289 超前分支提醒、97753 方向同意 + 边角 → 社区自洽
- **其余：** 作者自更新/已关收尾（Doud-FR×6、Diaspar4u×7、liuhao1024×6、fangliquanflq×4、jerrygooch 等），订阅噪音

## 处置

- 118/118 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 2802 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十三批 · 2026-09-08 续战（104886-105446）→ 152 条并行（新规则，历史最大）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **311 去重→228 >frontier** → 活检筛 **152**（skip 76：comments 67 / draft 7 / reviews 2）→ diff 全收（含 13 个>60KB，最大 289KB）。

**执行：** 5 路子代理并行（31/31/31/31/28，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 31/31（104890-105065；子代理结果文件为中间态 22，API 全量复核补齐 31）
- chunk2 31/31（105067-105173）
- chunk3 31/31（105175-105273）
- chunk4 31/31（105274-105373）
- chunk5 28/28（105375-105446）

**结果：** **152/152 已 posted**，0 跳过，0 双发。主控全量核验 `posted=152, missing=[], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2802→2954`、`max/frontier=105446`。

## 待跟进（更新）

- 批量累计 **2954 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十四批 · 2026-09-08 (64 条)→ 已清零

**账号:** Enough1122 · **处理:** 64/64 标 Done（+3 回评）· **处理后未读:** 0
构成: comment 60 + mention 4 · 定向 @Enough1122: 3

## 定向 @Enough1122（3 条）→ head-SHA 核验后回评

- #105182 worker 准入合并（dalzio）：跨 key 序列化是设计目标（限流非去重）、HoL 取舍有 Boundaries 文档 → 接受闭环 [5585191205](https://github.com/NousResearch/hermes-agent/pull/105182#issuecomment-5585191205)
- #105671 长路径归档（Wenfengcheng, head `b494accc`==所援）：`import os` 实在第 15 行（raw 拉取 3260 行核验）→ 我那条是误报，撤回并认错 [5585193342](https://github.com/NousResearch/hermes-agent/pull/105671#issuecomment-5585193342)
- #105647 createPortal（Wenfengcheng）：信任边界一致（已信任插件 JS、无新隔离边界）、React/原生传播澄清留档 → 接受闭环 [5585195282](https://github.com/NousResearch/hermes-agent/pull/105647#issuecomment-5585195282)

## 其余 61 条

- **mention 4 条：** 3 条即上（@me 同体）、105175 无实体 → 信息性
- **第三方 8 条（非定向）：** 92213 上游硬限制确认、91224 独立实现验证、105264 flake 数据转交、87038 真机验证 + 改向建议、105454 五 PR 同 bug 系谱（#105168 最早）、94114 授权口径问、100098 独立回归验证、89865 本地 fix 佐证 → 社区自洽
- **其余：** 作者自更新/已关收尾（Bergmann89×6、andyst-dev×10、liuhao1024×6、chrisyoung2005×4 等），订阅噪音

## 处置

- 64/64 标 Done，失败 0，收件箱归零；3 条 @me 已回评闭环（含 1 条误报撤回）

## 待跟进（不变）

- 批量累计 2954 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十五批 · 2026-09-08 续战（105447-105682）→ 88 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **427 去重→131 >frontier** → 活检筛 **90**（skip 41：comments 35 / draft 3 / reviews 3）→ diff 全收（含 6 个>60KB，最大 335KB）。

**执行：** 4 路子代理并行（23/23/23/21，按编号序，单条 sleep 8，发前二次活检 + 幂等去重，API ≤4 线程；禁全目录清理）：
- chunk1 23/23（105447-105503；105455 cell 转义、105472 信任根签发方已标人类复看）
- chunk2 23/23（105505-105557；结果文件 `_result_e32_2.json` 自报 23，主控复核一致）
- chunk3 23/23（105559-105625）
- chunk4 19/21（105626-105680；105681 reviews=1+inline=3、105682 issues=1 被他人抢先，正确跳过；105627 Hooks 违规、105630 fail-open、105672 空 commits 等已标出）

**结果：** **88/90 已 posted**，2 正确跳过（105681/105682 第三方先到），0 双发。主控全量核验 `posted=88, missing=[105681,105682], dups={}`，与自报完全一致。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 2954→3042`、`max/frontier=105680`。

## 待跟进（更新）

- 批量累计 **3042 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十六批 · 2026-09-08 续战（105681-105789）→ 34 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **170 去重→53 >frontier** → 活检筛 **34**（skip 19：comments 14 / draft 3 / reviews 2）→ diff 全收（无大 PR），2 路并行（17/17）。

**执行波折：** chunk1 首棒被 provider 限流打断且未落盘评语（报零进度）；重开棒加 429 退避。复核发现首棒死前已发出 9 条（12:47–12:49，每 PR 恰 1 条）——重跑棒幂等跳过生效，0 双发。chunk1 实际 17/17（首棒 9 + 重跑 8）；chunk2 17/17（9 + 尾巴 8）。

**结果：** **34/34 已 posted**，0 跳过，0 双发。主控全量核验 `posted=34, missing=[], dups={}`。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3042→3076`、`max/frontier=105789`。

## 待跟进（更新）

- 批量累计 **3076 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十七批 · 2026-09-09 (54 条)→ 已清零

**账号:** Enough1122 · **处理:** 54/54 标 Done · **处理后未读:** 0
构成: comment 53 + mention 1 · 定向 @Enough1122: 1（thanks-only，无需回）

## 明细

- **@me 1 条：** #105757 liuhao1024 致谢（无 action items，diff 维持）→ 按 thanks-only 不回
- **mention 1 条即上**（@me 同体）→ 信息性
- **第三方 10 条（非定向）：** 92213 per-room 上游实现、93066/93751 macOS/复现证据并入、105141 催修、101980 更新口径修正预警、105779/105775 iap bug-hunting 初评、103370/87915 #105801 关联、92262 独立复现 → 社区自洽
- **其余：** 作者自更新/已关收尾（Bergmann89×6、notwitcheer merged×6、FarelRA×2、ahliweb×2 等），订阅噪音

## 处置

- 54/54 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 3076 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十八批 · 2026-09-09 续战（105790-105871）→ 26 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **197 去重→40 >frontier** → 活检初筛 22 + 5 transient error 逐一重查（4 补回，105867 确认有评论剔除）→ **26**（skip 14：comments 13 / draft 1）→ diff 全收（含 3 个>60KB，最大 230KB）。

**执行：** 2 路子代理并行（13/13，按编号序，单条 sleep 8，发前二次活检 + 幂等前置 + 429 退避，API ≤4 线程；禁全目录清理）：
- chunk1 13/13（105792-105829）
- chunk2 13/13（105831-105871）

**结果：** **26/26 已 posted**，0 跳过，0 双发。主控全量核验 `posted=26, missing=[], dups={}`；`posted_count==len(posted)` 完整性通过。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3076→3102`、`max/frontier=105871`。

## 待跟进（更新）

- 批量累计 **3102 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百批 · 2026-09-09 续战（105872-106200）→ 98 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **333 去重→155 >frontier** → 活检筛 **98**（skip 57：comments 46 / draft 9 / reviews 2，0 error）→ diff 全收（含 2 个>60KB，最大 69KB）。

**执行：** 4 路子代理并行（25/25/25/23，按编号序，单条 sleep 8，发前二次活检 + 幂等前置 + 429 退避，API ≤4 线程；禁全目录清理）：
- chunk1 25/25（105878-105993）
- chunk2 25/25（105998-106056）
- chunk3 25/25（106057-106126；106090 guarded-import 先于 ensure_ready 真小 bug、106083 legacy key、106101 retention×3 等已标出）
- chunk4 23/23（106128-106200；106158 广告 bump 与 diff 不符、106183 缓存 token 双计、106196 工具链未 pin 等已标出）

**工具坑（chunk3 上报，已评估无害）：** WinPS `@($null).Count==1` 误报有评论、WinPS 5.1 `Invoke-RestMethod` 烂非 ASCII（改 curl.exe 解）。误报方向是多跳过而非多发，且四路 skip 全 0，主控复核 98/98 实发印证无影响。已记入 SOP 避坑。

**结果：** **98/98 已 posted**，0 跳过，0 双发。主控全量核验 `posted=98, missing=[], dups={}`；`posted_count==len(posted)` 完整性通过。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3102→3200`、`max/frontier=106200`。

## 待跟进（更新）

- 批量累计 **3200 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第九十九批 · 2026-09-09 (48 条)→ 已清零
**账号:** Enough1122 · **处理:** 48/48 标 Done（+3 回评）· **处理后未读:** 0
构成: comment 44 + mention 4 · 定向 @Enough1122: 3（Halldrix 逐点核验三连）

## 定向 @Enough1122（3 条）→ head-SHA 核验后回评

- #104068 bot-chat 双流上报（Halldrix, head `3c858e51`）：空流守卫有测试钉 + 纯诊断不碰投递 → 接受闭环 [5594612683](https://github.com/NousResearch/hermes-agent/pull/104068#issuecomment-5594612683)
- #104131 artifact 路径路由（Halldrix, head `7a21cca0`）：tilde-user 拒绝有意 + renderer 极简名单无害 + 危险 scheme 有测试钉 → 接受闭环 [5594613849](https://github.com/NousResearch/hermes-agent/pull/104131#issuecomment-5594613849)
- #105555 compaction 落盘（Halldrix, head `f842dfdf`）：attempt 锚定 + retention 同 diff 内覆盖 + fail-open 可观测有意 → 接受闭环 [5594615028](https://github.com/NousResearch/hermes-agent/pull/105555#issuecomment-5594615028)

## 其余 45 条

- **mention 4 条：** 3 条即上（@me 同体）、85428 无实体 → 信息性
- **第三方 2 条（非定向）：** 84650 机制背书、104221 flyover → 社区自洽
- **其余：** 作者自更新/已关收尾（tachyon-r×9、KhanCold×9、0xble×2 等），订阅噪音

## 处置

- 48/48 标 Done，失败 0，收件箱归零；3 条 @me 已回评闭环

## 待跟进（更新·顺序注记）

- 批量累计 **3200 条** 已发，等作者/maintainer 响应（第九十九批落笔时待跟进误写 3102，依第一百批为准）
- #96080 署名落地（非阻塞）

> 注：第九十九批与第一百批在文件中乱序（内容无缺失），以本节待跟进为准。

---

# 第一百零一批 · 2026-09-09 (51 条)→ 已清零

**账号:** Enough1122 · **处理:** 51/51 标 Done · **处理后未读:** 0
构成: comment 46 + mention 5 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 5 条：** 72638/92440/86198/87264/92122 全无实体（Diaspar4u 重基系列回声）→ 信息性
- **第三方 1 条（非定向）：** 92262 paulybeebe 53 测试全过确认 → 社区自洽
- **其余：** 作者自更新/已关收尾（Diaspar4u×5、frizikk×6、kshitijk4poor merged×3 等），订阅噪音

## 处置

- 51/51 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（更新）

- 批量累计 **3200 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零二批 · 2026-09-09 续战（106201-106445）→ 63 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取（09-08 回扫补漏）**146 去重→131 >frontier** → 活检初筛 64 + 2×504 transient 重查（均有评论，剔除）→ **64**（skip 67：comments 62 / draft 4 / reviews 1）→ diff 全收（含 6 个>60KB，最大 432KB）。

**执行：** 3 路子代理并行（22/21/21，按编号序，单条 sleep 8，发前二次活检 + 幂等前置 + 429 退避，API ≤4 线程；禁全目录清理）：
- chunk1 22/22（106204-106286；106250 probable double-listing、106216 64 文件打包已标出）
- chunk2 21/21（106288-106358）
- chunk3 20/21（106360-106445；106445 活检后新增评论，正确跳过）

**结果：** **63/64 已 posted**，1 正确跳过（106445 第三方先到），0 双发。主控全量核验 `posted=63, missing=[106445], dups={}`，与自报完全一致；`posted_count==len(posted)` 完整性通过。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3200→3263`、`max/frontier=106440`。

## 待跟进（更新）

- 批量累计 **3263 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零三批 · 2026-09-09 (40 条)→ 已清零

**账号:** Enough1122 · **处理:** 40/40 标 Done · **处理后未读:** 0
构成: comment 38 + author 1 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条：** 92122 无实体 → 信息性
- **第三方 6 条（非定向）：** 106326 workaround 实证、94680 状态检查 + 回归预警、106360 Win11 原生验证、103489 方向确认 + 一处 flag、90677 Telegram 实地证据、105274 Thorium 漏网补充 → 社区自洽
- **域外 1 条：** runhey/OnmyojiAutoScript#1802（author ping，非 hermes-agent 范围，只标 Done 不动作）
- **其余：** 作者自更新/已关收尾（teknium1、kshitijk4poor merged×3、nftpoetrist merged 等），订阅噪音

## 处置

- 40/40 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 3263 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零四批 · 2026-09-09 续战（106441-106627）→ 47 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取（09-08 回扫：106441 系 404 幽灵号，无遗漏）**243 去重→115 >frontier** → 活检筛 **47**（skip 68：comments 64 / draft 3 / reviews 1，0 error）→ diff 全收（无大 PR），3 路并行（16/16/15）。

**执行：** 3 路子代理并行（16/16/15，按编号序，单条 sleep 8，发前二次活检 + 幂等前置 + 429 退避，API ≤4 线程；禁全目录清理）：
- chunk1 16/16（106450-106500；106479 重试全砍、106491 私人邮箱误带已标出）
- chunk2 16/16（106502-106599）
- chunk3 15/15（106602-106627）

**结果：** **47/47 已 posted**，0 跳过，0 双发。主控全量核验 `posted=47, missing=[], dups={}`；`posted_count==len(posted)` 完整性通过。

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3263→3310`、`max/frontier=106627`。

## 待跟进（更新）

- 批量累计 **3310 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零五批 · 2026-09-10 (179 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 179/179 标 Done（+1 迟到补清 +4 回评）· **处理后未读:** 0
构成: comment 172 + mention 7 · 定向 @Enough1122: 4

## 定向 @Enough1122（4 条）→ head-SHA 核验后回评

- #105053 branch-pin（0xalydev, head `94df746c`）：双缺 heal/畸形输出保活/离散 argv/DI 快径四点确认 → 接受闭环 [5611124060](https://github.com/NousResearch/hermes-agent/pull/105053#issuecomment-5611124060)
- #90781 blockquote 排序（sg-shag, head `e8664123`）：_clean 系上下文未动 + #89997 互补定位接受；**纠偏 1 处**：chunk 后缀转义并未完全拿掉（send_message_tool.py 仍新增，import 而非复制 + 回归测试，原担忧落空但添加正当）→ [5611125299](https://github.com/NousResearch/hermes-agent/pull/90781#issuecomment-5611125299)
- #106219 per-session Docker（DavidMetcalfe, head `9d261167`==所援 fix commit）：reaper 补 pop close-key + 失败则红回归测试 → 真泄漏闭环 [5611126637](https://github.com/NousResearch/hermes-agent/pull/106219#issuecomment-5611126637)
- #106246 suppress_memory_notify（DavidMetcalfe, head `a675ba9d`）：窄 guard 接受（_load_config 双路径已吞 Exception + 兄弟同形 + 测试钉）→ [5611128045](https://github.com/NousResearch/hermes-agent/pull/106246#issuecomment-5611128045)

## 其余 175 条

- **mention 7 条：** 4 条即上（@me 同体）、92122 无实体、105205 JamesQuirk 贴我评语（认同引用）、105182 已关 → 信息性
- **第三方 18 条（非定向，teknium1 系终审为主）：** 104024  spray 系谱图、90678/93386/101528/101480/101496/101243 exact-head 复审、106290/99953/102873/86214 合并转交、105636 分包修复、98116 多 profile 警告、91224 独立复现、93580 冲突提醒、104323/96272/100098 跟进 → 社区自洽
- **其余：** 作者自更新/已关收尾（Xipong×10、KoNit-K×7、kshitijk4poor merged×7、100yenadmin、Christopher-Schulze 等），订阅噪音
- **迟到 1 条：** wisdom 补清

## 处置

- 180/180 标 Done（含迟到），失败 0，收件箱归零；4 条 @me 已回评闭环（含 1 处纠偏）

## 待跟进（不变）

- 批量累计 3310 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零六批 · 2026-09-10 续战（106628-107015）→ 117 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **337 去重→200 >frontier** → 活检筛 **117**（skip 83：comments 68 / draft 11 / reviews 4，0 error）→ diff 收 116/117（#106808 以 103 文件 +23k 行触发 diff 接口 406，该 chunk 改走 files API 逐页取 patch 审读）。

**执行：** 5 路子代理并行（24/24/24/24/21，按编号序，单条 sleep 8，发前二次活检 + 幂等前置 + 429 退避，API ≤4 线程；禁全目录清理）：
- chunk1 24/24（106632-106715）
- chunk2 24/24（106717-106812，含 #106808 files API 特审；子代理未回终报，主控 API 直查确认 24/24）
- chunk3 24/24（106819-106900）
- chunk4 24/24（106901-106945；106920 跨 PR 引用 clicksmith 模块待确认已标出）
- chunk5 21/21（106951-107015）

**结果：** **117/117 已 posted**，0 跳过，0 双发。主控全量核验 `posted=117, missing=[], dups={}`；`posted_count==len(posted)` 完整性通过。

**处置：** 已落盘 `drafts/_campaign/{n}.diff`（除 106808 外）与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3310→3427`、`max/frontier=107015`。

## 待跟进（更新）

- 批量累计 **3427 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零七批 · 2026-09-10 (16 条)→ 已清零

**账号:** Enough1122 · **处理:** 16/16 标 Done · **处理后未读:** 0
构成: comment 16 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **第三方 1 条（非定向）：** 91206 Robin021 实地数据 + 两处 gap → 社区自洽
- **其余：** 作者自更新/已关收尾（moonweave×4、projetsjsl×3 等），订阅噪音

## 处置

- 16/16 标 Done，失败 0，收件箱归零；无需回评

## 待跟进（不变）

- 批量累计 3427 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百零八批 · 2026-09-10 续战（107016-107126）→ 27 条并行（新规则）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿，不限大小）。search 日切片拉取 **377 去重→54 >frontier** → 活检筛 **28**（skip 26：comments 21 / draft 4 / reviews 1，0 error）→ diff 全收（含 3 个>60KB，最大 302KB）。

**执行（含一次双开事故与幂等实证）：** 本批误将 3 个 chunk 各启动了两套共 6 个子代理，两套互为“并发评审者”。结果全部被“发评前二次活检 + 幂等跳过”正确互拦，**最终 0 双发**，反而实地验证了幂等机制：
- chunk1（107031-107069）：二棒先发 7，一棒发 3（107060/107065/107069），各方向互跳 — **10/10 唯一**
- chunk2（107071-107108）：一棒发 6（107071/107078/107081/107103/107105/107107），二棒发 3（107079/107092/107100）— **9 发**；107108 被 ehz0ah 人类 review（1 review + 2 inline，指出 Anthropic mid-history system 角色覆盖）抢先，两棒均正确弃评
- chunk3（107111-107126）：二棒发 8，一棒全部幂等跳过 — **8/8 唯一**

**结果：** **27/28 已 posted**（唯一数），1 正确跳过（107108），0 双发。主控全量核验 `unique_posted=27, missing=[107108], dups={}`；`posted_count==len(posted)` 完整性通过。

**要点留档：**
- 107124 草稿发现可复现的 4+ 分隔符绕过（delegation quality gate feedback 去毒不足，`tools/delegation_quality_gate.py:186-190`），未进已发评语，仅备注留档（不补发第二条，维持一 PR 一评）
- 107111 嵌套插件崩溃可致 journal 判定 unsafe 卡死后续发现/安装（`plugins_cmd.py:1008` vs `plugin_install_state.py:262`）
- 107103 与 #107071 跨 PR 冲突（删除 `chatImagePaste.ts`）、107107 vitest 其余包仍 4.1.10

**处置：** 已落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3427→3454`、`max/frontier=107126`。

## 待跟进（更新）

- 批量累计 **3454 条** 已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）
- 教训：批量派发前先核对是否已派同编号 chunk（本批双开未致损，但需避免）

---

# 第一百零九批 · 2026-09-10 (18 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 18/18 标 Done（+1 迟到补清 +1 回评）· **处理后未读:** 0
构成: comment 12 + mention 6 · 定向 @Enough1122: 1

## 定向 @Enough1122（1 条）→ head-SHA 核验后回评

- #106660 Luna Reserve fallback（albidev, head `9a32a23b`==所援 commit）：常量集中化 + reserve 耗尽推进测试钉 + 防御性 getattr，三处均在 head diff 实证 → 接受闭环 [5614940301](https://github.com/NousResearch/hermes-agent/pull/106660#issuecomment-5614940301)

## 其余 17 条

- **mention 6 条：** 1 条即上（@me 同体）、92440/87264/91234/96913 无实体、18188 lancecheney 冲突解决致谢 → 信息性
- **第三方 1 条（非定向）：** 88189 Chriswenwener 生产侧泄漏佐证 → 社区自洽
- **其余：** 作者自更新/已关收尾（Diaspar4u×5、KoNit-K×3 等），订阅噪音
- **迟到 1 条：** Responses verbosity 补清

## 处置

- 19/19 标 Done（含迟到），失败 0，收件箱归零；1 条 @me 已回评闭环

## 待跟进（不变）

- 批量累计 3454 条已发，等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 长期决策 · 2026-09-10：review 战役收官，转 inbox-only

**用户决策：** 不再批量审核 PR（审查耗精力 + 烧 token，这种活交还社区），以后只处理 GitHub inbox。
**终局：** 累计 posted **3454**，frontier **107126**（state 已标 `retired-inbox-only`）。
**Inbox SOP 不变：** triage → @me 实证核验后回评 → 全标 Done → 归零核验 → 战报续记。
**例外（2026-09-10 用户补充）：** 已审查过的 PR，若作者 @我们请求协助审查，可以接（先核 head SHA + diff，增量复评）。

---

# 第一百一十批 · 2026-09-10 (33 条)→ 已清零（inbox-only 首批）

**账号:** Enough1122 · **处理:** 33/33 标 Done · **处理后未读:** 0
构成: comment 31 + mention 2 · 定向 @Enough1122: 0 · 复审请求: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 2 条：** 86062 无实体、107126 已关（MiseHinoha 确认被 #107236 取代）→ 信息性
- **第三方 1 条（非定向）：** 106971 monerostar Win11 原生验证 → 社区自洽
- **其余：** 作者自更新/已关收尾（aniruddhaadak80×17、Gabrielnkl×2 等），订阅噪音

## 处置

- 33/33 标 Done，失败 0，收件箱归零；无需回评（无复审请求触发例外条款）

---

# 第一百一十一批 · 2026-09-11 (18 条)→ 已清零

**账号:** Enough1122 · **处理:** 18/18 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 16 + mention 2 · 定向 @Enough1122: 1（复审请求，例外条款触发）

## 定向 @Enough1122（1 条）→ 增量复评已发

- #107078 ntfy attachments（DavidMetcalfe, head `7efc4c064`==所援 commit）：五点全在增量 diff（22KB compare）实证——类型守卫 return 化 + 字节截断双处 + media message_id + 文档改写 + 服务器感知 2MB/15MB 上限（含 mutation 验证）；作者对 15MB 的 live probe 纠偏一并接受 → [5622022359](https://github.com/NousResearch/hermes-agent/pull/107078#issuecomment-5622022359)

## 其余 17 条

- **mention 2 条：** 89921 无实体、107078 即上（@me 同体）→ 信息性
- **其余：** 作者自更新/已关收尾（aniruddhaadak80×9、KoNit-K 等），订阅噪音

## 处置

- 18/18 标 Done，失败 0，收件箱归零；1 条 @me 已增量复评闭环

---

# 第一百一十二批 · 2026-09-11 (141 条 + 迟到 4 条)→ 已清零

**账号:** Enough1122 · **处理:** 141/141 标 Done（+4 迟到补清 +7 回评）· **处理后未读:** 0
构成: comment 133 + mention 8 · 定向 @Enough1122: 7（6 快照内 + 1 迟到 mention 内挖出）

## 定向 @Enough1122（7 条）→ head-SHA 核验后回评

- #106706 auto-reveal（KoNit-K, head `a442d316`==所援）：eviction + wrapper pin + 复用测试 → [5628106748](https://github.com/NousResearch/hermes-agent/pull/106706#issuecomment-5628106748)
- #106735 lifecycle 注释剥离（KoNit-K）：POSIX 规则 + heredoc fail-open 接受，无代码变更 → [5628108220](https://github.com/NousResearch/hermes-agent/pull/106735#issuecomment-5628108220)
- #106765 browserbase 402 缓存（KoNit-K）：key 基数有界 + 升级 stale 有文档 → [5628109616](https://github.com/NousResearch/hermes-agent/pull/106765#issuecomment-5628109616)
- #106787 unsloth QR（KoNit-K）：全仓 sweep 1391 绿 + fail-open matcher 接受 → [5628110900](https://github.com/NousResearch/hermes-agent/pull/106787#issuecomment-5628110900)
- #106791 memory 路由（KoNit-K）：显式路由句 + 有界例外 + fail-open 接受 → [5628112268](https://github.com/NousResearch/hermes-agent/pull/106791#issuecomment-5628112268)
- #107103 TUI draft 附件（pepmach, head `94cc0a69`）：native 独立 32-cap（reject 不驱逐已准入，测试钉）→ [5628113529](https://github.com/NousResearch/hermes-agent/pull/107103#issuecomment-5628113529)
- #106704 feishu 热加载（KoNit-K, head `8b474cbe`==所援；迟到 mention 内挖出）：(mtime,size) 指纹 + `_rule_id_set` 统一，两处 diff 实证 → [5628186413](https://github.com/NousResearch/hermes-agent/pull/106704#issuecomment-5628186413)

## 其余 134 条

- **mention 8 条：** 6 条即上@me同体 + 84236 YS-OH-CORE 补丁提供 + 82393 alt-glitch 簇更新 + 92122 无实体 + 85388/105537 请审他人 + 102840 macOS 验证 + feishu 迟到即上 → 信息性
- **第三方 22 条（非定向，teknium1 系终审为主）：** 落地/转交/重定向通知 10+ 条（102145/100625/93759/91150/96404/91483/106078/100289/99810/105636/99953/102873/86214）、独立验证（102928/100992/98145/91570/102840）、数据点（85393/84565/95449/93580/104323/96272）→ 社区自洽
- **其余：** 作者自更新/已关收尾（tachyon-r 关闭 5、KhanCold 关闭 9、Xipong 系、KoNit-K 系、nftpoetrist 等），订阅噪音
- **迟到 4 条：** feishu mention、updater、mcp proxy env、adapter registry 补清

## 处置

- 145/145 标 Done（含迟到），失败 0，收件箱归零；7 条 @me 已回评闭环（其中 1 条系迟到 mention 内挖出——迟到项亦须扫 @me）

## 经验

- 迟到补清的 mention 也可能藏 @me（本批 #106704），以后补清后加扫一遍 involved/mention

---

# 第一百一十三批 · 2026-09-11 (43 条)→ 已清零

**账号:** Enough1122 · **处理:** 43/43 标 Done（+3 回评）· **处理后未读:** 0
构成: comment 40 + mention 3 · 定向 @Enough1122: 3（KoNit-K Path C 三连）

## 定向 @Enough1122（3 条）→ head-SHA 核验后回评

- #106693 approval reaper 广播（KoNit-K, head `c61ba49c`）：`orphan=` kwarg 解耦前缀嗅探（双向测试钉）+ count/ids 语义文档化 → diff 实证闭环 [5630117642](https://github.com/NousResearch/hermes-agent/pull/106693#issuecomment-5630117642)
- #106697 隐藏窗轮询（KoNit-K）：可见性 CONTROL 设计 + 清理守卫 + seed-once 契约接受，无代码变更 → [5630118729](https://github.com/NousResearch/hermes-agent/pull/106697#issuecomment-5630118729)
- #106702 Windows resume（KoNit-K）：resume-once + fail-open + None 安全路径接受 → [5630119965](https://github.com/NousResearch/hermes-agent/pull/106702#issuecomment-5630119965)

## 其余 40 条

- **mention 3 条：** 92122 无实体、106704 KoNit-K 对 #106710 的 delta 说明（已评 PR 的自洽注记）、84236 Halldrix 确认 YS-OH-CORE 复现成立 → 信息性
- **第三方 4 条（非定向）：** 102993/106897 jquesnelle 纳入致谢、95295 兼容性评审、94781 teknium1 转交 → 社区自洽
- **其余：** 作者自更新/已关收尾（KoNit-K×5、x7peeps×5、KoNit-K 关 1 等），订阅噪音

## 处置

- 43/43 标 Done，失败 0，收件箱归零；3 条 @me 已回评闭环

---

# 第一百一十四批 · 2026-09-11 (32 条)→ 已清零

**账号:** Enough1122 · **处理:** 32/32 标 Done · **处理后未读:** 0
构成: comment 30 + mention 2 · 定向 @Enough1122: 4（KoNit-K Path C 复核 FYI×4，无需回）

## 明细

- **@me 4 条：** 106693/106787/106702/106791 KoNit-K “Ack 后复核：无 review 线程、无 CHANGES_REQUESTED、无 CI 失败、merge-tree clean、无事可做” → FYI 类，按 thanks/confirmation 不回；已轻量核验 4 个 PR 均无第三方 review，确认无动作项
- **mention 2 条：** 92122 无实体、84409 Halldrix 复现确认 + 补丁提供 → 信息性
- **第三方 6 条（非定向）：** 84045/93365 brianoestberg 下游催办、100492 实测、103959 原 reporter 佐证、105836/100629 kshitijk4poor 复审转交 → 社区自洽
- **其余：** 作者自更新/已关收尾（KoNit-K×5 等），订阅噪音

## 处置

- 32/32 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百一十五批 · 2026-09-11 续战（107127-108095）→ 17 实发 + 306 静默（新口径首战）

**口径：** 新规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿；**只发有问题的**，干净静默记 clean）。search 日切片拉取 **561 去重→514 >frontier** → 活检筛 **330**（skip 184：comments 172 / draft 5 / reviews 7，0 error）→ diff 全收（含 15 个>60KB，最大 443KB）。

**执行：** 11 路子代理并行（×30，按编号序，发前二次活检 + 幂等前置 + 429 退避，API ≤4 线程；存疑点一律 PR-head 交叉证伪，不硬发；禁全目录清理）。

**结果：** **posted 17 / clean 306 / skipped 7**，合计 330 对账齐。主控全量核验 `posted=17, missing=[], dups={}`；`posted_count==len(posted)` 完整性通过。

实发 17（个个带可举证缺陷）：107145 session key 分裂、107150 迁移残表、107241 fail-closed 破口、107429 硬编码路径+吞异常、107610 cwd 清理失效（实测）、107650/107675 测试读源码违规、107689 脱敏正则漏网（实测）、107716 跨 PR 断言冲突、107750 凭据 masking 违背保证、107933 硬编码 ⌘B、107934 docstring 矛盾、107938 子串误伤、108021 YAML 布尔漏认、108046 倒计数写反、108056/108057 ci.yaml 非法缩进。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3454→3471`（仅计实发）、`reviewed_clean` +306、`max=108057`、`frontier=108095`（108095 本人有评论，永久不合格，前沿越过无漏网）。

## 待跟进（更新）

- 批量累计实发 **3471 条**（+306 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）
- 下轮 collect/biopsy 须同步过滤 `posted + reviewed_clean`（search comments:0 仍会捡回 clean 项）

---

# 第一百一十六批 · 2026-09-11 (23 条)→ 已清零

**账号:** Enough1122 · **处理:** 23/23 标 Done · **处理后未读:** 0
构成: comment 22 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条：** 96783 已关（tuancookiez-hub 总结）→ 信息性
- **第三方 1 条（非定向）：** 104586 overlap 注记 → 社区自洽
- **其余：** 作者自更新/已关收尾，订阅噪音

## 处置

- 23/23 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百一十七批 · 2026-09-11 续战（108096-108194）→ 2 实发 + 30 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 229→51（已过滤）→ 活检筛 **32**（skip 19：comments 17 / draft 1 / closed 1，0 error）→ diff 全收（无大 PR），2 路并行（16/16）。

**执行：** 2 路子代理并行（16/16，发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；禁全目录清理）：
- chunk1 0/16（5 处疑点全证伪，其余影响面为零 withhold）
- chunk2 2/16（108177 重复测试类遮蔽 + 无断言、108179 未使用 import 挂 lint；SSRF 面等 6 处证伪）

**结果：** **posted 2 / clean 30 / skipped 0**，合计 32 对账齐。主控全量核验（API 实发 == 结果文件 posted，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3471→3473`、`reviewed_clean` 306→336、`max=108179`、`frontier=108194`。

## 待跟进（更新）

- 批量累计实发 **3473 条**（+336 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百一十八批 · 2026-09-12 (66 条)→ 已清零

**账号:** Enough1122 · **处理:** 66/66 标 Done · **处理后未读:** 0
构成: comment 65 + mention 1 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 1 条：** 86062 已关（Christopher-Schulze 总结）→ 信息性
- **第三方 5 条（非定向）：** 106970 实地报告 + gap、101524 计费 bug 确认、106975/103634 teknium1 落地通知、102287 单 profile 惰性集注记 → 社区自洽
- **其余：** 作者自更新/已关收尾（state 系关单一堆、Doud-FR×5 等），订阅噪音

## 处置

- 66/66 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百一十九批 · 2026-09-12 续战（108195-108379）→ 5 实发 + 67 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 编号>前沿；只发有问题的）。search 日切片拉取 **319 去重→109 >frontier** → 活检筛 **73**（skip 36：comments 30 / draft 6，0 error）→ diff 全收（含 8 个>60KB，最大 607KB），3 路并行（25/25/23）。

**执行：** 3 路子代理（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；禁全目录清理）+ 主会话补审 1 个：
- chunk1 2/25（108208 空断言占位、108254 测试读源码违规；**漏审 108242，主会话补审**）
- chunk2 1/25（108284 Pill 精简致 tsc 失败 + 测试矛盾；500KB+ 双大 PR 抽查无事）
- chunk3 2/21（108357 沙箱逃逸面、108372 缓存键缺位；108376 有 finding 但被第三方抢先，正确跳过）
- 主会话补审 108242（composer-mode frame，69KB/29 文件全读）：'canceled' 真值协议转换齐全（use-composer-queue/submit 双处在 diff 内）、drain→compute-host 携带 frame（head 文件实证）、`_apply_correction` 的 `**_extra` 仅新参数时透传且有 except 兜底 → clean，未发

**结果：** **posted 5 / clean 67 / skipped 1**，合计 73 对账齐。主控全量核验 `posted=5, dups={}`，API 实发 == 结果文件；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`（108242 记入 chunk1 结果文件）；campaign_state.json 更新 `posted 3473→3478`、`reviewed_clean` 336→403、`max=108372`、`frontier=108379`。

## 待跟进（更新）

- 批量累计实发 **3478 条**（+403 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）
- 教训：子代理报数须与分配数核对（本批 chunk1 少报 1 个，主会话复核对账发现；已补）

---

# 规则变更 · 2026-09-11：恢复批量 review（只发有问题的）

**用户决策：** 恢复 hermes 仓库 PR 批量审查，附加新口径——
1. 任何人 review 过的不重复 review（沿用零评论/零 review/零内联门槛）；
2. **评完没发现问题的不发评语、静默跳过，只发有问题的**（blocking 或 Non-blocking findings 才 POST）。
**落地：** state.rule 已更新；新增 `reviewed_clean[]` 记录“评过且干净”的 PR（下轮不再重复捡起）；posted 计数口径改为“带 findings 的实发数”。
**风格（2026-09-11 用户补充）：** 不啰嗦不抢戏，只精准找真正有问题的点；无填充段、无通用建议、无“looks good”垫话，有 findings 才发。

---

# 第一百二十批 · 2026-09-12 (31 条)→ 已清零

**账号:** Enough1122 · **处理:** 31/31 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 24 + mention 6 + author 1 · 定向 @Enough1122: 1

## 定向 @Enough1122（1 条）→ 增量复评已发

- #105503 Czech i18n（ostravajih, head `9882bf95`）：三点全结构性实证（types.ts → +1/-1、cs 三目录 +4312/+887/+603 落地、zionzangar 原生目录 SHA 校验集成）→ [5639475015](https://github.com/NousResearch/hermes-agent/pull/105503#issuecomment-5639475015)

## 其余 30 条

- **mention 6 条：** 102840/92122 无实体、91277 更新器问题汇总、89138/89265 无网重基受阻 → 信息性
- **第三方 4 条（非定向）：** 94056 清单、104781 A/B、98538 钉正、106936 求助 → 社区自洽
- **域外 1 条：** Onmyoji author ping，只标 Done
- **其余：** 作者自更新/已关收尾，订阅噪音

## 处置

- 31/31 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

---

# 第一百二十一批 · 2026-09-12 续战（108380-108545）→ 4 实发 + 56 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 400→94（已过滤）→ 活检筛 **60**（skip 34：comments 32 / draft 2，0 error）→ diff 全收（无大 PR），3 路并行（20/20/20）。

**执行：** 3 路子代理并行（20/20/20，发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；禁全目录清理）：
- chunk1 1/20（108381 命名 no-op；6 处疑点全证伪）
- chunk2 1/20（108439 测试必挂：实现缺 `args.to` 检查；SBPL/ xe UAPI 等证伪）
- chunk3 2/20（108499 无 scope 调 secret、108511 共享 jar 锁落空；2 处证伪）

**结果：** **posted 4 / clean 56 / skipped 0**，合计 60 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3478→3482`、`reviewed_clean` 403→459、`max=108511`、`frontier=108545`。

## 待跟进（更新）

- 批量累计实发 **3482 条**（+459 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百二十三批 · 2026-09-12 续战（108546-108839）→ 7 实发 + 96 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 530→152（已过滤）→ 活检筛 **103**（skip 49：comments 34 / draft 15，0 error）→ diff 全收（含 4 个>60KB，最大 216KB），4 路并行（26/26/26/25；prompt 含完工自对账要求）。

**执行：** 4 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 4/4 通过；禁全目录清理）：
- chunk1 2/26（108572 pycs flag 漏网、108591 死 fixture；5 处证伪，diff 逐文件校验完整）
- chunk2 2/26（108658 i18n 漏传、108665 docstring 虚假；WinPS 双坑自绕）
- chunk3 2/26（108710 stop 静默成功、108722 状态行残留；3 处证伪）
- chunk4 1/25（108836 无界 repair loop；大 PR 重点扫描）

**结果：** **posted 7 / clean 96 / skipped 0**，合计 103 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3482→3489`、`reviewed_clean` 459→555、`max=108836`、`frontier=108839`。

## 待跟进（更新）

- 批量累计实发 **3489 条**（+555 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百二十二批 · 2026-09-12 (74 条)→ 已清零

**账号:** Enough1122 · **处理:** 74/74 标 Done · **处理后未读:** 0
构成: comment 67 + mention 7 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 7 条：** 92122 无实体、102840 triage 簇注记、93730 connorblack 三 gap（非定向）、100765 重基说明、105040 已关总结、89138/89265 重基状态 → 信息性
- **第三方 11 条（非定向，teknium1 系终审为主）：** 落地/转交 6 条（100448/100604/103844/96370/104534/103500 证据致谢）、独立验证 2 条（83775/93386）、求助 1 条（89570）、nftpoetrist 系 → 社区自洽
- **其余：** 作者自更新/已关收尾（nftpoetrist 关闭 8、KoNit-K×5、aniruddhaadak80×4 等），订阅噪音

## 处置

- 74/74 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百二十四批 · 2026-09-12 (9 条)→ 已清零

**账号:** Enough1122 · **处理:** 9/9 标 Done · **处理后未读:** 0
构成: comment 9 · 定向 @Enough1122: 0 · 第三方: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention: 0 条**
- 9 条全是作者自更新/已关收尾（adagues、fangliquanflq、Forser×2 已关、33hodl、JerryLiu369、chelsealong、mudi-il 已关、marcelobernardo-cf-stikcky），订阅噪音

## 处置

- 9/9 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百二十五批 · 2026-09-12 续战（108840-108889）→ 2 实发 + 12 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 117→27（已过滤）→ 活检筛 **14**（skip 13：comments 11 / draft 2，0 error）→ diff 全收（含 1 个>60KB），2 路并行（7/7；prompt 含完工自对账要求）。

**执行：** 2 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 2/2 通过；禁全目录清理）：
- chunk1 1/7（108855 中断 ACK 门控字段网关从不发送，测试 mock 掩盖；死锁等证伪）
- chunk2 1/7（108886 DNS 外带 guard 可被行续接绕过，已正则实证；stale-lock 等置信不足不发）

**结果：** **posted 2 / clean 12 / skipped 0**，合计 14 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3489→3491`、`reviewed_clean` 555→567、`max=108886`、`frontier=108889`。

## 待跟进（更新）

- 批量累计实发 **3491 条**（+567 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百二十六批 · 2026-09-12 (41 条)→ 已清零

**账号:** Enough1122 · **处理:** 41/41 标 Done · **处理后未读:** 0
构成: comment 37 + mention 4 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 4 条：** 102840/18188 无实体、96852/94411 MrTheSoulz 重基说明 → 信息性
- **第三方 1 条（非定向）：** 103653 XBold 求问特性 → 社区自洽
- **其余：** 作者自更新/已关收尾（auroracapital 关闭 6、egilewski×5、chrisyoung2005×3、tomatau×3 等），订阅噪音

## 处置

- 41/41 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百二十七批 · 2026-09-12 续战（108890-109019）→ 3 实发 + 59 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 199→86（已过滤）→ 活检筛 **62**（skip 24：comments 23 / draft 1，0 error）→ diff 全收（含 3 个>60KB，最大 712KB 走 files 分页），3 路并行（21/21/20；prompt 含完工自对账要求）。

**执行：** 3 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 3/3 通过；禁全目录清理）：
- chunk1 0/21（3 处疑点全证伪，干净）
- chunk2 2/21（108948 workflow YAML 缩进非法致门禁全挂、108986 multiplex 破坏未声明；stacked 108949/108950 增量无害归属一处发防 spam；712KB refactor 审计通过）
- chunk3 1/20（109009 归档子任务 KeyError 可达；8 处疑点逐个验证后放行）

**结果：** **posted 3 / clean 59 / skipped 0**，合计 62 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3491→3494`、`reviewed_clean` 567→626、`max=109009`、`frontier=109019`。

## 待跟进（更新）

- 批量累计实发 **3494 条**（+626 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百二十八批 · 2026-09-13 (86 条)→ 已清零

**账号:** Enough1122 · **处理:** 86/86 标 Done · **处理后未读:** 0
构成: comment 80 + mention 6 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 6 条：** 84869/85428/92122 无实体、97344 rodrigogs 回评释（非定向）、102840 Halldrix 致 ehz0ah（非定向）、109080 作者自述 → 信息性
- **第三方 12 条（非定向，teknium1 系为主）：** 落地/转交 5 条（85094/93923/89608/108179/100146 系）、独立验证 4 条（87515/104860/85793/100362 系）、求助/转述 2 条（106034/83498 系）、CI bot 1 条 → 社区自洽
- **其余：** 作者自更新/已关收尾（jeeves-assistant 关闭 5、JPeetz×5、oferlaor×5、gaoanze888×5 等），订阅噪音
- 关联：108886 同源 dns_exfil 修（liuhao1024）已关收尾

## 处置

- 86/86 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百二十九批 · 2026-09-13 续战（109020-109394）→ 20 实发 + 148 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 385→215（已过滤）→ 活检筛 **168**（历史最大；skip 47：reviews 26 / comments 17 / draft 4，0 error）→ diff 全收（含 10 个>60KB，最大 426KB 走 files 分页），6 路并行（28×6；prompt 含完工自对账要求）。

**执行：** 6 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 6/6 通过；禁全目录清理）：
- chunk1 4/28（109021 文档 fence、109037 删不变测试、109044 签名 None、109046 约束漏判）
- chunk2 7/28（109066 kitchen-sink、109070 硬编码、109075 重复 hunk、109080 空 scope 测试、109098 关 asar 校验、109099 探针回归、109102 漏 session_key）
- chunk3 1/28（109113 login 类型错配；4 处证伪）
- chunk4 1/28（109242 split 截断终答；233KB 审计放行）
- chunk5 3/28（109263 Decimal 漏捕、109298/109300 argv 永 miss 且互斥；164KB/流式等放行）
- chunk6 4/28（109305 id 键被杀、109328 并发 rotation 丢弃、109347/109348 Mock 双不兼容；Honcho 大 PR 逐项证伪）

**结果：** **posted 20 / clean 148 / skipped 0**，合计 168 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3494→3514`、`reviewed_clean` 626→774、`max=109348`、`frontier=109394`。

## 待跟进（更新）

- 批量累计实发 **3514 条**（+774 clean 静默），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百三十批 · 2026-09-14 (240 条 + 迟到 1 条)→ 已清零

**账号:** Enough1122 · **处理:** 241/241 标 Done（+2 回评）· **处理后未读:** 0
构成: comment 187 + mention 53（+迟到 comment 1）· 定向 @Enough1122: 38

## 定向 @Enough1122（38 条）

- **yflmq001 #108254**（实质跟进：getsource 源文本测试已换成 Popen-stub 行为测试）：head `38c54331fdf4` 实证（getsource 消失、stub 落地）→ ack [5658000918](https://github.com/NousResearch/hermes-agent/pull/108254#issuecomment-5658000918)
- **Qwinty #109066**（实质跟进：承认 scope 问题，从干净 upstream 重建分支）：head `9aad0347972a` 实证（7 文件 +1588/-18 全 Camofox 域）→ ack [5658001073](https://github.com/NousResearch/hermes-agent/pull/109066#issuecomment-5658001073)
- **mrkillbob × 36**（同一话术批量请求 review 自有老 PR #91414-#102874，指定 AI review、不走 Codex）：实测 36 个全不满足默认门槛（人人有评论；19 个已有我们 AI review；10 个人类/bot review 在途；1 个 draft）→ **用户决策：全量重审（过滤 draft + 人类 review 在途）**
  - review 作者鉴别：andrexibiza 人类在途 5 个（93182×6、94079×3、95850×5、97368×2、99351×4）→ 排除；mrkillbobbot 自有 bot 5 个 → 不拦；draft 101552 → 排除
  - **实审 30 个**，见下一批

## 其余 203 条

- **mention 其余：** 92590 pt-BR 求 maintainer（非定向）、102840 teknium1 落地致谢（已关）、109080 作者自述、92616/92661 DavidMetcalfe 系、84624/84409/93756/85943/105555/105696 无实体 → 信息性
- **第三方 25 条（非定向）：** teknium1 落地/转交系（102840/86980/90668/85094）、独立验证群（83509/83520/87199/96533/90199/83954/98612/91220/83436/101523/93897/86351）、AI triage 重复注记 5 条（109300/109098/109305/109021/109037 系，与我们实发 findings 互证）、求助 2 条 → 社区自洽
- **迟到 1 条：** 67667 vidarak 自更新（无 @me）→ 只标 Done
- **其余：** 作者自更新/已关收尾（enzo-adami×5、oferlaor 系、ayushnangia 系、jeeves 系等），订阅噪音

## 处置

- 241/241 标 Done，失败 0，收件箱归零；2 条实质 @me 已回评闭环

---

# 第一百三十一批 · 2026-09-14 特战（mk36 重审 30 个）→ 6 实发 + 24 简短干净回复

**背景：** mrkillbob 同一话术 @Enough1122 点名要 AI review 自有 36 个老 PR（指定不走 Codex）。**用户决策：全量重审（过滤 draft + 人类 review 在途）**；同时立新规（@-REQUEST RULE 2026-09-14，已写入 `state.rule`）：**被 @ 点名的 review 无论有无问题都要回复**（干净发极简一句；例行批量战役维持只发有问题）。

**过滤：** andrexibiza 人类在途 5 个（93182/94079/95850/97368/99351）+ draft 101552 → 排除；mrkillbobbot 自有 bot 不拦。**实审 30 个**（91414..97370 × 15，97866..102874 × 15），2 路并行；diff 全收（含 12 个>60KB、最大 1.4MB 走 files 分页，100240 diff 406 走 files 分页）。

**执行：** 2 路子代理（审当前 head + head 交叉证伪 + 干净极简回复；禁全目录清理；自对账 2/2 通过）：
- chunk1 15/15 全回复（3 findings：91414 guarded mode 永不激活 blocking、93785 非法值抛错路径、97370 egress provider label 绕过；12 干净）
- chunk2 15/15 全回复（3 findings：100681 快照成功误报 + inode 回归、97869 fcntl 破 Windows、97870 subject 编码碰撞；12 干净；429 自退避 1 次）

**结果：** **posted 30 / skipped 0**（其中 findings 6、干净简短回复 24），URL 精确核验 30/30（旧 review 不干扰计数），`dups` 无新增。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3514→3519`（97370 已在列，只 +5）、`reviewed_clean` 774→798（24 个计入，避免下轮重复捡起；备注：本次按 @-request 规则发了简短回复）、frontier/max 不动（老号段）。

## 待跟进（更新）

- 批量累计实发 **3519 条**（+798 clean，前含 24 个 @-request 简短回复），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百三十二批 · 2026-09-14 续战（109514-110477）→ 13 实发 + 283 静默 + 2 跳过

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 480→480（已过滤，最新 #110477）→ 活检筛 **298**（历史最大；skip 182：comments 134 / reviews 35 / draft 9 / closed 4，0 error；480 量太大超时一次，改 checkpoint 续跑）→ diff 全收（16 个>60KB，最大 391KB，无 406），10 路并行（30×9 + 28；两波 5+5 错峰）。

**执行：** 10 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 10/10 通过；禁全目录清理）：
- 第一波：chunk1 3/30（109660 脚本语法错、109666 无界事件、109636 私钥漏拦）、chunk2 0/30（187KB 审完）、chunk3 0/30、chunk4 3/30（109859 slot 撞 index、109861 SSRF 八进制绕过 +inet_aton 实测、109864 repair 删 live）、chunk5 0/30
- 第二波：chunk6 0/30（283KB 审完）、chunk7 0/28+2 跳过（110130/110158 半路人类评论）、chunk8 5/30（110196/110253/110260/110266/110267）、chunk9 0/30（391KB/142KB 审完）、chunk10 2/28（110390 task_id 路径逃逸、110400 未捕获 traceback）

**结果：** **posted 13 / clean 283 / skipped 2**，合计 298 对账齐（未发全被 clean+skip 覆盖，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3519→3532`、`reviewed_clean` 798→1081、`max=110400`、`frontier=110477`。

## 待跟进（更新）

- 批量累计实发 **3532 条**（+1081 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百三十五批 · 2026-09-14 续战（110482-110786）→ 3 实发 + 106 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 206→168（已过滤，最新 #110786）→ 活检筛 **109**（skip 59：comments 55 / draft 4，0 error；checkpoint 后台跑）→ diff 全收（7 个>60KB，最大 211KB，无 406），4 路并行（28/28/28/25）。

**执行：** 4 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 4/4 通过；禁全目录清理）：
- chunk1 1/28（110508 typed 约束被 inline 路径绕过；211KB 收据逻辑无 bug）
- chunk2 0/28（169KB/158KB 重点审完；6 存疑证伪）
- chunk3 0/28（6 存疑证伪；3 边缘低影响不发）
- chunk4 2/25（110771 新列无迁移必崩、110777 allow_all 未覆 adapter 层；207KB 审完）

**结果：** **posted 3 / clean 106 / skipped 0**，合计 109 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3532→3535`、`reviewed_clean` 1081→1187、`max=110777`、`frontier=110786`。

## 待跟进（更新）

- 批量累计实发 **3535 条**（+1187 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百三十七批 · 2026-09-14 续战（110789-110864）→ 1 实发 + 27 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 239→43（已过滤，最新 #110864）→ 活检筛 **28**（skip 15：comments 14 / draft 1，0 error）→ diff 全收（无大 PR），2 路并行（14/14）。

**执行：** 2 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 2/2 通过；禁全目录清理）：
- chunk1 0/14（途中遇 429 限流，head 证伪做不了的一律不硬发，纪律正确）
- chunk2 1/14（110830 probe 失败误报 TimeoutExpired + 死代码；其余 13 证伪放行）

**结果：** **posted 1 / clean 27 / skipped 0**，合计 28 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3535→3536`、`reviewed_clean` 1187→1214、`max=110830`、`frontier=110864`。

## 待跟进（更新）

- 批量累计实发 **3536 条**（+1214 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百三十九批 · 2026-09-15 续战（110880-111399）→ 6 实发 + 106 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 490→275（已过滤，最新 #111446）→ 活检筛 **112**（skip 163：comments 156 / draft 6 / closed 1，0 error；checkpoint 后台跑）→ diff 全收（5 个>60KB，最大 339KB，无 406），4 路并行（28×4）。

**执行：** 4 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 4/4 通过；禁全目录清理）：
- chunk1 2/28（110907 短值误脱敏、110918 平台裸串 fail-open；262KB 审完）
- chunk2 3/28（110988 lease 尾部 wipe、111035 无锁杀 ticker、111098 fenced 改写 + 本地复现）
- chunk3 1/28（111156 无 brew 必失败；292KB/339KB 逐项证伪）
- chunk4 0/28（2 存疑证伪）

**结果：** **posted 6 / clean 106 / skipped 0**，合计 112 对账齐（clean 覆盖全部未发，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3536→3542`、`reviewed_clean` 1214→1320、`max=111156`、`frontier=111399`（111400+ 下轮重捡）。

## 待跟进（更新）

- 批量累计实发 **3542 条**（+1320 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百四十一批 · 2026-09-15 续战（111477-111711）→ 12 实发 + 75 静默 + 1 跳过

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 581→163（已过滤，最新 #111711）→ 活检筛 **88**（skip 75：comments 71 / draft 2 / reviews 1 / closed 1，0 error；checkpoint 后台跑）→ diff 全收（仅 1 个>60KB），3 路并行（30/30/28）。

**执行：** 3 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 3/3 通过；禁全目录清理）：
- chunk1 2/30（111508 无超时挂起、111555 异常漏捕）
- chunk2 1/30（111650 裸 URL 误记证据；79KB 审完）
- chunk3 9/28+1 跳过（111656/111666/111674/111675/111676/111679/111680/111696/111710；111711 半路 triage 定重跳过）

**结果：** **posted 12 / clean 75 / skipped 1**，合计 88 对账齐（未发全被 clean+skip 覆盖，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3542→3554`、`reviewed_clean` 1320→1395、`max=111710`、`frontier=111711`。

## 待跟进（更新）

- 批量累计实发 **3554 条**（+1395 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百四十三批 · 2026-09-16 续战（111714-112485）→ 13 实发 + 186 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 526→385（已过滤，最新 #112485）→ 活检筛 **199**（skip 186：comments 155 / draft 13 / reviews 5 / closed 13，0 error；checkpoint 后台跑）→ diff 全收（6 个>60KB，最大 603KB，无 406），7 路并行（28×6+31）。

**执行：** 7 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 7/7 通过；禁全目录清理；两 chunk 主动纠正 WinPS 空数组误计并复核）：
- chunk1 1/28（111796 代理绕过 wire-body cap；61KB/133KB 审完）
- chunk2 1/28（111885 `includes` 串改 remembered navigation）
- chunk3 5/28（112009 与 main 设计冲突、112013/112014 重复实现、112032/112068 与 main 已有通道冲突；528KB 审完）
- chunk4 3/28（112128 反斜杠 typo 漏报、112130 fence evasion、112165 `SyntaxError` + 编译验证）
- chunk5 1/28（112320 注释与代码顺序矛盾）
- chunk6 1/28（112404 cyclic symlink 无限递归；603KB 审完）
- chunk7 1/31（112433 `None` DB 无设防 + 跨 profile 串数据；90KB 审完）

**结果：** **posted 13 / clean 186 / skipped 0**，合计 199 对账齐（未发全被 clean 覆盖，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3554→3567`、`reviewed_clean` 1395→1581、`max=112433`、`frontier=112485`。

## 待跟进（更新）

- 批量累计实发 **3567 条**（+1581 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百四十五批 · 2026-09-16 续战（112507-112689）→ 5 实发 + 69 静默

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 457→106（已过滤，最新 #112689）→ 活检筛 **74**（skip 32：comments 17 / reviews 11 / draft 2 / closed 2；2 个 504 重试捡回，均 eligible；checkpoint 后台跑）→ diff 全收（仅 1 个>60KB），3 路并行（25/25/24）。

**执行：** 3 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 3/3 通过；禁全目录清理；null-aware 计数复核）：
- chunk1 1/25（112543 与 112542 重复实现；6 存疑证伪）
- chunk2 3/25（112565 误杀 pythonw+孤儿 tray、112621 文档与删除行为矛盾、112632/112616 同基线二选一；80KB 审完）
- chunk3 1/24（112672 每会话泄漏 AudioContext；2 次 429 冷却通过）

**结果：** **posted 5 / clean 69 / skipped 0**，合计 74 对账齐（未发全被 clean 覆盖，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3567→3572`、`reviewed_clean` 1581→1650、`max=112672`、`frontier=112689`。

## 待跟进（更新）

- 批量累计实发 **3572 条**（+1650 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百四十七批 · 2026-09-16 续战（112691-112810）→ 4 实发 + 69 静默 + 1 跳过

**口径：** 默认规则（open + 非 draft + 零评论/零 review/零内联 + 过滤 posted/clean + 编号>前沿；只发有问题的）。search 日切片去重 202→83（已过滤，最新 #112810）→ 活检筛 **74**（skip 9：comments 6 / draft 2 / reviews 1，0 error；checkpoint 后台跑）→ diff 全收（5 个>60KB，最大 193KB，无 406），3 路并行（25/25/24）。

**执行：** 3 路子代理并行（发前二次活检 + 幂等前置 + 429 退避；存疑一律 head 证伪；自对账 3/3 通过；禁全目录清理；null-aware 计数复核）：
- chunk1 3/25（112698 外部 home 绑定回归、112726 in-flight 回调被修剪、112728 删除成功误报 500；79KB 审完）
- chunk2 0/25（4 存疑证伪；68KB/79KB 审完）
- chunk3 1/24+1 跳过（112778 phase 归一化丢 rebind 信号 + head 证实；193KB/97KB 审完；112798 半路人工评论跳过）

**结果：** **posted 4 / clean 69 / skipped 1**，合计 74 对账齐（未发全被 clean+skip 覆盖，API 实发 == 结果文件，`dups={}`）；`posted_count==len(posted)` 完整性通过。

**处置：** 落盘 `drafts/_campaign/{n}.diff` 与 `Temp/opencode/campaign/{n}.md`；campaign_state.json 更新 `posted 3572→3576`、`reviewed_clean` 1650→1719、`max=112778`、`frontier=112810`。

## 待跟进（更新）

- 批量累计实发 **3576 条**（+1719 clean），等作者/maintainer 响应
- #96080 署名落地（非阻塞）

---

# 第一百四十六批 · 2026-09-16 (22 条)→ 已清零

**账号:** Enough1122 · **处理:** 22/22 标 Done（+1 回评）· **处理后未读:** 0
构成: comment 22 · 定向 @Enough1122: 1

## 定向 @Enough1122（1 条）

- #107145 KoNit-K（rebase 到当前 main，head `7dce3441`，求跟进）：新旧 diff 逐行比对，仅 blob 索引变化、hunk 内容完全一致 → 纯 rebase，早前 3 点保持关闭，干净简短回复 [5695558425](https://github.com/NousResearch/hermes-agent/pull/107145#issuecomment-5695558425)

## 其余 21 条

- **第三方 1 条（非定向）：** 92338 zhounuo528 现场确认仍未修（带精确位点）→ 社区自洽
- **其余：** 作者自更新/已关收尾（EAbaracus 关闭 6、Vocllum/Xuxyyy/hailyuzairi 关闭 3、KoNit-K 自更新 1 等），订阅噪音

## 处置

- 22/22 标 Done，失败 0，收件箱归零；1 条 @me 已回评闭环

---

# 第一百四十四批 · 2026-09-16 (88 条)→ 已清零

**账号:** Enough1122 · **处理:** 88/88 标 Done（+3 回评）· **处理后未读:** 0
构成: comment 84 + mention 4 · 定向 @Enough1122: 3

## 定向 @Enough1122（3 条，均已审 PR 作者回应求复评 → 逐个 head 实证后回复）

- #100969 Wenfengcheng（dispatcher decomposition 后重基，head `2e1d71c6`）：改动迁入 `kanban_db_dispatch.py:1997-2025`，`no_default_assignee` 取自 resolve 前原始输入，dry_run 短路不变 → 干净简短回复 [5693681448](https://github.com/NousResearch/hermes-agent/pull/100969#issuecomment-5693681448)
- #110771 Wenfengcheng（legacy-store 兼容性质疑，head `b90f69a9`）：head 源码双实锤——`SCHEMA_SQL` 已声明该列（`hermes_state_common.py:400`），`_init_schema` 通用 reconciler（`:881-900`）且写入打开路径必调，早前迁移点关闭 → 干净简短回复 [5693683161](https://github.com/NousResearch/hermes-agent/pull/110771#issuecomment-5693683161)
- #107145 KoNit-K（三处 leftover caller 已穿透 store 语义，head `6713d31b`）：adapter/undo/handoff 全走 `include_telegram_dm_thread_via_store` + fanout-adoption，新测试钉住三路 key 一致，早前 3 点全闭 → 干净简短回复 [5693684808](https://github.com/NousResearch/hermes-agent/pull/107145#issuecomment-5693684808)

## 其余 85 条

- **mention 1 条：** 92122 无实体、96891 SmelterLabs 已关自述 → 信息性
- **第三方 10 条（非定向）：** teknium1 落地 5 条（97351/91206/86345/85372/111696 系）、独立验证群（84045 B1nary0perator、87463 benxutech 真机、103703 rybalkaie、96220 KeyArgo、105968 NanamiMio）→ 社区自洽
- **其余：** 作者自更新/已关收尾（kshitijk4poor×9、jonpol01×7、33hodl×7、teknium1 系 salvage、KoNit-K 关闭 3 等），订阅噪音

## 处置

- 88/88 标 Done，失败 0，收件箱归零；3 条 @me 已回评闭环

---

# 第一百四十二批 · 2026-09-16 (154 条)→ 已清零

**账号:** Enough1122 · **处理:** 154/154 标 Done · **处理后未读:** 0
构成: comment 146 + mention 8 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 8 条：** 92122/95359/87274/105000/85428 无实体、87367 majordave 自更新（WSL2 定重说明，已关）、93007 AlexJiaJun 真机反馈、91078 CN-42 独立复现+补丁缺口 → 均非定向，信息性
- **第三方 16 条（非定向）：** 独立复现/验证群（104486 fyxs、91981 0xFastly、84202 Chalars1011、103182 CTCycle、90246 ccccyk0919、91078 CN-42、93007 AlexJiaJun 系）、感谢/跟进（83954 JaimeMarques、103796 fmercurio、101759 ahrazzle 转队列）、AI 起草部署报告（105968 NanamiMio）、teknium1 落地 2 条 → 社区自洽
- **其余：** 作者自更新/已关收尾/已合并收尾（teknium1 合并 15、Christopher-Schulze×20、33hodl×7、djagya×7、kyssta-exe 关闭 3 等），订阅噪音

## 处置

- 154/154 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百四十批 · 2026-09-15 (56 条)→ 已清零

**账号:** Enough1122 · **处理:** 56/56 标 Done · **处理后未读:** 0
构成: comment 53 + mention 3 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention 3 条：** 18188/72638 无实体、105503 ostravajih 求 teknium1/OutThisLife（非定向）→ 信息性
- **第三方 10 条（非定向）：** 独立验证群（85197/88538/101876/105023/86233 系）、kshitijk4poor 落地 3 条、alt-glitch triage 2 条 → 社区自洽
- **其余：** 作者自更新/已关收尾（teknium1 系 salvage×10、33hodl×3、Diaspar4u×3 等），订阅噪音

## 处置

- 56/56 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百三十八批 · 2026-09-15 (182 条 + 迟到 6 条)→ 已清零

**账号:** Enough1122 · **处理:** 188/188 标 Done（+2 回评）· **处理后未读:** 0
构成: comment 173 + mention 18（+迟到 6；中途重启一次，DELETE 幂等重跑）· 定向 @Enough1122: 3

## 定向 @Enough1122（3 条）

- #96720 druyang（冲突已解，求复评）：head `61d7539a8770` 增量复评（4 文件 +74/-2，守卫位置不变，新测试钉住 preserve 行为，早前点已闭）→ 干净简短回复 [5673251058](https://github.com/NousResearch/hermes-agent/pull/96720#issuecomment-5673251058)
- #86940 x7peeps（CI 诊断：5 项已修但又 CONFLICTING）：`mergeable=False` API 实证 → 回复等 rebase 后再整遍 [5673251295](https://github.com/NousResearch/hermes-agent/pull/86940#issuecomment-5673251295)
- #89992 100yenadmin（关闭致谢）→ 致谢类，无需回评

## 其余 185 条

- **mention 15 条：** kvnloo cross-link 群（非定向）、MrTheSoulz×2 重基说明、DavidMetcalfe/ostravajih/seb-almeida 重基说明、trevornk/ayushnangia 已关总结、无实体 2 条 → 信息性
- **第三方 45 条（非定向）：** kvnloo cross-link 22、100yenadmin 独立验证 5、teknium1 落地 3、CI bot 2、独立验证群（103928/89996/103112/89145/105610 等）、andrexibiza/jehowe 等 → 社区自洽
- **迟到 6 条（无 @me）：** 91928/51334 最新是我们旧评、98616 下游确认、105836 kvnloo 注记、102256 独立复现、109113 作者自更新 → 只标 Done
- **其余：** 作者自更新/已关收尾/teknium1 系 salvage（liuhao1024×6、Adolanium×12、KoNit-K×7、jonpol01×7 等），订阅噪音

## 处置

- 188/188 标 Done（含重启前已删部分，失败 0，收件箱归零；1 条闪断重试成功）；2 条实质 @me 已回评闭环

---

# 第一百三十六批 · 2026-09-14 (13 条)→ 已清零

**账号:** Enough1122 · **处理:** 13/13 标 Done · **处理后未读:** 0
构成: comment 13 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention: 0 条**
- **第三方 1 条（非定向）：** 105968 NanamiMio AI 起草的部署问题报告 → 社区自洽
- **其余：** 作者自更新/已关收尾/已合并收尾（kyssta-exe 关闭 3、liuhao1024 关闭 2、teknium1 合并 1 等），订阅噪音

## 处置

- 13/13 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百三十四批 · 2026-09-14 (23 条)→ 已清零

**账号:** Enough1122 · **处理:** 23/23 标 Done · **处理后未读:** 0
构成: comment 23 · 定向 @Enough1122: 0

## 明细

- **@me: 0 条**（无需回评）
- **mention: 0 条**
- **第三方 1 条（非定向）：** 102501 chenwei791129 现场报告支撑 → 社区自洽
- **其余：** 作者自更新/已关收尾（bunnyfu×3、lepetitprince716-prog×4、Vocllum×2、vKongv×2 等），订阅噪音

## 处置

- 23/23 标 Done，失败 0，收件箱归零；无需回评

---

# 第一百三十三批 · 2026-09-14 (70 条)→ 已清零

**账号:** Enough1122 · **处理:** 70/70 标 Done（+3 回评）· **处理后未读:** 0
构成: comment 66 + mention 4 · 定向 @Enough1122: 3

## 定向 @Enough1122（3 条，均 bbasketballer75 同一话术 check-in）→ 逐个 head 实证后回复

- #91218 MiniMax 定价（head `de080f63e2bc`）：Decimal 既有导入 + M3 `_snap` 行落地，两点全闭 → 确认无阻塞 [5661372590](https://github.com/NousResearch/hermes-agent/pull/91218#issuecomment-5661372590)
- #91186 taskkill 升级（head `42e634a5d4ec`）：升级路径 `status.py:270` 只捕 `FileNotFoundError`，`TimeoutExpired` 仍裸奔 → 剩这 1 项在作者侧 [5661372853](https://github.com/NousResearch/hermes-agent/pull/91186#issuecomment-5661372853)
- #94413 Docker 路径翻译（head `5a4c74069721`）：`PurePosixPath` 移植到位（`base.py:1071-1087`），UNC 拒绝 + `windows_only` 用例仍缺 → 2 项在作者侧 [5661373102](https://github.com/NousResearch/hermes-agent/pull/94413#issuecomment-5661373102)

## 其余 67 条

- **mention 1 条：** 98603 已关 stacked 说明 → 信息性
- **第三方 6 条（非定向）：** teknium1 落地 3 条（104758/95162/100557 系）、独立验证 3 条（105141/95475/99527 系）→ 社区自洽
- **其余：** 作者自更新/已关收尾/已合并收尾（teknium1 合并 9、holny×4、33hodl×4、fangliquanflq×3 等），订阅噪音

## 处置

- 70/70 标 Done，失败 0，收件箱归零；3 条 @me 已回评闭环
