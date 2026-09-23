# 第1批 · 2026-09-23(19 条)→ 已清零
**账号:** Enough1122 · **处理:** 19/19 标 Done · **处理后未读:** 0
构成: comment 17 + mention 2(另 cc-switch issue 1) · 复审回复: 0 · 静默跳过: 0 · 列请示: 0

## 背景事件
今日 11:42–13:18 **kshitijk4poor 在做 perf sweep,批量关闭旧 PR**。本批 19 条中 13 条是该清扫产生的关闭通知(9 条纯关闭事件无新评论,4 条附关闭评论,全部引用或复核了我们 8–9 月的旧 review,均只 @ PR 作者、无一向我们提问)。这解释了为何一批低编号旧 PR(51466–105718)同时涌入收件箱。

## 🎯 复审回复
无。两条 scan 出的 pending @ 核实后均不满足 §1.2 复审前提:

1. **PR #87273**(fix(desktop): clear sticky billing error,olympusbuildz)— thelonewander3r 9-02 长评引用我们两点:point 1(assistantLooksSuccessfullySettled 把 error/failed 工具行当成功落定)他认可"still stands"并给了补丁 commit;point 2(跨会话清 billing block)他认为"already handled"(clearBillingBlock(sessionId) 对 session 不匹配 no-op)。**随后作者 olympusbuildz 今日 11:49 自己关闭 PR**(stale/conflicting,可 rebase 后重开)。线程已死,无需回应;thelonewander3r 对 point 2 的反驳仅备案,不影响后续(该 PR 未合并)。
2. **PR #89253**(Trim tool schema descriptions,cmacjr11)— kshitijk4poor 今日 13:16 关闭,关闭理由明确引用我们 8-21 的发现("hardcoded /opt/data/scripts/ … a regression flagged by Enough1122 and never fixed"),邀作者量到热点成本后重提。纯收尾,无提问。

## 其余(17 条 comment)
- **perf sweep 关闭评论 6 条**(kshitijk4poor → 各 PR 作者,未 @ 我们):#98235(telegram adapter 缓存重建——k 判定 main 上 `_load_gateway_config` 并非缓存)、#103252(OpenViking prefetch cache——k 判定 queue_prefetch 在 main 是刻意 no-op,缓存按 query 键永不会命中;比我们当时"bounds 合理"的 review 更进一步,但与我们陈述的事实不冲突)、#91938(gateway platforms 缓存——k 实测 warm 路径仅省 0.24ms,2116 行不值)、#105718(hoist compaction imports——k 实测 warm import 0.30µs)、#89253/#87273(见上)。
- **纯关闭事件 11 条**(无新评论,latest_comment 回落到 PR 正文):repfigit #92231 相关 shallow-copy PR、byzorky1-sudo #105619、Finn763 #101181/#101176/#102064、Christopher-Schulze #85850、teddiesloco #95640、Diaspar4u #91234、chad1987 #92167(仍 open)、akivavh #85291(仍 open)、sweetrb #51466(仍 open)、olympusbuildz #87162。注:92167/85291/51466 state 仍 open,通知应来自 sweep 触碰(打标/状态变更),无新评论,不动。

## cc-switch issue #7382(OpenCode V2 适配,非 hermes-agent)
sugu6 11:41 回复 = 按我们 11:33 要求贴出 Windows + v2.0.15 实测(纯 V1 配置现状、opencode 端零告警、证实"单数 provider 仍被支持非一律失效"),并认领自己上条"先合 #7579"的口误(漏看 isDraft),认同卡点 = #7577 零人工 review,表态愿意后续一起 @ 维护者。**收条类,无提问,标 Done 不回。** 我们此前承诺"持续盯 #7577,久无 review 就 @ 维护者"——#7577 现仍 reviews=0,如需推进由用户定夺(非本批动作)。

## 处置
19/19 标 Done(gh CLI 线程级 DELETE,15+4,失败 0)。scan_pending_mentions 先行 ✓。未跑 inbox_auto_sweep(已逐线程人工读最新评论分类,比 sweep 启发式更准)。

## 待跟进
- 延续:batch26 剩 19 条搁置中,续跑通道未定(Hermes/OpenCode2/豁免 claude),待用户定。
- 新增(观察项,非阻塞):kshitijk4poor 的 perf sweep 正在批量关闭我们审过的旧 PR,关闭理由多条比我们当时的 review 更深(尤其 #103252 的"缓存永不命中"、#91938 的成本核算)。**对农场的含义**:低编号 PR 正被上游集中清理,frontier 断点机制不受影响(只往前走);但若 sweep 持续,frontier 之后的候选池可能加速蒸发,续跑 batch26 的窗口在收窄。
- cc-switch #7577 若持续零 review,是否由我们出面 @ 维护者——待用户定夺。

## 后续动作 · #7577 实证 review(cc-switch,用户指令)
用户在 @ 维护者与实证 review 之间选了后者(暂不发 @ 评论)。已对 DEAN-Cherry 的 PR #7577 做逐文件核对(head `a6f772d` / base `6f6087cd`):
- 丢字段机制坐实:`OpenCodeProviderConfig` 顶层无 flatten 兜底 → `api`/`env` 必丢;`OpenCodeModelLimit` 只有 context/output → `limit.input` 必丢。PR 的损失清单逐项精确。
- 修复核验:import 两分支入库原始 JSON ✓;write 路径校验与持久化分离 ✓;解析失败行为不变 ✓;删包函数仅 live.rs 两处调用点、CI 四平台背书 ✓;两个回归用例改动前必失败 ✓。
- 已发评论:https://github.com/farion1231/cc-switch/pull/7577#issuecomment-5795760389
- 遗留:@ 维护者的评论 → **已发**(用户指令):https://github.com/farion1231/cc-switch/issues/7382#issuecomment-5795838369 。升级触发器:约一周仍零 review 或作者失联 → 考虑接手(注明出处)。
