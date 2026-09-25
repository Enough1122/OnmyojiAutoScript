# 第5批 · 2026-09-25（50 条）→ 已清零
**账号:** Enough1122 · **处理:** 50/50 标 Done · **处理后未读:** 0
构成: comment 46 + mention 4 + author 1（另有 mention 4 条重复计入）· 复审回复: 4 · 静默跳过: 46 · 列请示: 0

## 🎯 复审回复（4 条，均 @ 触发 + 实证核验）

1. **#66280** fix(telegram): live locations in background（michaelmwu）— head `75ee804f55`
   - 两点 follow-up 均落实 ✓：body 已更正 30s TTL 说法；`gateway/config_loader.py` 的优先级改动已移除，只剩只读 helper，唯一消费者是 Telegram legacy-extra 桥且规则收窄（platform section 未显式给值才回退）。
   - 遗留：`mergeable_state=dirty`，需 rebase。
   - 回评:https://github.com/NousResearch/hermes-agent/pull/66280#issuecomment-5825860326

2. **#93344** fix(mcp-oauth): refresh before browser auth（Elliot-Construct）— **maintainer 点名要求解释测试覆盖分歧**
   - 实跑 PR head `3accb6f8db`：`test_refresh_on_401_with_valid_refresh_token` **FAILED** —— `tests/tools/test_mcp_oauth.py:1180` 断言 `mock_add_auth.await_count == 1`，而 `_add_auth_header` 在 mcp 2.0.0（仓库 pin）与 1.28.1 中都是 **sync**，`patch.object` 产出 MagicMock，`.await_count` 是 MagicMock，断言恒假。
   - 另一个新测试同样 FAILED（SDK lock RuntimeError）。两测试都 patch 掉 `_refresh_token`/`_handle_refresh_response`，只驱动分发。
   - 结论：生产改动无问题，缺口是新路径没有能通过的测试。
   - 回评:https://github.com/NousResearch/hermes-agent/pull/93344#issuecomment-5825861732

3. **#117452** fix: tolerant memory entry matching（crouching-tiger-hidden-whale）
   - 作者称三处已修，**但 head `1829dd10b0` 的 diff 与 09-21 评审时完全一致**（改动只在 temp clone）→ 无可核验内容，已请其推送 + rebase。三条方案本身正确。
   - 回评:https://github.com/NousResearch/hermes-agent/pull/117452#issuecomment-5825863074

4. **#91984**（**我方 PR**，operator attribution + dashboard assign dry-run）— benperry6 指出 stale-probe 守卫残留竞态
   - **结构核实成立**：探针是裸 SELECT（`_board_conn` 无事务），`assign_task` 才 `BEGIN IMMEDIATE`（`hermes_cli/kanban_db.py:3044`）重读且**从不复查 `expect`** → 两读之间的提交被静默覆盖，承诺的 409 不触发；reassign 同形。
   - 修复方向已回评（`expect` 传进 `assign_task`/`reassign_task`，事务内比对或条件 UPDATE + 确定性测试）。
   - ⚠️ **修复尚未实现，待用户定**（本机实现 or 走 Hermes 通道）。
   - 回评:https://github.com/NousResearch/hermes-agent/pull/91984#issuecomment-5825864382

## 其余（46 条静默跳过）
- **已关/被取代收尾 2 条**:#87206（被 #122039 取代，OutThisLife 明言「用了你的 root cause」）、#92639（被 #122000 取代，诊断与代码均被 credit）——DavidMetcalfe 的逐点答辩无需再回，线程已关。
- **致谢/收条 2 条**:#97344（rodrigogs 收尾致谢，我方 retraction 已闭环）、#99992（DevEverything01 致谢 + 接受非阻塞 note）。
- **第三方记录性发言 1 条**:#92159（andyst-dev 说明与 #92078 的重叠，无提问）。
- **其余 41 条**：作者自更新、CI/播报、无正文推送、第三方讨论等纯告知类，未逐条留痕。

## 处置
`scan_pending_mentions` 先行 ✓（8 条 pending @，逐条判定）→ 4 条实核后回评 → 集合级 `PUT /notifications` 清零 → `gh_inbox.py` 确认 = **0**。归档：`reviews/hermes-agent-2026W38/rb/{66280,93344,117452,91984}.md`（117452 为追加）。

---

# 第6批 · 2026-09-25（1 条）→ 已清零
**账号:** Enough1122 · **处理:** 1/1 标 Done · **处理后未读:** 0
构成: comment 1 · 复审回复: 0 · 静默跳过: 1 · 列请示: 0

