# 第1批 · 2026-09-24（66 条）→ 已清零
**账号:** Enough1122 · **处理:** 66/66 标 Done · **处理后未读:** 0
构成: comment 53 + mention 13 · 复审回复: 3 · 静默跳过: 62 · 列请示: 1(cc-switch)

## 🎯 复审回复（3 条，均先拉当前 head 实证）

1. **PR #85365**（PRATHAMESH75，fix(gateway) HERMES_BUNDLED_* 进 launchd/systemd）— 作者按我们早盘 verify（`_verify_85365.md` 指出的 hostile-char round-trip 缺失）补了 `test_systemd_unit_carries_hostile_chars_forward_round_trip`。已在声称 head `d1fc255f02` 核实：在位，bake 含 `%`/`"`/`\` 的指针 → 丢 wrapper env → regenerate → `Environment=` 行字节一致 + `_unit_environment_value` 恢复原值，与声称逐项吻合；follow-up 2（`HERMES_HOME`/`VIRTUAL_ENV`/`PATH` 转义）作者诚实说明仍 defer，现状确未修。结论 ACCEPT，已回最简确认。
   回评：https://github.com/NousResearch/hermes-agent/pull/85365#issuecomment-5803694165
2. **PR #86578**（kuehnberger，anthropic prompt cache policy 签名测试）— 作者 21:43 直接 @ 请我们检查最新 rebase。已核：head `fbdb2d88` 单 commit、纯测试（1 文件 +74）、mergeable 无冲突，rebase 干净，positional-`agent` 契约 guard 仍在。有一处内容漂移如实告知：8 月验证过的 exact `(False, False)` 元组断言在重写后变为 tuple-shape + 全 bool 检查，仍是有效 guard，不算回归。结论：rebase 正确，无阻塞。
   回评：https://github.com/NousResearch/hermes-agent/pull/86578#issuecomment-5803696776
3. **PR #65982**（fcavalcantirj，claude-agent-sdk provider，41 commits / +30k）— 回应我们今日 review 的三点（架构决策/新 pin 的 CI/13-13 证据）：作者已加阻塞式 `claude-sdk-packaging` CI job。已在声称 head `b3a77fd8` 核实：job 在 `.github/workflows/tests.yml:15` 在位（exact-head checkout、SDK-only 实装 + co-install + locked 测试 + SHA 校验）；`agent.claude_agent_sdk` 默认块在位（config 重构后搬到 `config_defaults.py`，内容完整）；pins 未变（0.2.144/2.0.0/httpx2/starlette）。三处剩余如实列出：① `mergeable_state` 此刻为 `dirty`（main 在作者 rebase 后又前进了，需再 rebase 一次）；② 新 workflow 仍 `action_required` 零 job，待维护者批准；③ in-tree vs standalone 架构 owner 仍未回。结论：证据接受，推进卡点不在作者侧。
   回评：https://github.com/NousResearch/hermes-agent/pull/65982#issuecomment-5803699804

## 列请用户定夺（1 条）

- **cc-switch #7382**：维护者 farion1231 14:34 已回——OpenCode V2 目前不稳定、breaking change 多，社区大量用户暂不升级，故**想等一段时间观察再考虑**（Deepseek harness 相关 PR 同理）。这是明确的 defer 决策，不是提问，未回。倾向：接受等待（我们 #7577 的实证 review 已贴，技术准备在案；触发器可定为"V2 稳定信号或一周后"再跟进）。是否现在回一条接受等待的确认、还是彻底静默，等你定。
  https://github.com/farion1231/cc-switch/issues/7382#issuecomment-5795838369（我们的 @ 排期请求）→ 维护者回复在后。

## 其余（62 条静默 Done，无需逐条回复）

- **scan 扫出的旧 pending 3 条**（kuehnberger 8-26，#86612/#87302/#86578 各一）：内容均为"AI review 已解决，请人类 maintainer 看"的转交语，@ 的是 teknium1/GottZ 等，仅顺带提到我们已验证，无向我们的提问；且 #86612/#87302 此刻 state 已为 **closed**，线程已死。一律备案不回。
- **订阅噪音**：其余 60 余条 ours=0（无一条是自己的 PR），latest 多为作者自更新（rebase/push/关闭事件）与第三方讨论，无新 @、无提问。抽样确认 closed PR 的关闭评论多为常规收尾。按 SOP 只归档不回。
- 顺序合规：`scan_pending_mentions` 先于标 Done ✓；未跑 `inbox_auto_sweep`（逐线程人工分类已覆盖）。

## 处置

66/66 标 Done（gh CLI 线程级 DELETE，失败 0）。评语草稿已归档 `reviews/hermes-agent-2026W38/rb/{85365,86578,65982}.md`。处理后未读经 `gh api notifications -q length` 确认 = **0**。

## 待跟进

- 延续：batch26 剩 19 条搁置，续跑通道未定（待用户定）。
- 新增观察：#65982 作者响应质量高（CI job 一次到位），卡点只剩 maintainer 侧（workflow 批准 + 架构 owner）；若维护者迟迟不批，可考虑是否由我们再 @ 一次——待用户定（非本批动作）。
- cc-switch：V2 适配线被维护者明确 defer；#7577 的技术 review 已在案，无需动作，等触发器。

