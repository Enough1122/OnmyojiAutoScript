# 第21批 · 2026-09-21（收件箱 94 条 → 已清零）

**账号:** Enough1122 · **处理:** 94/94 标 Done（8 线程级 DELETE + 集合级 PUT /notifications）· **处理后未读:** 0 · **失败:** 0

构成: comment 78 + mention 15 + author 1 · 仓库: NousResearch/hermes-agent 92 + ANG-Ventures/hermes-agent 2 · ours: 0

## 🎯 复审回复（2 条，均已实证核验后回评）

| PR | 作者 | 我方原意见 | 复审结论 | 回评 |
|---|---|---|---|---|
| #117299 | Kyzcreig | 4 non-blocking：retry 不吃持久化 backoff / backoff gate 未按 fingerprint 作用域 / 失败的 drift check 未节流 / 测试元组断言永真 + minor（policy 未 gate） | ✅ 全部已修（head `800acae4` 逐条核：`adapter.py:2096` max(retry_after_until, backoff_until)、`:2018` gate 带 fingerprint、`:2175` except 路径补 stamp、`:2198` policy gate、测试 `test_discord_command_sync_recovery.py:339` 已 armed）；另修了 retry/reconnect 竞态的 lock 串行化 | [5754103292](https://github.com/NousResearch/hermes-agent/pull/117299#issuecomment-5754103292) |
| #116827 | DavidMetcalfe | 2 non-blocking：dedup key 在 create_at 缺失时坍缩 / allowlist 大小写不对称 | ⚖️ 作者带证据反驳 → 实核 mattermost/mattermost master：`Reaction.IsValid()` 拒绝 `CreateAt == 0`、`SaveReactionForPost` 保存前强制 lowercase → 两条均撤回，无残留 | [5754104290](https://github.com/NousResearch/hermes-agent/pull/116827#issuecomment-5754104290) |

## 列请用户定夺

无。

## 其余（静默归档 7 条 pending + 85 条噪音）

- **86578 / 86612 / 87302**（kuehnberger）：提供给维护者的人类复核 follow-up（@teknium1 等），对我们只是叙述性提及 + 后续 rebase 说明 → 修复告知类，不回。
- **96852**（JaimeMarques）：`plugin-source` helper 收口（8e2e5169e7）说明 —— 历史批次已判"确认类，无需回评"（见 `_inbox_report_2026-08-27.md`），本次沿用，不回。
- **105537**（DavidMetcalfe）：我方两个 confirm-ask 的答复（COALESCE 顺序 + 无双计），作者声明"confirm-ask, no code change"；线程后续为他人讨论 → 确认类，不回。
- **117302 / 117359**（liuhao1024）：纯致谢（其修复已被上游 cherry-pick 落 main：117630 / 117591）→ 不回。
- 其余 ~85 条：第三方讨论、CI/推送回声、他人 AI 复评、作者自更新、我方 issue 自通知 → 批量清零。
- **ANG-Ventures/hermes-agent** #775 / #777（Kyzcreig 移植 #117299 的 review 修复 + 断言 AST gate）：第三方仓库的移植性 PR，非指向我们的复核请求 → 信息性，不回。

## 处置

- 线程级 DELETE 8 条（86578/86612/87302/96852/105537/116827/117302/117359）+ 集合级 PUT 清零 → 读回 unread = **0**。
- 复审回复 2 条已读回确认（作者、正文、时间戳均正确）。

## 待跟进

- #116827：无（两条已撤）。
- #117299：作者自报的遗留项（其它三处元组断言 + lint gate）为其自跟踪工作，无需我们跟进。
- 94111/100626 等旧信息性线程：维持归档。

---

# 第22批 · 2026-09-21（收件箱 72 条 → 已清零）

**账号:** Enough1122 · **处理:** 72/72 标 Done（5 线程级 DELETE + 集合级 PUT /notifications）· **处理后未读:** 0 · **失败:** 0

构成: comment 65 + mention 6 + author 1 · 仓库: NousResearch/hermes-agent 70 + ANG-Ventures/hermes-agent 2 · ours: 0

## 🎯 复审回复（2 条，均已实证核验后回评）

