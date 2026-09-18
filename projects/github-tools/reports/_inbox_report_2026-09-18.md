# 2026-09-18 战报

## 收件箱 · 上午批次(111 条)→ 已清零
**账号:** Enough1122 · **处理:** 111/111 标 Done · **处理后未读:** 0
构成: comment 104 + mention 7 · 复审回复: 1 · 打捞处置/立场说明静默清: 4 · 收条/杂项: 其余 · 列请示: 0

### 🎯 复审回复
- **#109044** feat(agent): adaptive reasoning effort(auto)(patrykkopycinski,head `1826d102ef`)——**部分放行**:①我们 9/12 指出的 user-message-less 循环 pin 失效已按建议修复(`pinned_sig == sig` 覆盖 None==None,注释说明动机,两个新测试钉住行为);②作者声称 "`_reset_auto_effort_pin` still resets on model switch/resume" 不实——全 PR diff 内该 helper 只有定义和测试调用,`/model` 选择器 hunk 只加选项未接 reset:定时任务流(sig 恒 None)模型切换后旧 effort 永久钉住。已要求接线或撤回声明。回评:https://github.com/NousResearch/hermes-agent/pull/109044#issuecomment-5724620853

### 静默清空(打捞处置类,均无提问)
- #84201 / #90786(kshitijk4poor):环境标记泄漏两 PR 打捞进 #114312,对我方 point 1 的处置已说明(bash 契约测试替代 import 常量),已关原创关。
- #104781(kshitijk4poor):launchctl 正则锚定已打捞进 #114208 并合并(main 61e730cc),我方 sibling 模式备注核实"grep count 1"属实。
- #87627(erinem808 + claude-ct):Revell plugin-index 种子仓立场说明(愿移交/愿删),信任边界决策留给维护者,非我方裁决项。

### 处置
Done 111 / 失败 0 / 复审回复 1 / 列请示 0。

## 续战 · 100 条战役批次二(5×20 子代理并行,frontier 113308 → 113897)
**活检:** 100/100 存活 · **发帖:** 8(2 blocker + 6 非阻塞)· **静默 CLEAN:** 91 · **SKIP 超限:** 1(113500,146KB)
8 条 FINDINGS 均经主流程 diff 实证后才发(113496 的 2-tuple mock 在 main :41 亲自核对;113522 的 eval 调用方在 main 亲自核对)。

### 已发(8 条)
| PR | 级别 | 发现 |
|---|---|---|
| 113496 | **blocker** | `send_final_ledgered` 改 3-tuple 但未更新的 `tests/gateway/test_diagnostic_wake_presentation.py:41` 仍 mock 2-tuple——合并即 ValueError;另 TTS-caption 失败义务可被重连扫重发成重复文本 |
| 113522 | **blocker** | `spawn_background_process` 新增无默认值的 keyword-only `completion_linger_seconds`,未更新的 `evals/gateway_completion/delivery_lifecycle.py:63` 调用即 TypeError;与 #113520 同改 onboarding.ts 同一 `if (runtime.ready)` 块,必然冲突 |
| 113309 | 非阻塞 | `steer()` 把每次中途插话无条件写成持久 "preference",50 条 FIFO 每次压缩全量重放,一次性叮嘱变长期指令 |
| 113345 | 非阻塞 | `_in_test_context` 自识别臂用 `"pytest" in str(arg)` 自由子串扫全 argv:生产 `-q "fix my pytest tests"` 被误判测试上下文,踩 fail-closed 生产 home 拒绝 |
| 113327 / 113334 | 非阻塞 | 同改 `_on_summary_failure`(~:3518)与 `test_compressor_truncated_summary_guard.py` 的竞品对,必然冲突,请维护者二选一(113334 更完整) |
| 113566 | 非阻塞 | `cron stop` 在两个可达窗口(注册前构造期/legacy 无 fire owner 路径)做了真实标记(bookkeeping+last_status=interrupted)却按 `interrupted==0` 报 "not currently running" |
| 113567 | 非阻塞 | `_sentences` lookbehind 从 `[.!?]` 扩到 `[.!?\]]`:句中隔空引用("Smith [3] argues")被切碎,<4 词碎片被丢,覆盖率统计失真;`(?<=[.!?]\])` 即可匹配声明意图 |