# 第2批 · 2026-09-24（50 条）→ 已清零
**账号:** Enough1122 · **处理:** 50/50 标 Done · **处理后未读:** 0
构成: comment 43 + mention 7 · 复审回复: 3 · 静默跳过: 47 · 列请示: 0

## 🎯 复审回复（3 条，均先拉当前 head diff 实证,file:line 为 post-image 行号）

1. **PR #94413**（bbasketballer75,fix(gateway) Windows Docker media path 平移）— 作者按我们 9-14 复核的两项 open item 推了 `53b777e7b1` 并由 FriendlyCityJohnstown rebase 至 `85d4f61d06`(干净,无代码变更)。已在 head 逐项核实:①UNC 拒收三处边界全在位——`_parse_docker_volume_mounts` base.py:962、`_translate_docker_container_media_path` normpath 前后双重 guard :1083/:1087(POSIX normpath 保留双斜杠,复查必要)、`validate_media_delivery_path` :1139;②`posixpath.normpath` 先于 `/root/.hermes` credential guard 归一化,点段拼写绕不过;③`test_unc_sources_and_candidates_fail_closed` test_platform_base.py:988 + `@pytest.mark.windows_only test_windows_native_docker_media_path_translation` :1018-1019。结论 ACCEPT。
   回评：https://github.com/NousResearch/hermes-agent/pull/94413#issuecomment-5808198148
2. **PR #97344**（rodrigogs,fix(kanban) block 必须带 reason）— 作者 9-12 反驳我们"return code 2 是 breaking change 应加 release note"的 note:docs 已把 reason 写进调用契约、仓库无 CHANGELOG 约定。已对 upstream main 核实两项均真:kanban.md:397(overview 示例含 "need input")、kanban.md:958(CLI reference `<reason>`);根目录无 CHANGELOG.md(API 404)。结论:接受 docs-contract 框架,我方 note 过度保守,已回帖撤回致谢。线程内 Moep90 9-18 提的 dashboard 层 NULL-reason 缺口是作者与第三方的讨论(9-23 作者已回,不 @ 我们),不介入。
   回评：https://github.com/NousResearch/hermes-agent/pull/97344#issuecomment-5808199976
3. **PR #117902**（liusencomic-cyber,Volcengine Ark Agent Plan provider）— 作者按我们 9-21 的 live-network 测试意见在 `c432f5f3a1` 修复。已核:两个 fetch_models 测试均 monkeypatch `providers.base.open_credentialed_url`(HTTPError 404 :51 + URLError :64),断言 None,零网络 I/O。ARK_API_KEY 与 pay-as-you-go 共用属 in-tree 约定,回帖表示无异议。结论 ACCEPT。
   回评：https://github.com/NousResearch/hermes-agent/pull/117902#issuecomment-5808201872

## 其余（47 条静默 Done）

- **scan 扫出的 pending @ 4 条,3 条因线程已死不回**:84121/91240 两条 "Status nudge"(FriendlyCityJohnstown 模板催审,引用我们旧 review 要求确认)——两个 PR 此刻均已 **closed 未 merge**,nudge 失效;86195(西语 locale 译注,8-16)——PR 已 closed。均为收尾类。
- **117091**:youyoutu405-source 的第三方验证报告(确认我们 9-20 review 的 point 1,并加码发现 sweep 级 rollback + 重复投递路径,提出贡献回归测试)。通读全文无向我们的提问,对象是 PR 作者/维护者;按克制口径不介入,备案。
- **订阅噪音 43 条**:ours=0,latest 为作者自更新/推送事件/第三方讨论(closed 收尾居多),无新 @、无提问。抽样确认后 Done。

## 处置

`scan_pending_mentions` 先行 ✓(7 条 pending 全部分类)→ `inbox_auto_sweep` 清 19 条纯告知(fail 0)→ 其余集合级 `PUT /notifications` 清零。处理后 `gh api notifications` 确认 = **0**。回评草稿归档 `reviews/hermes-agent-2026W38/rb/{94413,97344,117902}.md`(117902 追加,另两个新建)。

## 待跟进

- 延续:batch26 剩 19 条搁置,续跑通道未定(待用户定);#65982 卡 maintainer 侧(workflow 批准 + 架构 owner)。
- 延续:cc-switch #7382 维护者 defer,等触发器(第1批列请示项,用户未裁,继续挂起)。
- 观察:youyoutu405-source 连续两轮在 #117091 做高质量独立验证并两次提出贡献边界回归测试(`test_worker_pid_recycled_boundary.py`,10/10 过)——若作者/维护者接,与我们 9-20 的 point 1 修复建议同一方向;暂无需我们动作。

# 第3批 · 2026-09-24（28 条）→ 已清零
**账号:** Enough1122 · **处理:** 28/28 标 Done · **处理后未读:** 0
构成: comment 23 + mention 5 · 复审回复: 0 · 静默跳过: 28 · 列请示: 0

