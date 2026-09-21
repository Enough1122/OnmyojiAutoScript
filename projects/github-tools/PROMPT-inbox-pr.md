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

### 2.3 并行打法（2026-09-20 起：预检 → 审阅 → verdict 文件 → 只核 blocker）

**流水线（按序执行，别跳步）：**

1. **拉 diff**：`python scripts/diffs_batch115.py drafts/_batch{NN}_list.json drafts/_batch{NN}_final.json`
   （≥100KB 的自动记 OVER，收尾时补进 `_campaign_state.json` 的 `deferred`）。
2. **机械预检（脚本，派单前一次跑完）**：
   `python scripts/preflight_batch.py batch{NN}`
   产出 `drafts/_preflight_batch{NN}.json`：每条 PR 的
   `apply_ok`（hunk 是否基于旧版 main）、`mergeable_state`、**配对预警**
   （共享文件的疑似堆叠/互斥对）。派单时把这三项直接写进 chunk 简报——
   - `apply_ok=false` → 子代理按"机械 rebase"快审（不必深读语义）；
   - 配对预警 → 两个 PR 的草稿都要写明"只能落一个"，避免重复深读。
   `--no-mergeable` 可跳过 gh api（限流时）。
   **pre-image 来源（2026-09-21 起）**：脚本用 `git show upstream/main:<path>` 取文件内容（工作树兜底），
   并打印 `base=<ref>@<sha>`。派单前先 `git -C D:\\Hermes\\repos\\hermes-agent-fix fetch upstream`——
   工作树可能停在某条 PR 分支上，旧版脚本从工作树取文件会**误报 apply-fail**（#117301 反例）。
3. **一 PR 一代理、整批一次铺满（2026-09-21 起：吞吐优先）**：
   - 并发上限 `delegation.max_concurrent_children` 由 10 提到 **20**。改配置认准真 home
     `C:\Users\admin\AppData\Local\hermes`；shell 里若残留 `HERMES_HOME=/tmp/...` 会把配置写进测试 home
     （2026-09-21 踩过）——**改前先 `echo $HERMES_HOME` + `hermes config get`，改后读回确认**。
   - **一次 `delegate_task` 调用 = 一个完成单元**：12 个 task 也只回来一条汇总。所以波浪墙钟 ≈
     单个代理耗时（实测 ~10 分钟），**批越大越划算**——把当下全部 eligible 一次铺完，绝不拆小波
     （小波 = 干等最慢的那个）。真正的时间税是"小波 + 波浪间空转"，不是并发不够。
   - 子代理简报模板加四句时间盒：**≤12 分钟**、静态证据优先（diff + `git show upstream/main:<file>`
     能坐实的结论**不跑测试**）、只有结论依赖运行时才跑单文件测试（≤1 次）、改动 <120 行且读完干净 →
     直接 CLEAN 收、不为找问题而深挖。
   - 实测口径（2026-09-21 01:00-01:30）：eligible 到达 ≈ **23 条/小时**；12 路一波并行 ≈ 60-70 条/小时。
     队列不降反升时先查"是不是又在派小波"。**prep（diff+预检）只要 9 秒**（12 条实测），不是瓶颈。
4. **verdict 文件汇报（不再靠聊天框）**：每个 chunk 完工写
   `drafts/_verdict_batch{NN}_chunk{K}.json`：
   ```json
   {"chunk": "chunk3", "verdicts": [
     {"n": 116571, "v": "CLEAN", "level": null, "note": "一句话"},
     {"n": 116578, "v": "DRAFT", "level": "nonblocking", "note": "...", "evidence": ""},
     {"n": 116676, "v": "DRAFT", "level": "blocker", "note": "...", "evidence": "file:line"},
     {"n": 116701, "v": "SKIP_STALE", "level": null, "note": "原因"}]}
   ```
   `v=DRAFT` 表示草稿已写到 `Temp/opencode/campaign/{N}.md`。
5. **收集与校验**：`python scripts/collect_verdicts.py batch{NN} 10`
   —— 检查 10 行齐全、草稿存在且首行合规、**草稿引用文件与 diff 头比对防错配**，
   输出 `_batch{NN}_collect.json`（clean/skip 种子 + blocker 清单 + 问题清单）。
   报 `WAIT` 就等下一轮（这是设计行为，别当失败重派）。
6. **核验（只保 blocker）**：blocker 候选按组给 1–2 个核验代理，要求真实复现
   （`git apply --check`、临时副本跑语义、构造攻击形态）并给 CONFIRMED/REFUTED/PARTIAL；
   非阻塞草稿由主流程抽查（约 30%）+ 全量过一遍 diff 文件头。
