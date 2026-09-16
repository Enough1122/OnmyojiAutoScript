# Inbox 战报 · 2026-08-26

**账号:** Enough1122 · **处理前未读:** 107(+处理期间新进 16,共 123)· **处理后:** 0
**快照:** `drafts/_inbox_triage.json` · 全部来自 NousResearch/hermes-agent

## 概况
- reason:comment 91 + mention 16;自己的 PR 仅 1 个(#81563,已 closed,残留致谢)
- 91 条 comment:作者自我更新 53 · teknium1 收尾 4 · 无评论实体 27 · 第三方评论 7(均不指向我)
- 噪音/信息类 105 条 + 新进 16 条全部标 Done,**无一需要逐条回复**

## 🎯 实际动作:复审 2 个 PR 并回评

### #86322 feat(a2a): per-peer custom headers(aryn-lacy)
作者 17:14Z 宣称"三点全部落实,ready for review"。**核实 head `dd23585`(4 文件)后回评:**
- ✅ nit 2(auth header 冲突静默):WARNING 日志已加,`TestAuthCollisionWarning` 双向覆盖
- ✅ nit 3(`time.sleep` 退避):sleep 处已注明 worker 线程安全性
- ❌ **nit 1(524 重试重复执行)是空头支票**:回复声称"TaskStore 按 client messageId 索引、`_prepare_task` 重放原任务、驱逐时清索引+6 个新测试",但 diff 只碰 client 侧 4 文件;main 上 `_prepare_task` 无条件 `new_task_id()`、全文 0 处 `messageId`、TaskStore 仅按 task_id 键控。文档中"Hermes peers do dedupe"的断言在 main 上**当前为假**。只落了 client 半边(`idempotency: true` 自愿声明 + 字节一致重发 + contract 注释)。回评给了两条路:(a) 本 PR 补服务端 replay guard(我的偏好);(b) 文档诚实收窄 + 另开 PR 跟踪
- 📝 顺带抓到一个陈旧注释:`_send_task` 注释称 card fetch "WITHOUT credential-bearing headers",与代码及其自家测试矛盾
- 回评:[#issuecomment-5423160342](https://github.com/NousResearch/hermes-agent/pull/86322#issuecomment-5423160342)

### #94096 fix(matrix): MAS refresh-token(Sahilvishnaliya)
作者 07:00Z 称"马上 force-push:OIDC discovery→token_endpoint 主路径 + 折入你的 nit 2/3"。**核实 head `1a73308`(08-24,force-push 未落地)后回评:**
1. MAS 路径不存在:仍只调 legacy `/_matrix/client/v3/refresh`(vlify 实测证 matrix.org MAS 拒收),无 OIDC discovery / `token_endpoint` / `MATRIX_OIDC_CLIENT_ID`
2. nit 3(刷新次数有界)未做:`_sync_loop` 两条 M_UNKNOWN_TOKEN 路径均 refresh→continue 无计数器,若令牌持续被拒会无限刷新(仅 45s sync 超时限速)
3. nit 2(dead fallback)**在新代码里原样复现**:`new_refresh = resp.get("refresh_token"); if not new_refresh: new_refresh = resp.get("refresh_token")`(同表达式,永不生效)
- 回评:[#issuecomment-5423160688](https://github.com/NousResearch/hermes-agent/pull/94096#issuecomment-5423160688) — 请作者 force-push 后 ping 我复审 nit 1 延期至 follow-up 没问题

## ℹ️ 致谢/信息类(已归档,免回复)
- teknium1:我 #81563 的 `NSLocalNetworkUsageDescription` 一行修复已带署名 cherry-pick 进 #95298 并合并("saved you the trip");同主题 issue 保留跟踪 macOS 27 半段;#95298 致谢名单有我 → 按惯例不回复
- kshitijk4poor #95342(openviking User-Agent,merged)、NeoAiLabs 在 Arch 实测佐证 jackulau desktop-entry 修复、6 位作者关闭自己 PR 的总结评论 → 信息性

## 终局
- 标 Done:123/123,失败 0;**最终未读 0**
- 发出实质回评 2 条(#86322、#94096),均指向"宣称与代码不符"的缺口
- 待跟进:#94096 作者 force-push 后会 ping 复审;#86322 等作者选 (a)/(b) 后复验

---

# 第二批(同日稍后,32 条)→ 也已清零

**账号:** Enough1122 · **处理:** 32/32 标 Done · **处理后未读:** 0
构成:comment 27 + mention 5;27 条 comment 无一 @ 我(已扫描正文)

## mention 5 条明细

1. **#86322(aryn-lacy a2a)← 重要:第三方 corroboration**
   andrexibiza 10:11Z 提交 blocking re-review(head `dd23585`),第一条 blocker 与我的回评完全一致——"The claimed Hermes idempotency contract still does not exist",并明确署名 **"Credit to @Enough1122 for catching the docs/tree mismatch on this head"**。作者此前(08-25 21:43Z)还吃了 andrexibiza 旧 head `13bb676b` 的三个 blocker。现在两位 reviewer 在 nit 1 上立场一致,作者压力到位 → 免回复,等作者动作。
2. **#86062(Christopher-Schulze,FTS corrupt index 恢复)**
   10:51Z "Thanks both — rebased onto current main,probe-cost concern fully adopted":采纳了我/strzhao 的 per-open integrity-check 开销关切(`fts_integrity_engine` 一次性探针)+ rebase 与上游 trigger-subset/跨进程 admission 语义兼容 → 可复review,免回复。
3. **#93007(dokterdok,unread session counts)**
   重浮出的是我 08-24 已答复过的线程("Nothing further from me - ready on my side"),无新内容 → 归档。
4. **#92074(ruangraung,已关)**
   teknium1 收尾:经 #95083 salvage 带署名合并;ruangraung 致谢 teknium1 → 信息性归档。
5. **#95101(andrexibiza,authority manifest S1)**
   作者自己的 exact-head 状态更新(CI 绿、S1 taxonomy 按 #95028 Part VIII 修复完成、"no code blocker found"),无指向我的提问 → 信息性归档。

## 待跟进(累计)
- #94096 等 Sahilvishnaliya force-push 后 ping 复审
- #86322 等 aryn-lacy 回应(两条 blocker:我的 replay-guard 缺口 + andrexibiza 的同题 blocker)
- #86062 可在排期允许时复验 rebase 版

---

# 第三轮:复审行动(~12:3xZ)

## #86062 复验完成 ✅([comment-5424937294](https://github.com/NousResearch/hermes-agent/pull/86062#issuecomment-5424937294))
核实 rebase 版 head `edfe0c6231`,作者 10:51Z 宣称全部成立;探针开销 marker 方案、上游语义兼容、原子恢复形状均达标。
**顺手抓到一个潜在 bug(non-blocking)**:`_legacy_fts_index_corrupt` 的 `except sqlite3.OperationalError` 分支是死代码——OperationalError 是 DatabaseError 子类却写在第二个 except,"no such table" 会先被第一个 except raise 而非按意图 continue。当前不可观测(调用点表已建),已请作者对调 except 或合并判断。

## 其余三个的状态
- #94096:head 仍 `1a73308d`,force-push **仍未落地** → 等
- #86322:head 仍 `dd23585596`,aryn-lacy 未回应双 blocker → 等
- #95101:blocker review 5026029567 是 **andrexibiza 自评自己的 PR**,不欠我复验;mention 来自参与订阅 → 不动

---

# 第四批(同日 111 条)→ 已清零

**账号:** Enough1122 · **处理:** 111/111 标 Done · **处理后未读:** 0  
构成:comment 97 + mention 14;97 条 comment 无一 @我(已扫正文,含 3 条 teknium1 收尾)

## mention 14 条明细(6 条需关注)

1. **#95418(codex-runtime, YusenZhang0601) ← 需复审** — 回应我 5 点 review,新 head `aae50f91` 声称 bare table 数据丢失等全修(#79023)。去重扫描正文含 @Enough1122,待深审(已取 diff,39094B)。
2. **#94922(web dashboard, iborazzi) ← 需复审** — 回应我 review,声称 stale base 导致的 `PUT Mutation Lock`/`_CONFIG_MUTATION_LOCK` 等回归已补,新 head `113022e`。含 @Enough1122。
3. **#86322(aryn-lacy a2a) ← 关键更新** — 作者回我+andrexibiza 双 blocker,新 head `7fe503c`(rebase `2f9e187`)声称 Blocker2(allowlist 未接入 POST)已修。待重验 Blocker1(replay guard)是否落地。
4. **#94096(matrix, Sahilvishnaliya) ← 关键更新(已验证)** — 作者兑现承诺,新 head `35a3cf70` 已取 diff 验明:legacy `/v3/refresh` 首试+M_UNKNOWN_TOKEN 时 MAS OAuth2 回退(OIDC discovery→`token_endpoint`+`MATRIX_OIDC_CLIENT_ID`),`_MAX_REFRESH_ATTEMPTS=8` 有界,dead fallback 已删,whoami/sync 双路径均接 refresh。**我早前 3 个 nit 已闭环,可放行**。
5. **#86183/#86062(FTS, strzhao)** — 告知两分支已收敛,已把 #86183 剩余增量以单 commit 叠到 #86062 rebase head 之上(`strzhao:converge/fts-integrity-hardening@1d0e7`), #86183 退役。信息性。
6. **#92730(DavidMetcalfe/MiMoHo)** — MiMoHo 第三方评论:cache 防逐出方向正确但引入跨轮回归(`completeAssistantMessage`/`failAssistantMessage` 清 pending)。非 @我,但 mention 订阅触发;属需关注的第三方加强 review。

其余 8 条 mention: #86183 状态更新、#86062 已验、`#92074`/`#95598` 归档、`#921??` 等 teknium1 campaign 跟踪信息性。

## 本轮批量 Review 战役补完(95228..95515)

- 候选 112(95228..95520 中无评论/review 的),已按旧 SOP(发后 sleep 8,跳过 sleep 3,去重 v2)分 4 批并发跑,断点前 W2/R2 通道触发内容过滤中断 3 次,剩余 17 个改本会话直审直发补完。
- 结果:W4 26 posted+2 skipped, R1 22 posted, R3 21 posted, R2 4+17 posted → **合计 90 posted**,其余 22 为他人先评/已关等 skipped。全量 diff 均 <60k 且 ≤8 文件,无超限。
- 断点已追至 **95515**, pending 归零;最新 5 个 open PR(95516..95520)中 2 个已在 W4 跳过,3 个待下一轮。

## 待跟进(累计)

- **立即复审:** #95418、#94922、#86322(重验)、#92730(MiMoHo 回归) — diff 已拉取,可马上出评论(问是否现在发)
- **94096 已闭环:** 无需再等 force-push
- **其余:** #86183 已退役, #86062 早前已验

