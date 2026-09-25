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
5. 全部处理完后逐 thread 标 Done（DELETE 用 `gh api -X DELETE /notifications/threads/{tid}`），目标 unread=0，失败 0。传输怪癖（2026-08-23 实测）：.env token 对通知只读，通知写操作必须走 gh CLI（classic token）；线程级 **PUT 一律 404**（GitHub 侧怪癖），标已读用线程级 DELETE，批量清零可用集合级 `PUT /notifications`（2026-09-17 实测可用；bash 里写 `gh api -X PUT notifications` 不带前导斜杠，Git Bash 会把 `/notifications` 改写成文件路径）。

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

- `open + 非 draft` 是基本候选条件（2026-09-25：已有 issue comment / formal review / inline comment **不再过滤候选**；它们必须先读作观点对照）。默认战役优先 `fast` lane 的 ≤15 文件且增删行数 ≤250 PR；更大/高改动 PR 不丢弃，进入 durable task pool 的 `deep` lane，由 worker 按风险处理。
- **超限/高改动不丢**：>15 文件或增删行数 >250 的 PR 保留在 `review_pool.db`，由 `deep` lane 处理；不要用 `deferred` 隐藏。连续多个独立 GitHub 端点持续 403/429 才暂停。
- 断点续打（2026-09-17 明确）：普通新 PR 只从 `frontier` 之后取；但 head 漂移、错误 deferred、退出 worker 的未完成项必须继续留在 durable pool，不能因编号低于 frontier 被漏掉。新候选 = frontier 之后仍 open 的 PR，另加 pool 中 `resume:`/head 漂移重审项，按 §2.2 活检规则筛选。不要重复评已处理 PR。
- 跳过：已关闭 / 404 / draft / 我方已有完全重复的结论。**已有他人或我方 comment/review/inline 不构成跳过**：先读已有内容并做语义去重；若新发现是独立 bug、反证、遗漏边界或作者回复后状态变化，继续发布。

### 2.2 单条审阅步骤

1. **活检与观点对照**：`GET /pulls/{N}` 确认 open & 非 draft；读取 `GET /issues/{N}/comments`、`GET /pulls/{N}/reviews`、`GET /pulls/{N}/comments` 全部已有观点。attention 非空不触发 SKIP；只在我方结论与既有结论实质重复（同根因、同证据、同修复建议）时静默，否则有实质新发现就发布。
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
4. **语义去重与发布**：`python scripts/post_one.py {N}` 自动补 header、确认 open/non-draft，并拦截**完全相同的我方评论**；已有他人或我方 review 本身不拦截。发布前完成语义去重：结论实质重复则不发；独立新问题、反证、遗漏或状态变化可发为补充/追评。`POSTED` 后必须从 URL 取 `issuecomment-<id>`，用 `gh api repos/NousResearch/hermes-agent/issues/comments/<id> --jq '.user.login'` 读回确认 `Enough1122`；不通过就 `requeue`，禁止把第三方 URL 记成我方 `posted`。旧批次才使用 `post_batch.py`。
5. **增量归档与断点落盘（每条必做）**：评语另存 `reviews/hermes-agent-YYYYWww/rb/{N}.md`，编号记入 `progress.txt`（含静默项，标 `clean/silent`）。durable DB 是并发与断点权威；`_campaign_state.json` 只保留历史集合并记录已确认终态的 frontier，不能覆盖 DB 中 queued/running 项。

### 2.3 并行打法（持续 durable worker pool）

**流水线（按序执行，别跳步）：**

1. **拉 diff**：`python scripts/diffs_batch115.py drafts/_batch{NN}_list.json drafts/_batch{NN}_final.json`
   （超大/高改动项进入 durable `deep` lane；不再只记 deferred）。
2. **机械预检（脚本，派单前一次跑完）**：
   `python scripts/preflight_batch.py batch{NN}`
   产出 `drafts/_preflight_batch{NN}.json`：每条 PR 的
   `apply_ok`（hunk 是否基于旧版 main）、`mergeable_state`、**配对预警**
   （共享文件的疑似堆叠/互斥对）。派单时把这两项直接写进 worker 简报——
   - `apply_ok=false` → 子代理按"机械 rebase"快审（不必深读语义）；
   - 配对预警 → 两个 PR 的草稿都要写明"只能落一个"，避免重复深读。
   `--no-mergeable` 可跳过 gh api（限流时）。
   **pre-image 来源（2026-09-21 起）**：脚本用 `git show upstream/main:<path>` 取文件内容（工作树兜底），
   并打印 `base=<ref>@<sha>`。派单前先 `git -C D:\\Hermes\\repos\\hermes-agent-fix fetch upstream`——
   工作树可能停在某条 PR 分支上，旧版脚本从工作树取文件会**误报 apply-fail**（#117301 反例）。