7. **发帖**：`python scripts/post_batch.py <n1> <n2> ... --workers=4` —— **并发、无 sleep**
   （2026-09-21 用户定："先别考虑限流的事情，触发了再说，提高效率"；403/429 真出现再退避）。
   单发仍可用 `post_one.py`（其间隔由 `POST_SLEEP` 环境变量控制，默认 0）。
   发帖可与下一批的审阅重叠（子代理在跑时主流程发上一批的帖）。
8. **归档**：`python scripts/archive_batch.py drafts/_batch{NN}_status.json drafts/_batch{NN}_list.json`
   （状态值 posted/clean/skip/deferred；frontier 只在批次内构成连续前缀时才前进）。

**子代理 prompt 要点（模板化，别每次重写）：**
- 只审列出的 N 个 PR；读 `drafts/_campaign/{N}.diff` 逐文件读全；先核对 diff 文件头编号（防错配）。
- 活检一行命令；`git apply --check` 结果以预检 JSON 为准（不必重跑）。
- 行号一律用 **diff post-image**（补丁打到临时副本后量的行号）——main 侧行号会让 PR 作者找错位置。
- 草稿首行固定声明；正文英文；只报真实行号，不确定写"建议确认"。
- **503/限流自查重试**（sleep 60×n，最多 3 次），不要因一次网关故障把整轮丢掉。
- 完工写 verdict JSON（见上），聊天里只回一句"chunk K done"。

**成本经验（2026-09-20 五批实测）：** 核验全覆盖 ≈ 与审阅同价，收益集中在 blocker；非阻塞核验多数只修行号。报告走聊天框会延迟/截断/复读，走 verdict 文件后消失。


## 3. 铁律

1. **实证优先**：任何“已修复/已落地”结论必须有当前 head 的 file:line 证据；没拉到 diff 就写“未核验”。
2. **只报问题**：主动 review 无实质问题一律静默跳过（本地归档，不发帖）；回复仅限 §1.2 复审前提的 @ 触发场景；宁可少发，不刷存在感。
3. **不复评**：发前必查 Enough1122 是否已有 AI review；有则 SKIP_DUPE。
4. **收件箱归零**：每批结束 unread 必须 0；API 连续失败则静默退出等下一轮，不硬标。
5. **凭证不入库**：`.env*`、token、key 永不写进仓库文件。
6. **先 scan 后清**：`scan_pending_mentions` 先于任何 sweep / 标 Done；清理前确认线程内无未回 @，防止把"有人在等"的线程当纯告知类埋掉（sweep 脚本加防护前尤其如此）。
7. **断点必落盘**：每批结束把 `frontier`（本批处理过的最大 PR 号，含 silent-clean / skip / deferred）写进 `_campaign_state.json` 与 `progress.txt`；下批从 `frontier+1` 继续，只审编号更大的新 PR，绝不回头。超限 PR（>15 文件 / ≥100KB）记 `deferred`，断点照常前进。
8. **汇报走文件**：子代理的 verdict 一律写 `drafts/_verdict_batch{NN}_chunk{K}.json`（§2.3 第 4 步），聊天框只回一句确认。报告截断/延迟/复读是 2026-09-20 前的主要时间税，不要回退到聊天汇报。
9. **机械检查前置**：`apply_ok` / `mergeable_state` / 配对预警由 `preflight_batch.py` 在派单前一次跑完（§2.3 第 2 步），不让 10 个子代理各跑一遍。
10. **通道边界（2026-09-21 用户定，硬规则）**：批量审阅**只跑 Hermes 自己的通道**。禁止转 `claude` CLI（走公司代理→公司模型，**公司侧有审计**）或走公司 provider 的 `opencode2` 调用——开源贡献不是公司工作，用公司资源干这个=审计风险。用户提"Claude/OpenCode 很快"只是在说速度，**不是改派授权**；要提速就优化 Hermes 侧（一 PR 一代理 / 整批铺满 / 并发上限 / 子代理时间盒），不动执行方。
11. **换执行方/通道先确认（2026-09-21 用户定）**：凡是**改变执行方、工具或通道**（claude/opencode/公司资源/外部服务）或**动用户配置**的动作，先给用户 ≤2 选项的短确认再动手；本战役流水线内的日常动作（扫候选 / 派子代理 / 复审 / 发帖 / 归档 / 清 inbox）照旧**直接干不问**。
