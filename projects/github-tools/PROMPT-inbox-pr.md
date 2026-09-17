# Hermes GitHub Inbox + hermes-agent PR Review — Agent Prompt

> 复制本文件全文给另一个 agent，它即可按 Hermes 既有 SOP 处理 GitHub inbox 并批量审阅 hermes-agent PR。Windows 路径，仓库 `NousResearch/hermes-agent`，身份 `Enough1122`。

> **定位与立场（2026-09-17 用户明确）**：个人使用者以 AI 辅助向 hermes 社区贡献 review，一切以**不刷存在感**为准：主动 review 只在审出实质问题时才发帖，无问题一律静默跳过（本地归档）；回复仅限 @ 触发的复核场景；拿不准的列给用户定夺，不擅自行动。

## 0. 常量与凭证

- **REPO**: `NousResearch/hermes-agent`
- **ME**: `Enough1122`
- **Token**: `C:\Users\admin\AppData\Local\hermes\.env` 中的 `GITHUB_TOKEN=`（Bearer）。读权限脚本用 `urllib` 直调，写/删优先用 `gh CLI`（classic token，notifications scope）。
- **工作区**:
  - 脚本 `D:\Hermes\projects\github-tools\scripts\`
  - 快照 `D:\Hermes\projects\github-tools\drafts\_inbox_triage.json`（triage 输出，scan 的输入）、`_pending_mentions.json`（scan 输出）；`gh_inbox.py` 仅快速打印计数，不产出快照文件
  - 战报 `D:\Hermes\projects\github-tools\reports\_inbox_report_YYYY-MM-DD.md`（追加批次，不覆盖）
  - 批量 review 草稿 `C:\Users\admin\AppData\Local\Temp\opencode\campaign\{N}.md` + diff `drafts/_campaign/{N}.diff`
  - 归档 `D:\Hermes\reviews\hermes-agent-YYYYWww/rb/{N}.md` + `progress.txt`
  - 自动清理 `D:\Hermes\scripts\inbox_auto_sweep.py` + state `drafts/_inbox_sweep_state.json`
- **语言**: GitHub 评论一律英文；本地战报/总结用中文。

## 1. Inbox 处理流程（目标：收件箱归零）

### 1.1 拉取与分诊

```powershell
python D:\Hermes\projects\github-tools\scripts\gh_inbox.py
python D:\Hermes\projects\github-tools\scripts\gh_inbox_triage.py
python D:\Hermes\projects\github-tools\scripts\scan_pending_mentions.py
# 可选：自动清理纯告知类
python D:\Hermes\scripts\inbox_auto_sweep.py --dry-run
python D:\Hermes\scripts\inbox_auto_sweep.py
```

- `gh_inbox_triage.py`：拉全量 unread，12 并发 resolve PR（number/state/merged/user/head_ref），16 并发取 `latest_comment_url`，输出 TSV + JSON，统计 by reason / by repo / ours vs theirs。
- **顺序铁则**：`scan_pending_mentions.py` 必须先于任何清理动作（sweep 或标 Done）。`inbox_auto_sweep.py` 只按**最新一条评论**分类，若线程里 pending @ 之后跟着推送/致谢类事件，会被它当纯告知类清掉——已知缺陷（脚本未加防护）。修复前：人工批次把 sweep 放在 scan 之后跑；cron 自动清理放开前需先给 sweep 加 pending 防护。
- `scan_pending_mentions.py`：**唯一"有人在等我"标准** — `comments after my LAST comment` 中 `body contains Enough1122 and author != me`（不带 @ 前缀也算，与脚本一致）。忽略 `reason==mention`（不可靠）。并发 6（12 会触发 secondary 限流导致误报 0）。输出 `drafts/_pending_mentions.json`。已知盲区：PR review **正文**（`/pulls/{N}/reviews`）不扫描，必要时人工补看。
- 限流：403/429 退避 `sleep 60*(attempt+1)`，最多 3 次；连续 3 个 API 失败则本轮静默退出不动收件箱。

### 1.2 分类规则（2026-09-17 起按"克制发声"口径）

- **复审并回复**：@ 我 **且** 满足其一：① 作者按我们之前的意见做出了修改；② 有迹象表明我们之前的 review 意见有误；③ 作者就我们的 review 意见提问、需要我们裁决（如"here or follow-up?"）→ 走 §1.3。
- **直接清空（标 Done）**：致谢与修复告知、disposition 收条、CI 播报、已合并/关闭摘要、自己评论回声、无正文推送事件、第三方之间与我无关的讨论等纯告知/噪音类。
- **列请用户定夺**：@ 我但不满足复审前提，或内容实质但意图无法判定 → 记入战报"待用户定夺"节并当面汇报；不擅自回复，也不擅自清。
- 同一线程只提醒一次（state 记录 thread id + updated_at；有新活动才再提醒）。
- 注意：以上分类与 sweep 一致，仅基于**最新一条**评论；线程内更早的未回 @ 不参与判定，故 §1.3.1 的 scan 才是"有人在等我"的唯一权威，清理不得先于 scan。

### 1.3 定向 @ 回复 SOP（必须实证）

1. 只回满足 §1.2 复审前提的 pending（@ 触发的复核）；订阅噪音（作者自更新/无实体 body 更新/teknium1 收尾/第三方非定向讨论）一律只归档不回。
2. 回复前必须拉**当前 HEAD diff 全文**核验（`gh_pr_detail.py` 或 `gh api repos/{REPO}/pulls/{N}` + `/pulls/{N}/files`），逐条引用 `file:line` 验证作者声明。声明为真 → 接受；为假 → 指出 diff 现状 + 期望修复。
3. 回评风格（英文，贴 issuecomment 链接回战报）：
   - 接受：`Verified on head {sha}: ... (file:line ...). Accept as addressed.` + 残留非阻塞 note（如有）。
   - 部分放行：列 `❌ 仍在 diff / ⚠️ 新问题`，要求作者处理。
   - 误报更正：承认误标并致谢（如 #97317 案例）。
   - 被点名的复核即使验证通过也回最简一句确认（回应点名，不算刷存在）；"无问题静默"规则只约束**主动** review（§2.2），不约束 @ 触发的复核。
   - 回评正文同时追加存 `reviews/hermes-agent-YYYYWww/rb/{N}.md`（无则创建），与战役评语同库可追溯。
4. 发评用 `post_followup.py {N}`（正文先写进 `Temp/opencode/campaign/{N}.md`），成功 sleep 8s。不要用 `gh_post.py` 手写一次性脚本。
5. 全部处理完后逐 thread 标 Done（DELETE 用 `gh api -X DELETE /notifications/threads/{tid}`），目标 unread=0，失败 0。传输怪癖（2026-08-23 实测）：.env token 对通知只读，通知写操作必须走 gh CLI（classic token）；线程级 **PUT 一律 404**（GitHub 侧怪癖），标已读用线程级 DELETE，批量清零可用集合级 `PUT /notifications`（2026-09-17 实测可用）。

### 1.4 战报格式（追加到 `_inbox_report_YYYY-MM-DD.md`）

```md
# 第N批 · YYYY-MM-DD（X 条）→ 已清零
**账号:** Enough1122 · **处理:** X/X 标 Done · **处理后未读:** 0
构成: comment A + mention B · 复审回复: C · 静默跳过: D · 列请示: E
## 🎯 复审回复（如有，每条：PR 标题/作者/head sha + 实证 1/2/3 + 回评链接）
## 列请用户定夺（如有，每条：线程 + 原文摘录 + 我方倾向；无可省）
## 其余（第三方评论抽样 + 作者自更新数 + 已关收尾）
## 处置（Done 数/失败数/无需逐条回复）
## 待跟进（延续阻塞 + 新增阻塞 + 已闭环移出）
```

## 2. hermes-agent 批量 PR 审阅流程

### 2.1 选候口径（默认战役口径）

- `open + ≤15 文件 + 无 issue 评论 + 无 review + 无 inline 评论 + 非 draft + diff <100KB`（2026-09-17 放宽自 ≤8/<60KB；size 以 additions+deletions 近似，拉 diff 时复核真值）。
- **超限不丢**：>15 文件或 ≥100KB 的零关注 PR → 由 `count_candidates.py` 扫描时记入 `_campaign_state.json` 的 `deferred` 列表（number+files+size，滚动覆盖为本次扫描结果）——断点继续往前，但 backlog 留底，有胃口时点名补审；大改动常是高风险变更，不审也要看得见。
- 断点续打（2026-09-17 明确）：审阅**只往前走**——PR 编号全局递增，比 frontier 大的就是新 PR。frontier 的**权威来源是本地 `drafts/_campaign_state.json`**（每批收尾更新，含 posted / silent-clean / skip 的最大编号）；`find_next_new_prs.py`（按 GitHub 已评论最大编号反推）只作兜底校验——静默跳过的 PR 在 GitHub 上无痕迹，只靠它会把 clean PR 重复审一遍。新候选 = frontier 之后仍 open 的 PR，按 §2.2 活检规则筛选。不要重复评已处理 PR。
- 跳过：已有关注 / 已关 / 404 / 活检中途有人评论（发前重检）。

### 2.2 单条审阅步骤

1. **活检**：`GET /pulls/{N}` 确认 open & 非 draft；`GET /issues/{N}/comments`、`GET /pulls/{N}/reviews`、`GET /pulls/{N}/comments` 任一非空 → SKIP_STALE。
2. **拉 diff**：存 `drafts/_campaign/{N}.diff`，逐文件读全（不是只看 title）。
3. **写评语**到 `C:\Users\admin\AppData\Local\Temp\opencode\campaign\{N}.md`，**必须**以 `> AI code review — automated review for reference; please use your judgment.` 开头。结构：
   ```md
   > AI code review — ...
   [1段：这个 PR 做了什么 + 总体评价，点名关键文件]
   1. **标题** — file:line 实证 + 风险/复现路径 + 建议修复（区分 blocker / 非阻塞）
   2. ...
   Minor: ...
   ```
   - 只报 diff 里真实存在的行号；不确定的写“建议确认”而非断言。
   - 常见抓点：并发/竞态、幂等、鉴权/allowlist、路径穿越、secret 落盘、代理透传、超时/重试上限、测试钉错半侧、死代码、文档与实现不符、重叠 PR 冲突风险。
   - **发布门槛（克制发声，2026-09-17 起）**：草稿写完自检——**无实质问题（仅 LGTM/纯吹毛求疵）→ 不发帖**（记 SKIP_CLEAN），草稿转归档；有 ≥1 个实质问题（blocker 或有价值的非阻塞发现）才走第 4 步发布。
4. **去重与发布**：`python scripts/post_one.py {N}`（自动补 header + 发前 liveness 重检 + Enough1122 去重 + POST issue comment + sleep 8）。批量首选用 `post_one.py`；老 PR 首评可用 `post_review.py`；已评 PR 的追评用 `post_followup.py`。输出 `POSTED/SKIP_DUPE/SKIP_STALE/ERR` 如实记录。注意：`post_one.py` 目前**没有** SKIP_CLEAN 判定，发布门槛由 agent 在写稿阶段把关，无问题草稿不要传给它（脚本加门槛前如此）。
5. **归档与断点落盘（每批必做）**：评语另存 `reviews/hermes-agent-YYYYWww/rb/{N}.md`，编号记入 `progress.txt`（含静默跳过的 PR，标 `clean/silent`），并**必须**更新 `drafts/_campaign_state.json`：silent-clean 编号追加进 `reviewed_clean` 列表、`frontier` = 本批处理过的最大 PR 编号（不论 posted / silent-clean / skip）、posted 编号追加进 `posted` 列表。批次中途退出也要先落盘再退；下次战役直接从 `frontier+1` 起。

### 2.3 并行打法

- 按编号序分 chunk（如 5 路 ×25 或 13 路 ×20），子代理并行读 diff 写草稿，主流程串行 POST（单条 sleep 8 防限流）。
- 每 chunk 汇报 `posted / silent-clean（无问题未发） / skipped（原因）+ 代表 PR + 关键发现（blocker 候选）`，汇总进战报“续战”章节，更新累计已发数。

## 3. 铁律

1. **实证优先**：任何“已修复/已落地”结论必须有当前 head 的 file:line 证据；没拉到 diff 就写“未核验”。
2. **只报问题**：主动 review 无实质问题一律静默跳过（本地归档，不发帖）；回复仅限 §1.2 复审前提的 @ 触发场景；宁可少发，不刷存在感。
3. **不复评**：发前必查 Enough1122 是否已有 AI review；有则 SKIP_DUPE。
4. **收件箱归零**：每批结束 unread 必须 0；API 连续失败则静默退出等下一轮，不硬标。
5. **凭证不入库**：`.env*`、token、key 永不写进仓库文件。
6. **先 scan 后清**：`scan_pending_mentions` 先于任何 sweep / 标 Done；清理前确认线程内无未回 @，防止把"有人在等"的线程当纯告知类埋掉（sweep 脚本加防护前尤其如此）。
7. **断点必落盘**：每批结束把 `frontier`（本批处理过的最大 PR 号，含 silent-clean / skip）写进 `_campaign_state.json` 与 `progress.txt`；下批从 `frontier+1` 继续，只审编号更大的新 PR，绝不回头。