3. **并发 worker 自取（2026-09-25 当前默认）**：把全部 open、非 draft 候选预载进 durable task pool（`review_pool.db`），按当前 `delegation.max_concurrent_children`（通常 10）启动 worker。worker 按 lane 领取：约 7 路 `fast`、3 路 `deep`；`fast` 优先 `changed_files<=15` 且增删行数 `<=250`，`deep` 优先更大或高改动任务，head 漂移/错误 deferred/resume 任务优先，lane 空时安全回退到任意 queued。每个 worker 原子 claim 一个 PR；`claim` 对同一 worker 幂等，已有未结 running claim 时只续租并返回原 PR，不得把重入响应当成下一条。完成审阅/语义去重/发布或静默落盘后立即再 claim，直到队列为空；不再拆 2–3 条小波，也不反复等用户确认。已关闭、draft、完全重复结论或过期失联项才标 skip/deferred。主流程用 `python scripts/review_pool.py <db> metrics` 联合 `delegate_task list` 巡检，目标是 active worker 数 = fresh claim 数、每 worker 恰好 1 条 fresh claim、expired claim=0；worker 退出时先回收其未完成 claim，再立即补位，健康任务不抢占。
4. **单条审阅与证据**：worker 每次只处理 `claim` 返回的一条 PR。活检 open/non-draft 与 exact head，读取 issue comments、formal reviews、inline comments 和完整 diff；优先静态证据，只有结论依赖运行时才跑一次目标测试。所有引用使用 post-image `file:line`。
5. **实时发布**：有实质问题才写 `drafts/_pending/<pr>.md` 并运行 `python scripts/post_one.py <pr>`；输出 `POSTED` 后用 `gh api repos/NousResearch/hermes-agent/issues/comments/<id>` 读回，确认作者 `Enough1122` 且 URL 属于当前 PR。完全相同的我方正文才跳过；独立新问题可继续发。
6. **写 durable result**：CLEAN 写 `result <pr> clean <worker>`；有效问题评论写 `result <pr> posted <worker> <canonical-url>`；已公开但被当前 head/作者反证推翻的意见，必须先发布并读回明确撤回/纠正，再写 `result <pr> corrected <worker> <canonical-url>`，并删除本地未发布旧草稿。`corrected` 仍强制 receipt 校验，但统计上不得计入 posted。`review_pool.py` 会在改变状态前再次校验 URL 和作者 receipt，并用 `claim_started_at` 拒绝早于本次 claim 的旧评论；owner mismatch 时不得发布或写 result。当前 head 重审为 CLEAN 时，旧 head 评论只能留作公开历史，禁止重新挂成当前 `posted` receipt。
7. **异常与重试**：单个 codeload/raw/content endpoint 403/429 时切到已落盘 diff、`gh pr diff`、另一 file endpoint 或单文件 `gh api`；多个独立端点持续失败才停止。处理中每 5 分钟执行一次 owner 校验 heartbeat；worker 退出后由统筹 `release` 回队列并立即补位。
8. **增量归档与继续**：每条完成后把终态追加到 `progress.txt`；可用 `_verdict_<worker>_<pr>.json` 留审计证据。durable DB 是并发与断点权威，`_campaign_state.json` 的 frontier 只约束新候选，head 漂移、错误 deferred 与 `resume:` 项不受编号限制。完成一条立即再次 `claim`，不设固定 chunk、波次或条数上限；`post_batch.py` 仅用于兼容旧批次。

**子代理 prompt 要点：**
- 只处理本次 claim 返回的 PR；claim 幂等，已有 running claim 时返回并续租原 PR，不得把它误当新任务。
- 先核对 exact head 和 diff 文件头；处理期间每 5 分钟 heartbeat。
- CLEAN 静默；DRAFT 必须有复现路径、实际影响和 post-image `file:line` 证据。
- 写完 result 立即领取下一条；不修改上游仓库代码。

**成本经验（2026-09-20 五批实测）：** 核验全覆盖 ≈ 与审阅同价，收益集中在 blocker；非阻塞核验多数只修行号。报告走聊天框会延迟/截断/复读，走 verdict 文件后消失。


## 3. 铁律

1. **实证优先**：任何“已修复/已落地”结论必须有当前 head 的 file:line 证据；没拉到 diff 就写“未核验”。
2. **只报问题**：主动 review 无实质问题一律静默跳过（本地归档，不发帖）；回复仅限 §1.2 复审前提的 @ 触发场景；宁可少发，不刷存在感。
3. **不复评完全相同正文**：发前必查 Enough1122 是否已有与草稿**完全相同**的 AI review；仅有同结论或已有不同 review 不构成拦截，仍按 §2.2 做语义去重。
4. **收件箱归零**：每次 inbox 收口时 unread 必须为 0；API 连续失败则保留状态，等下一轮重试，不硬标完成。
5. **凭证不入库**：`.env*`、token、key 永不写进仓库文件。
6. **先 scan 后清**：`scan_pending_mentions` 先于任何 sweep / 标 Done；清理前确认线程内无未回 @，防止把"有人在等"的线程当纯告知类埋掉（sweep 脚本加防护前尤其如此）。
7. **断点必落盘**：每条完成即写 durable result 和 `progress.txt`。`_campaign_state.json` 仅汇总历史终态；queued/running/head 漂移项始终以 `review_pool.db` 为准，不能被 frontier 或 deferred 列表隐藏。
8. **汇报走文件**：verdict、草稿和 result 逐条落盘，聊天框只作控制面；报告截断/延迟/复读是旧批模式的主要时间税，不恢复固定 chunk 汇报。
9. **机械检查前置**：`apply_ok` / `mergeable_state` / 配对预警由 `preflight_batch.py` 在派单前一次跑完（§2.3 第 2 步），不让 10 个子代理各跑一遍。
10. **通道边界（2026-09-21 用户定，硬规则）**：批量审阅**只跑 Hermes 自己的通道**。禁止转 `claude` CLI（走公司代理→公司模型，**公司侧有审计**）或走公司 provider 的 `opencode2` 调用——开源贡献不是公司工作，用公司资源干这个=审计风险。用户提"Claude/OpenCode 很快"只是在说速度，**不是改派授权**；要提速就优化 Hermes 侧（一 PR 一 claim / 并发上限 / 持续 worker），不动执行方。
11. **换执行方/通道先确认（2026-09-21 用户定）**：凡是**改变执行方、工具或通道**（claude/opencode/公司资源/外部服务）或**动用户配置**的动作，先给用户 ≤2 选项的短确认再动手；本战役流水线内的日常动作（扫候选 / 派子代理 / 复审 / 发帖 / 归档 / 清 inbox）照旧**直接干不问**。