| PR | 作者 | 我方原意见 | 复审结论 | 回评 |
|---|---|---|---|---|
| #117714 | Halldrix | 1 blocker 级测试缺陷（deliberate-switch 测试 stub 嵌套错层）+ docstring 与实现不符 + fail-open 无日志 + batch overlap 提示 | ✅ head `8848dc14` 逐条核验:stub 已改 `{"fallback": {...}}` 嵌套（`test_fallback_route_gate.py:131`，作者另实证回退 predicate 会 2 处失败，静态结构吻合）；docstring 改"config key under the fallback: block"（`fallback_route_gate.py:9`）；except 补 debug 日志（`:75`）。两个 deliberate non-take 论证成立 | [5758143181](https://github.com/NousResearch/hermes-agent/pull/117714#issuecomment-5758143181) |
| #94391 | Sahilvishnaliya | 3 条建议（non-ASCII 断言 / .vbs 读者排查 / 字节序钉死 utf-16-le）| ✅ head `a5123a78` 逐条核验:测试断言 `"hömè-höme" in task_text`（`test_gateway_windows.py:353`）；双写入点 utf-16-le+显式 BOM（`gateway_windows.py:583/:725`）；单 BOM 断言防回退。另核 KoeQi67 数据点:update 路径 `update_cmd_windows.py:1110` 走同一 `_write_task_script`，本 PR 落地后 update 不再回退编码 | [5758146086](https://github.com/NousResearch/hermes-agent/pull/94391#issuecomment-5758146086) |

## 列请用户定夺

无。

## 其余（静默归档 ~67 条）

- **作者修复告知（无 @，~20 条）**：tobenwarrior 系（#115188/#116399/#116409/#116422/#117724/#117730）、jonpol01 #117399、strzhao #116185、yingliang-zhang #117244、fangliquanflq #117538/#117637/#117728、liuhao1024 #117671/#117549、execsumo #112404、a692570 #117613、jbbottoms #117720、omid-io #116090、youyoutu405-source #115081、TaoMasterCoder #114751、sfire123 #85901、kokhlo #117908（author）——均"confirmed/fixed in <sha>"式告知，无 @ 无提问 → 克制发声口径不回。
- **closed-PR 补充 "What does this PR do?" 描述**（#117674/#117408/#117388/#117537/#117525/#117286/#117533/#103354/#117380/#113102/#89021）：作者补模板描述，无 @ → 不回。
- **33hodl 8 条**（#86048 等）：无正文推送事件 → 噪音。
- **ANG-Ventures #775/#777**（Kyzcreig）：#117299 修复向 fork 的移植 PR，信息性 → 不回（沿用第21批口径）。
- **#92122**（kvnloo）：exact-head "KEEP/PICK-ONE" 三方分诊贴 → 非指向我们 → 不回。
- **#96990**（KeyArgo）向维护者催进度、**#104086**（dacheah）第三方独立验证、**#89871**（specetator）workflow 过期自述、**#83911**（teknium1）salvage 播报、其余推送/CI 回声 → 批量清零。

## 处置

- 线程级 DELETE 5 条（117714/94391/92122/ANG 775/777）+ 集合级 PUT 清零 → 读回 unread = **0**。
- 复审回复 2 条已读回确认（POSTED + 链接有效）；归档 rb/117714.md 追加 + rb/94391.md 新建，progress.txt 记 followup×2。

## 待跟进

- 无新增阻塞。batch26 审阅流水线停在派单前（diff+预检就绪，22 条 PR #117740-#117778），待 Hermes 通道续跑。

# 第23批 · 2026-09-21（3 条）→ 已清零
**账号:** Enough1122 · **处理:** 3/3 标 Done · **处理后未读:** 0
构成: comment 3 + mention 0 · 复审回复: 0 · 静默跳过: 0 · 列请示: 0

## 其余
- #116090(omid-io,已关):作者关帖转投 #116710 从读侧解决,致谢 teknium1——纯关闭摘要,我方 09-20 评语已归档,无需动作。
- #61305(AndreasG78):第三方 deathlord911 附议我方 08-15 review 的 Origin/Referer 检查,并补充 SameSite=Lax 对 sibling-site 不设防的论据——非 @ 定向、作者未动,静默清。
- #106544(KoNit-K):作者 09-19 自更新称已保留我方评审过的 full-mode 不变量(1a2202de20),未 @;另一条为旁观者催合并。静默清。

## 处置
Done 3/3,失败 0。sweep 对三类均 unclassified-keep,按 SOP 手动 gh api -X DELETE 逐线程清理(踩了一次前导斜杠改写,去掉后成功)。

## 待跟进
无新增。#106544 作者有实质跟进(保留 full-mode 不变量),如后续 @ 触发再走 §1.3 复核。