### 静默 CLEAN(91 条)
chunk2/4/5 全 CLEAN(60 条,含子代理实下载 hindsight-client 0.10.0 wheel 验证强制升级兼容、process_group/killpg 契约、_parents_satisfied 集合核对等 head 实证);chunk1 16 条、chunk3 15 条。代表性 borderline 留档:113445(Windows 下 sig 退化 mtime+size,核心场景仅 POSIX 全覆盖)、113606(同 session 并发流共享 notifier 槽)、113883(Buzz 回填缺 [unverified] 信任标签)。

### 流程观察
- 两条 blocker 都是"改契约没扫全调用方/测试"同一类:发布前以 main 现状核对调用方,是本次拦截的关键动作。
- 竞品冲突对两批连续出现(昨日 2 对,今日 1 对),同批扫描的价值。
- 断点落盘:frontier=113897、累计 posted 3606、progress.txt 记 100 行、clean 草稿 91 份归档。

# 第3批 · 2026-09-18 下午（48 条）→ 清至 1(有意保留)

**账号:** Enough1122 · **处理:** 47/48 标 Done · **处理后未读:** 1(#93730 列请示)

## 🎯 复审回复(4,均实证 head 后发)
- **#91186** fix(gateway): taskkill /T /F escalation(bbasketballer75,head `b9ed394e7f`)——**放行**:我们 9/14 指出的 TimeoutExpired 逃逸已修:force=False 升级路径 `except subprocess.TimeoutExpired → OSError("taskkill fallback timed out")`,force=True taskkill 同步补齐;`test_force_false_taskkill_fallback_timeout_raises_oserror` 钉住 OSError 契约。https://github.com/NousResearch/hermes-agent/pull/91186#issuecomment-5728281913
- **#110253** fix(gateway): async pre-dispatch hooks(KoNit-K,head `fe5d2c824b`)——**放行**:rebase 后无回归:`pre_gateway_dispatch` 在共享超时集,`invoke_hook_async` 以 `asyncio.wait_for` 封顶并 fail-open,陈旧注释已更新,`test_async_pre_gateway_hook_times_out` 钉住取消。https://github.com/NousResearch/hermes-agent/pull/110253#issuecomment-5728284616
- **#113102** fix(peer): timed-out DM is a slow answer(jonpol01,head `a1e9d944fe`)——**放行**:采纳我方 phase 分析:仅 bare TimeoutError 且 session 已解析报 "accepted…Do NOT resend",URLError 包装回落 unreachable;新增 real-opener 双 phase 测试钉住两条签名。https://github.com/NousResearch/hermes-agent/pull/113102#issuecomment-5728287602
- **#91742** fix(agent): stamp type=message(huanshan5195,head `6115dfc8b9`)——**放行**:re-port 后 typeless 缺陷闭合,`_role_message_item` 统一出口、status 仅 assistant、user 项弃 id/phase 有文档化理由;作者"非三行改动"论据(preflight 按 type 分发)经 diff 证实。https://github.com/NousResearch/hermes-agent/pull/91742#issuecomment-5728290834

## 列请用户定夺(1)
- **#93730**(AI-Mart 9/9 @):催促"尽快 review 尽快合并"。非作者、无技术问题、无修改声明;connorblack 9/12 已做深度 review(3 gaps,作者已修)。按克制发声不回;线程保持未读待裁决。

## 处置
- sweep 清 29(纯告知);人工清 18(7 条 teknium1 关闭摘要 superseded/declined、2 条 ugoi 打捞告知、#113494 仅 credit 提及、其余第三方 +1/复现确认/催合 @teknium1);复审回复 4;列请示 1。失败 0。

## 流程观察
- gh api DELETE 端点在 Git Bash 下须去前导斜杠(`notifications/threads/{id}`),带 `/` 会被 MSYS 路径改写——此前批次未踩过,记入 SOP 备查。

## 续战 · 100 条战役批次三(5×20 子代理并行,frontier 113897 → 114080)
**活检:** 100/100 存活 · **发帖:** 12(2 blocker + 10 非阻塞)· **静默 CLEAN:** 47 · **SKIP_STALE:** 38 · **SKIP 超限:** 3(113904 120KB、114026 fork-sync 7.7MB/1816 文件、114074 5.3MB)
12 条 FINDINGS 均经主流程 diff 实证后才发;两条 blocker 由主流程逐行复核分支结构/解析逻辑后确认(113967 的 `if session is not None` 早退使 config 侧驱逐不可达,作者自己的注释与分支序矛盾;114025 的 `split(";")[0]`+盲目 `http://` 前缀把 Windows per-protocol 格式变成 `http://http=host:port`,测试只钉了 Windows 不用的全协议形式)。

### 已发(12 条)
| PR | 级别 | 发现 |
|---|---|---|
| 113967 | **blocker** | MCP session-None 宽限重构使 live-session 服务器的 config 移除/禁用/路由变更驱逐全部不可达:被移除服务器保留工具 overlay(配置即 allowlist),route-fingerprint 防异凭证借用守卫在共享连接存活期间失效;作者注释"Config-side reasons still evict immediately"与分支序矛盾 |
| 114025 | **blocker** | Windows 注册表代理探测:`http=h:p;https=h:p` per-protocol 格式经 `split(";")[0]`+盲目前缀 → `http://http=h:p` 直传给 bot,全部平台发送解析失败;同主机此前直连可用 → 回归;ProxyOverride 绕过表也未读 |
| 113903 | 非阻塞 | keyless 403 failover:页面级 403(目标站被封)触发全环漫游掩盖真实 per-URL 错误;`\b403\b` 命中目标 URL 路径;与 #113900 同 hunks 冲突 |
| 113912 | 非阻塞 | buzz edit 独立 argv 形式:内容以 `-` 开头被当选项旗标;与 #113918 同 hunk 冲突(其 `--content=` 等号形式更稳) |
| 113938 | 非阻塞 | cron reap 前置正确,但共享 assert 块落进新测试,原 async 路径"先恢复后认领"断言丢失 |
| 113975 | 非阻塞 | SKILL.md 内联 shell 改用 served_profile_child_env 后,UnscopedSecretError 可逃出只捕 TimeoutExpired 的 try,违反 run_inline_shell 永不抛出契约(窄窗口,请作者确认) |
| 113989 / 113996 | 非阻塞 | #113980 locale 跟随 profile 的双胞胎修复(不同作者,相隔 11 分钟,同 hunks 必冲突);113996 更完整(generation guard+竞态测试),请维护者二选一 |
| 114016 | 非阻塞 | 描述符池退役:owned-but-unfenceable 条目永不可回收(reachability 待确认);prepare() 无期限 await connectionPromise,挂死连接每 tick 积累一个 pending promise |
| 114044 | 非阻塞 | skill-count 缓存去掉 TTL 后,既有 skill 目录内 SKILL.md 增删不改类目 mtime,签名永不失效,错计数持续到重启;建议留长兜底 TTL |
| 114045 | 非阻塞 | 根目录误提交 PR1_body.md/PR2_body.md(两个无关 PR 的草稿) |
| 114077 | 非阻塞 | 应用级熔断按"最近一次撞击工具"单值记录:两个坏工具交替调用互相解锁,≥2 坏工具服务器上 #10447 防风暴被完全绕过;建议 per-tool 集合 |

### 静默 CLEAN(47 条)
五个 chunk 全部对 main 做了实证核对(escape_like/ESCAPE 配对、oauth 键与 ${VAR} 插值、_RUNTIME_MAIN_CONTEXT 存在性、上游 tag 与 commit 对应、 vitest onTestFinished 可用性、is_explicit_fork_child 经 mixin 存在等)。代表性 borderline 留档:114023/114040(初判 POSTED 后经主线程核实改判 CLEAN:stars NaN 安全、UTF-16 预算会计无误)、114076(能力锁存于 per-send shell,rich 无能 bot 每次发送多一趟注定失败的 roundtrip)、114006(eager 空会话行 reintroduce untitled-litter 风险,已有 cap 执行兜底)、114013(子串匹配可能把真 ValueError 误判 retryable,重试成本有界)。

### 流程观察
- 本批 0 个 SKIP_STALE 误报;38 条 stale 与活检全 100 存活说明候选快照时效良好。
- 双胞胎修复对再次出现(113989/113996,继昨日 2 对后第 3 对):同 issue 短窗口撞车已成常态模式。
- gh api DELETE 前导斜杠 MSYS 改写坑已记入战报(本批收件箱环节踩到)。
- 断点落盘:frontier=114080、累计 posted 3618、progress.txt 记满 100 行、clean 归档 47 条、rb/ 新增 15 份(12 posted + 3 复审回复)。