## 其余（1 条静默跳过）
- **#105871** chore(ci): remove publish-e2e-evidence pipeline（ethernet8023）— 线程已 **merged**。
  触发通知的是 PR **正文**（`latest_comment_url` 指向 body，非真人评论）；线程内仅两条：我方 09-08 的
  AI review（当时已发）与 09-12 CI bot 播报。**已知盲区已人工补查**：`/pulls/105871/reviews` 仅
  andrexibiza 一条 COMMENTED review（讨论 0-job recovery 路径不该改 PR 生命周期），**未点名我**。
  无待回内容 → 标 Done。

## 处置
`scan_pending_mentions` 先行 ✓（0 pending）→ 人工补查 review 正文（SOP §1.1 已知盲区）→ 线程级
`gh api -X DELETE notifications/threads/25547977605` → `gh_inbox.py` 确认 = **0**。

## 待跟进
- 🔴 **#91984 竞态修复待办**：回评已承诺推 follow-up，代码未动。需用户定执行方（本机 Claude Code / Hermes 通道）。
- **#117452** 等作者推送三处修复；**#66280** 等作者 rebase（dirty）。
- 延续：batch26 剩 19 条搁置，续跑通道未定（待用户定）；#65982 卡 maintainer 侧；cc-switch #7382 维护者 defer 继续挂起。
- 环境备注：本机 `mcp` 实装 1.28.1，仓库 pin `mcp==2.0.0`；核 93344 时已用 wheel 复核 2.0.0 签名（结论一致），后续核 mcp 相关 PR 需注意版本差。

---

# PR 批次27 · 2026-09-25（10 条）
**范围:** frontier `118225` → `118258`

- **CLEAN 静默归档 6 条:** #118226、#118227、#118232、#118252、#118253、#118258
- **已有讨论/重复，跳过 3 条:** #118238（2 comments）、#118248（1 comment）、#118255（GitHub `duplicate` 标签）
- **发现真实问题 1 条:** #118249 — `workspace` 可选但公共消费边界未传 session cwd，导致合法 `workspace_mutation` 报告被静默丢弃；草稿已落盘 `reviews/hermes-agent-2026W38/rb/118249.md`
- **发帖状态:** #118249 暂未发出；`post_one.py` / GitHub API 返回 403（本地 `GITHUB_TOKEN` 无效/触发限流），未绕过认证或重复尝试。已记入 `_campaign_state.json.pending_post=[118249]`。

**判定口径:** 已有任何 issue comment / review / inline comment 的 PR 直接跳过；本批仅对实证功能缺口准备回复，其余不发帖。

---

# PR 批次28 · 2026-09-25（10 条）
**范围:** frontier `118258` → `118294`

- **CLEAN 静默归档 5 条:** #118261、#118266、#118268、#118274、#118283
- **已有讨论，跳过 2 条:** #118278（2 comments）、#118281（1 comment）
- **超战役文件上限，留 deferred 1 条:** #118294（36 files）
- **发现真实问题 2 条:** #118264（硬编码作者机器路径 + `git add -A` 自动提交无关改动）；#118290（review 预检绕过隔离边界，且 `sqlite3.Error` 过宽）
- **发帖状态:** #118264、#118290 草稿已落盘；与上一批 #118249 一并暂存 `_campaign_state.json.pending_post`，待 GitHub 写认证恢复后发送。

---

# PR 批次29 · 2026-09-25（10 条）
**范围:** frontier `118294` → `118325`

- **CLEAN 静默归档 4 条:** #118298、#118302、#118307、#118309
- **已有讨论，跳过 3 条:** #118296、#118317、#118325
- **超战役文件上限，留 deferred 1 条:** #118314（29 files）
- **发现真实问题 2 条:** #118306（非有限 `failure_streak` 仍可能抛 `OverflowError`）；#118315（只在 Honcho 初始 `top_k` 页面内重排，无法找回未返回的相关结论）
- **发帖状态:** #118306、#118315 草稿已落盘；当前 pending 共 5 条（#118249、#118264、#118290、#118306、#118315），待 GitHub 写认证恢复后发送。

---

## 今日收尾
- 用户要求今天先停在这里；未启动下一批 PR review。
- 当前 frontier 保持 `118325`。下次从 `118325` 之后继续，并先处理 5 条已验证的 pending-post 草稿。
- 停止原因仅为用户收工，不是审查阻塞；GitHub 写认证/限流恢复后再发送，避免重复或误发。

