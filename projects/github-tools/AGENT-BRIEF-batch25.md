# batch25 子代理通用简报（每任务必读）

你在做 `NousResearch/hermes-agent` 开源 PR 的批量 AI code review。
身份仅作说明：账号 Enough1122。**你只做参考分析：不发帖、不评论、不 approve、不改任何仓库**。

## 产出（两件，缺一不可）

1. **verdict JSON** → `D:\Hermes\projects\github-tools\drafts\_verdict_batch25_<N>.json`
   ```json
   {"chunk": "<N>", "verdicts": [
     {"n": <N>, "v": "CLEAN|DRAFT|SKIP_STALE", "level": "blocker|nonblocking|null",
      "note": "一句话结论", "evidence": "file:line（blocker 必填，post-image 行号）"}]}
   ```
   - `v=CLEAN`：无实质问题（只有风格/挑刺/LGTM）。**不写草稿**。
   - `v=DRAFT`：有 ≥1 个实质问题（blocker 或有价值的非阻塞），草稿必须已落盘（见下）。
   - `v=SKIP_STALE`：活检发现已有关注（有人评论/review 过）、已关、404 等，note 写原因。

2. **草稿**（仅当 v=DRAFT）→ `C:\Users\admin\AppData\Local\Temp\opencode\campaign\<N>.md`
   - 首行固定：`> AI code review — automated follow-up for reference; not a maintainer.`
   - 正文英文；结构：1 段概述（这个 PR 做了什么 + 总体评价，点名关键文件），随后编号条目，每条给 file:line 实证 + 风险/复现路径 + 建议修复；最后 `Minor:` 放非阻塞小点。
   - 行号一律用 **diff post-image 行号**（main 侧行号会让作者找错位置）；只报 diff 里真实存在的行号；不确定的写 "please confirm" 而非断言。

## 审阅步骤

1. diff 已在 `D:\Hermes\projects\github-tools\drafts\_campaign\<N>.diff` —— **先核对 diff 文件头编号**再读；逐文件读全，不是只看 PR 标题。
2. 需要旧版文件时：`git -C D:\Hermes\repos\hermes-agent-fix show upstream/main:<path>`（**不要**用工作树文件，工作树可能停在别的分支）。
3. 预检已跑过（apply_ok / mergeable / 配对见任务说明）：**不要重跑预检**。
4. **时间盒 ≤12 分钟/PR**：静态证据优先（diff + `git show` 能坐实的结论**不跑测试**）；只有结论依赖运行时才跑单文件测试（≤1 次）；改动 <120 行且读完干净 → 直接 CLEAN 收，不为找问题而深挖。
5. 503/限流：`sleep 60×n` 重试，最多 3 次，别因一次故障丢掉整轮。

## 常见抓点（按 diff 实际内容判断，不硬套）

并发/竞态、幂等、鉴权/allowlist、路径穿越、secret 落盘、代理透传、超时/重试上限、测试钉错半侧、死代码、文档与实现不符、重叠 PR 冲突风险（有配对预警的要写明"只能落一个"）。

## 纪律

- 每条 claim 带文件 + 行号；跑不通/没验证的不要写成结论；判不出就归"非阻塞/待复核"并注明未验证。
- 完成后聊天里只回一行：`<N> <CLEAN|DRAFT|SKIP_STALE>`。