## 🎯 复审回复
无。本批 scan 扫出 pending @ 2 条,均为 **disposition 收条**,不构成复审前提:
- **#86198 / #87264**(Diaspar4u,08-23 同日两条):`@Enough1122 Final disposition: informational only; no change required.` 附 head sha 与"哪个 PR 是 canonical"的界定(#51839 相邻而非取代 / #85176 的 fail-closed 分类保留)。纯告知,不回。两线程其后评论(09-05、09-08)均指向 @teknium1 / @alt-glitch 求 review 与 workflow 批准,与我们无关。

## 盲区补看(本批新增动作)
对"最新 issue 评论早于今日 updated_at"的 11 条线程补查 `/pulls/{N}/reviews` 与 `/pulls/{N}/comments`(inline)——仅 **#18188** 有 review(teknium1 7-12,早于我们 9-20 的回评,已闭环),其余 10 条零 review 零 inline;今日更新为 push/rebase 事件,无新发言。

## 作者回应我们 review 但未 @ 我们(2 条,静默归档)
- **#92620**(wodesiku,08-23):回应我们 08-23 review——接受 point 1&3 并已实装 `_MAX_DELEGATE_PROVENANCE_HOPS = 16`(有界 for + else 失败关闭,含 acyclic 越界测试),point 2(missing-parent UX)说明不采纳理由。无提问、无 @,不介入。
- **#106841**(jamalkamaladdin,09-10):答我们"locale 完整性检查"非阻塞 note——`web/src/i18n/az.ts` 以 `Translations` 类型在编译期强制键完整,占位符与 en 一一对应。属对 review 的答复而非求裁决,不回。

## 其余（26 条静默 Done）
- **已关/被取代收尾 8 条**:87804→#121195(已 merge,cherry-pick 保署名)、94544→upstream 6fe933e(credited)、95035→#99520、95386→#120321、91234→#120175、105903→#121153(误关已恢复)、103690→#104567、103002→#121046。
- **维护者 rebase heads-up 2 条**:88863、103407(teknium1 通知作者 #121060 改了同一批 desktop 渲染文件)——对象是作者,非我们。
- **作者自更新/播报 9 条**:83997、72761、99527、84926、106221、94768、93249、86198(09-05)、87264(09-08)——rebase 说明 + 测试计数 + 求 maintainer 批 workflow,无向我们提问。
- **第三方讨论 1 条**:103965(jagosan 回 ghosttigerllc-bit,界定 scope、后续另开 PR 处理 #85700)。
- **我们自己的 review 是线程最后一条 6 条**:105159、89399、89000、89262、18188、87117——今日仅 push 事件,无人回应待处理。

## 处置
`scan_pending_mentions` 先行 ✓(2 条 pending 分类)→ 未跑 `inbox_auto_sweep`(28 条已逐条人工分类,无需脚本兜底)→ 集合级 `PUT /notifications` 清零。处理后 `gh api notifications` 确认 = **0**。本批无回评,无草稿需归档。

## 待跟进
- 延续:batch26 剩 19 条搁置,续跑通道未定(待用户定);#65982 卡 maintainer 侧。
- 延续:cc-switch #7382 维护者 defer,等触发器(第1批列请示项,用户未裁,继续挂起)。
- 新增观察:#92620 作者对我们 review 的三点已两点实装、一点说明理由,若日后有人再推该线程可一句话收尾;当前无 @,不动。

# 第4批 · 2026-09-24（15 条）→ 已清零
**账号:** Enough1122 · **处理:** 15/15 标 Done · **处理后未读:** 0
构成: comment 14 + author 1 · 复审回复: 0 · 静默跳过: 15 · 列请示: 0

## 其余（15 条纯告知类）
- **作者自更新/rebase 告知 2 条**:#86018(goetterbote2342 重写到 main fd552bf,吸收 sync-flow 重构,保留 resume-token 守卫+60s heartbeat)、#77429(OutThisLife 补充 duplicate #88393)。均无 @ 我。
- **第三方讨论 1 条**:#98660(OutThisLife 回 maintainer 口径:"Holding this one",指 PR 的 `'transparent'` boot 背景首帧露玻璃层、`applyTheme` 加阻塞 `sendSync`,已在 #98561 要 frame capture)。与我们无关。
- **已关 PR 收尾 4 条**:#116422、#116409、#116399(tobenwarrior desktop plugin 三连,已 close)、#87727(derinbarutcu17,已 close)。
- **sweep 自动清理 8 条**(纯告知/噪音,详见 `_inbox_sweep_log.jsonl`)。

## 处置
`scan_pending_mentions` 先行 ✓(0 pending)→ `inbox_auto_sweep` 清 8 + 人工 DELETE 线程 7(全 OK,无失败)。处理后 `gh_inbox.py` 确认 = **0**。本批无回评,无草稿需归档。

## 待跟进
- 延续:batch26 剩 19 条搁置,续跑通道未定(待用户定);#65982 卡 maintainer 侧;cc-switch #7382 维护者 defer 继续挂起。
- 无新增阻塞。