---

## 恢复与补发
- GitHub 写认证恢复后，已按草稿原样补发 5 条，未重复发送：
  - #118249: https://github.com/NousResearch/hermes-agent/pull/118249#issuecomment-5827015776
  - #118264: https://github.com/NousResearch/hermes-agent/pull/118264#issuecomment-5827017614
  - #118290: https://github.com/NousResearch/hermes-agent/pull/118290#issuecomment-5827019727
  - #118306: https://github.com/NousResearch/hermes-agent/pull/118306#issuecomment-5827021763
  - #118315: https://github.com/NousResearch/hermes-agent/pull/118315#issuecomment-5827023942
- `pending_post` 已清零；campaign frontier 仍为 `118325`，后续从其后的 PR 继续。

---

# 旧 worker 批次回收 · 2026-09-25
- deleg_49e0f7de 的 5 路结果已回收；已发布评论均经 GitHub API 读回：#122147、#122186、#122406、#122397、#122170、#122399、#122393、#122391。
- clean：#122192、#122128、#122364、#122371、#122383、#122157、#122156、#122153、#122149、#122191、#122162、#122150、#122144、#122403、#122193、#122405、#122189、#122184、#122165、#122163、#122152、#122145。
- deferred：#122387（72 files）、#122389（旧 worker 误领后未审，已重新排队）。
- worker-6 退出时领取的 #122346 已由后续 worker 接管并结案为 clean。
- 发现 10 条已发布 PR 的 head 在评论后变化，已按当前 head 重新排队复审；旧评论不等于当前 diff 已审。
- 当前持续池：10 个存活 worker；无固定条数上限，处理期间原子 heartbeat；队列仍有余量。

---

# GitHub Inbox follow-up · 2026-09-25
**账号:** Enough1122 · **初始未读:** 41 · **复审回复:** 4 · **静默归档:** 37 · **处理后未读:** 0
构成: comment 36 + mention 5；pending @ 扫出 5 条，其中 #87264 为明确的 “informational only; no change required”，不回；formal review 补扫 41 线程，无正文 @ 漏项。

## 复审回复（均已读回当前 head 实证并核验评论）
1. #113192 — 作者修复 `_new_reply` 异常时 quote 释放、sender fallback 有限淘汰；head `7990746...` 核验通过。  
   https://github.com/NousResearch/hermes-agent/pull/113192#issuecomment-5830453396
2. #122246 — Traditional Chinese aliases 不再强制映射到 `cmn-Hans-CN`，改为省略 `language_codes`；head `1057a368...` 核验通过。  
   https://github.com/NousResearch/hermes-agent/pull/122246#issuecomment-5830453394
3. #122392 — 确认 #121608 是剩余 agent 路径的 complementary carrier；按 `AGENTS.md` 撤回 source-literal test 建议；head `eae24848...` 核验通过。  
   https://github.com/NousResearch/hermes-agent/pull/122392#issuecomment-5830453489
4. #122396 — 修复真实 `ExecStop`→`SIGTERM`→persist 路径的 restart marker 写入；head `a063575...` 核验通过，30 分钟 stop→manual-start 边界为已披露非阻塞项。  
   https://github.com/NousResearch/hermes-agent/pull/122396#issuecomment-5830453420

## 静默归档
- #87264：作者最终 disposition 明确 informational only / no change required；不回。
- 其余 36 条：作者更新、CI 播报、第三方讨论、已关闭/合并收尾或无待回复内容；未逐一发帖。

## 处置
- `scan_pending_mentions.py` 在清理前完成；formal review 盲区补扫完成。
- 4 条回评均用 `post_followup.py` 发布并通过 `gh api repos/.../issues/comments/<id>` 读回，用户身份为 `Enough1122`。
- `gh api -X PUT notifications` 清空通知；随后 `gh api notifications --paginate -q length` 读回 **0**。
- 归档：`reviews/hermes-agent-2026W38/rb/{113192,122246,122392,122396}.md`；进度账本已追加 4 行 follow-up。

---

# GitHub Inbox follow-up · 2026-09-25（18:28）
**账号:** Enough1122 · **初始未读:** 2 · **复审回复:** 1 · **静默归档:** 1 · **处理后未读:** 0
构成: comment 2；pending @ 扫出 0 条。formal review 补扫无正文 @ 漏项。

## 复审回复
1. #122381 — 当前 head `7916f6e...` 实证确认 `mutable_tools_filter()` 修复了 `hermes mcp configure` 的 shorthand 写入崩溃，并统一到 checklist / enable-disable 路径。  
   https://github.com/NousResearch/hermes-agent/pull/122381#issuecomment-5830903475

## 静默归档
- #105968：作者仅报告 rebase、冲突处理、凭据写入迁移与测试通过；没有点名、提问或待裁决内容，不回。

## 处置
- 清理前先跑 `scan_pending_mentions.py`，二次扫描仍为 0 pending。
- 回评通过 `post_followup.py` 发布，并用 `gh api` 读回，作者为 `Enough1122`。
- `gh api -X PUT notifications` 清空；随后 `gh api notifications --paginate -q length` = **0**。
- 归档：`reviews/hermes-agent-2026W38/rb/122381.md`；进度账本已追加 `122381 follow-up`。

---

# Hermes 更新后恢复审计 · 2026-09-25

- 更新中断后释放旧 running claim，重铺持续 worker；durable SQLite 保持 queued/running/head 漂移的唯一实时权威，`_campaign_state.json` 仅保留历史汇总。
- 逐条 REST 审计发现 4 条已 posted PR 评论后 head 变化：#121785、#122141、#122381、#122391。旧评论仅作语义对照；已使用 `old-head:new-head` CAS 原子回队列并写入当前 head，避免 worker 领到旧 SHA。
- 并发巡检发现 `claim` 允许同一 worker 同时持有两条 running claim，旧实例因此形成幽灵满载。根因回归测试先复现失败，再将 claim 改为幂等：同一 worker 已有未结 claim 时只续租并返回原 PR。
- 回收 4 个已确认退出/触顶 worker 的无结果 claim，补位后恢复 10 个不同 live owner、10 条 fresh claim、0 条重复 owner。
- 发布脚本审计发现 `post_batch.py` 只委托 `post_one.post()`，不会绕开发布路径；进一步补齐 `post_one.py`、`post_review.py`、`post_followup.py` 的 canonical `pull/<pr>#issuecomment-<id>`、作者和正文读回门禁。
- 清理遗留发布路径：`run_chunk3_continue.py`、`run_chunk3_99116.py`、`run_chunk4_continue.py` 均在 token/API 初始化前以 retired guard 退出；`diffs_batch115.py` 不再以 100KB 为排除门禁，超大 diff 进入 deep；`preflight_batch.py` 对未缓存 diff 返回可重试的 `diff-not-cached`，不再伪装终态 deferred。
- 最终回归：49 tests passed；核心 Python 脚本 `py_compile` 与 targeted `git diff --check`（`core.whitespace=cr-at-eol`）通过。
- 收口快照：10 个 live worker、10 个不同 owner、7 fast / 3 deep、10 条 fresh claim、0 expired；DB 为 235 clean / 74 posted / 168 queued / 10 running / 5 skip。
- posted 凭证逐条 REST 读回：74/74 均为 `https://github.com/NousResearch/hermes-agent/pull/<pr>#issuecomment-<id>`，作者 `Enough1122`、正文非空；实时 head 对账 0 漂移。

---

# 公开意见纠错与状态模型 · 2026-09-25
- 旧批次对账时发现 #122129 的原 blocker 被作者真实镜像输出与当前 head 源码共同推翻：`locked=False` 不会触发重锁；`PythonEnvironment.sync()` 的 `frozen=True` 仍保留，镜像分支实际执行 `uv sync --frozen`。URL 规范化部分则已修复。
- 已公开明确纠正并按 comment ID 读回作者、正文与 canonical URL：<https://github.com/NousResearch/hermes-agent/pull/122129#issuecomment-5832269243>。
- durable pool 新增 `corrected` 终态：与 `posted` 共用 canonical receipt 门禁，但在 metrics 中单列，不计入 posted finding；`#122129` 已从 posted 移入 corrected。
- 删除 `drafts/_pending/122129.md` 中未实证的 air-gap 相反推测，保留 `rb/122129.md` 记录撤回依据，防止后续误发。
- 同步 #122155 的有效 posted receipt、#122392 的最终 follow-up receipt；#122385 的理论边界评论已删除并转 clean。
- 回归：`52 passed in 9.12s`；`review_pool.py`、`post_one.py`、`post_review.py`、`post_followup.py` 的 `py_compile` 通过。

