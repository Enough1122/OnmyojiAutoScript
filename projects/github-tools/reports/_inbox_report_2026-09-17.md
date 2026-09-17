# 2026-09-17 战报

## 收件箱(上午,临时流程)
109 条全部标已读;定向回复 3 条:#98616(裁决 here-or-follow-up)、#72637(核实 KeyArgo 追踪属实,支持折入)、#84236(核实 3 点已修,发现缺 schema-history 事件,要求补)。回评链接见对应 PR 线程。注:本轮未按 SOP 脚本走,scan/sweep/战报格式当日已按新 SOP 修订。

## 续战 · 10 条实战批次(SOP v2026-09-17 首跑)
**frontier:** 112810 -> 112836 · **发帖:** 5 · **静默 CLEAN:** 5 · **SKIP_STALE/DUPE:** 0
5 路子代理并行审稿,主流程质检抽查(2 条声明逐条坐实)后 post_one.py 串行发布。

### 已发(全部非阻塞发现,blocker 0)
| PR | 标题 | 发现 | 链接 |
|---|---|---|---|
| 112811 | feat(dashboard): plugin Config sections | post-mount setLoading 抬升重挂 chat host 可杀 PTY(非阻塞) | https://github.com/NousResearch/hermes-agent/pull/112811#issuecomment-5708266194 |
| 112813 | feat(buzz): reconcile joined channels | subscribe_discovered 活迭代 _channel_state 跨 await,并发变异炸 read loop(非阻塞) | https://github.com/NousResearch/hermes-agent/pull/112813#issuecomment-5708267943 |
| 112825 | feat(browser): lazy-launch Chrome | 拉起失败路径泄漏 detached Chrome(非阻塞) | https://github.com/NousResearch/hermes-agent/pull/112825#issuecomment-5708269963 |
| 112834 | fix(desktop): forced wake reconnects | wake skip 依赖 close 事件,half-open 副连接可悬挂至 30min 超时(非阻塞) | https://github.com/NousResearch/hermes-agent/pull/112834#issuecomment-5708271820 |
| 112836 | fix(desktop): preview tab closed on replay | 关闭标记全局且永久,回收端口/路径的新开预览被静默吞(非阻塞) | https://github.com/NousResearch/hermes-agent/pull/112836#issuecomment-5708273475 |

### 静默 CLEAN(核验后未发帖,记 reviewed_clean)
112821(kanban 只读守卫)、112823(RPC stdin 继承)、112826(stdio handler 崩溃韧性)、112829(usage 配额显示)、112831(buzz NIP-10 锚点)——各留 1 条 borderline 备注未达发帖门槛。

### 流程观察
- 发布门槛工作正常:50% 静默率,零噪音帖。
- 断点落盘:reviewed_clean/posted/frontier 均已更新。
- 待办:inbox_auto_sweep.py 仍缺 pending 防护;post_one.py 无 SKIP_CLEAN 判定(本次由 agent 把关)。

## 收件箱 · 下午批次(SOP v2026-09-17,70 条)→ 已清零
**账号:** Enough1122 · **处理:** 70/70 标 Done · **处理后未读:** 0
构成: comment 64 + mention 6 · 复审回复: 1 · 静默跳过: 0 · 列请示: 0

### 🎯 复审回复
- **#95238** fix(install): stop shipping a mirror(Finn763,head `fa131a6bd7`)——作者按我们 8/26 的 review 撤回镜像硬编码设计:mirror 表与匿名反代(ghfast.top/gh-proxy.com)全删,Electron/clone/PyPI 全部 canonical-first,被墙路径只提示用户自带 opt-in(UV_INDEX_URL / PIP_INDEX_URL / insteadOf / ELECTRON_MIRROR),并新增 guard 测试 `test_install_canonical_endpoints_only.py` 防回归。三点逐一实证通过;UV_NO_CONFIG 文档声明与 install.sh:33/2001 相符。报 2 条非阻塞文本残留:install.sh:3645 幽灵注释("mirror fallback above"已不存在)、install.ps1:4283 "(see the hint below)" 悬空(PS 路径无对应提示,sh 侧有)。回评:https://github.com/NousResearch/hermes-agent/pull/95238#issuecomment-5713295369 。作者向维护者提问"是否连 opt-in 钩子也不留"——非我方裁决事项,未代答。

### 其余
- mention 盲区补看:其余 5 条 mention 线程(#92122/#99730/#104068/#94341/#98616)逐一核 `/pulls/{N}/reviews` 正文,均无 @Enough1122,无漏。
- 64 条 comment 线程:作者关闭摘要/致谢/CI 播报/第三方互评等纯告知类,按 §1.2 全部静默标 Done,抽样无异常。

### 处置
Done 70 / 失败 0 / 复审回复 1 / 列请示 0。

### 流程观察
- 两个 gh CLI 坑(已绕过,记录备用):① Git Bash 会把 `-X DELETE "/notifications/threads/{id}"` 的前导斜杠改写成 `C:/Program Files/Git/...`——端点必须不带前导斜杠;② python 生成的线程 ID 清单带 CRLF,`while read` 循环须先 `tr -d '\r'`,否则 70 条全 FAIL。
- 本批未动续战(frontier 112836 维持),仅收件箱。

## 收件箱 · 傍晚批次(12 条)→ 已清零
**账号:** Enough1122 · **处理:** 12/12 标 Done · **处理后未读:** 0
构成: comment 11 + mention 1 · 复审回复: 1 · 静默跳过: 0 · 列请示: 0

### 🎯 复审回复
- **#110253** fix(gateway): await async pre-dispatch hooks(KoNit-K,head `a973e39a2c`)——作者按我们 9/14 的 review 修复:pre_gateway_dispatch 加入 callback-timeout 集(plugins_dispatch.py:46),异步路径全部经 `asyncio.wait_for` 兜底、超时取消后 fail-open(:267-286),陈旧注释同步更新,新增取消行为回归测试(tests/gateway/test_pre_gateway_dispatch.py:127-143)。逐条实证通过。回评:https://github.com/NousResearch/hermes-agent/pull/110253#issuecomment-5714886142

### 处置
Done 12 / 失败 0 / 复审回复 1 / 列请示 0。

## 续战 · 100 条战役批次(5×20 子代理并行,frontier 112836 → 113308)
**活检:** 100/100 存活(open、非 draft、零关注)· **发帖:** 17 · **静默 CLEAN:** 81 · **SKIP 超限:** 2(113027 162KB、113306 112KB)
草稿全部落 `Temp/opencode/campaign/`,已发+clean 均归档 `reviews/hermes-agent-2026W38/rb/`;主流程对 17 条 FINDINGS 逐条实证后才发。

### 已发(17 条;1 blocker + 16 非阻塞)
| PR | 级别 | 发现 |
|---|---|---|
| 112931 | **blocker** | 新增流式稳定性测试必然失败:`slice(0, lastIndexOf('R$')+1)` 保留裸 `R$` 尾,与自家 escape 规则的 `R\$` 前缀断言矛盾(代码与注释"cut before the second `$`"自相矛盾);另 `isCurrencyCodeDollar` 可逃逸 `$R$ 5` 型数学闭 `$` |
| 113006 | blocker 候选 | MS365 Planner `update_tasks`/`create_tasks` 只发 `SimpleNamespace(title=...)`:body-only 更新 patch `title:null`、其余已验证字段全丢弃;全插件唯一无测试写路径 |
| 113240 | 非阻塞 | WAL self-heal 窗口期借出的读连接归还后仍钉在已删 generation:进程残留 deleted-inode 持有者,foreign-opener 拒绝可长期持续 |
| 113026 | 非阻塞 | session→process cwd 切换触发 mountable 翻转:拆活沙箱、Desktop 选定挂载丢失(测试只盖反方向);`cleanup_vm` 移除疑似 VM 后端回归 |
| 113102 | 非阻塞 | `_is_read_timeout` 把 URLError 包裹的 connect 超时判为"已送达勿重发":peer 在 session 解析与 chat POST 之间宕机 → DM 静默丢失 |
| 113192 | 非阻塞 | `_send_email` 的 `_new_reply` 在 try 外(对照 `_send_with_files` 在内):异常后引语永久卡 "pending";`_last_original_by_sender` 无淘汰 |
| 113252 | 非阻塞 | `_shadow_state_metrics` 只写不逐(64 上限只管 `_shadow_state_prev`),与"bounded stores"注释矛盾 |
| 113308 | 非阻塞 | scrub 集漏 `SLACK_ALLOWED_USERS`(strip 集有):两策略集不一致,单独用 scrub 集的消费者仍泄漏 allowlist |
| 113231 | 非阻塞 | vault 表单 `requestSubmit()` 后无条件报 `submitted: true`:站点 JS preventDefault 时模型空等 |
| 113003 | 非阻塞 | cache 自愈未接入 TUI 分支;与 #113001 重叠(共享 6 函数逐字节相同,本 PR 为超集) |
| 113011 / 113014 | 非阻塞 | 同功能竞品对(`session.pinned.*`),同改 8 文件必然冲突,各自发评请维护者二选一 |
| 113001 | —(clean,重叠备注留档) | 与 #113003 重叠 |
| 112989 | 非阻塞 | 主后端自动恢复无退避/上限:ready 即重置 claim,ready→die→restart 无限循环 |
| 112925 | 非阻塞 | 并行平台加载:跨线程 re-enter 注册表时同线程递归守卫失效,`event.wait()` 无超时可死锁(条件性) |
| 112926 | 非阻塞 | 新 import-cost 探针读操作者真实配置且无隔离:开了 entry-point 插件的主机必红 |
| 112937 | 非阻塞 | browser_exec 的 stay-put 栅栏只做准入(`run_fenced` 传 no-op lambda),与 `_run_browser_command` 的 mid-command epoch 检查分叉 |
| 112975 | 非阻塞 | `stt.deepinfra.timeout/max_retries` 静默失效:deepinfra 委托未传 `config_section`,客户端设置回落 `stt.openai` 而 model/base_url 读自己的 section |

### 静默 CLEAN(81 条,各留 borderline 备注于归档草稿)
chunk1 全 20 条无实质缺陷(目录 yaml、安装器、kanban 身份、copilot token 新鲜度等均实证);chunk2-5 清单见 `progress.txt`。代表性 borderline:112868(修复后未重跑 workspace install,构建可能晚爆)、112903(空闲阈值后任何命令先重置 session,/status 读到新会话)、112841(重试总预算 ~4x 增长,cron 投递预算需覆盖)、112841 docstring ±25% 与实现 +0..25% 不符。

### 流程观察
- 发布门槛执行良好:100 条里 81 静默,17 发帖全部经主流程对 diff 实证(112931 的 blocker、112937 的"双路径分叉"、113003 的字节级重叠均为我方抽查确认后才发)。
- 子代理 1 条误报被拦截在发布前:chunk2 汇总曾称 112937"无 mid-command epoch check",草稿实为"browser_use_cli 路径未包围栏"——以草稿为准,属实发布。
- 断点落盘:frontier=113308、posted 3598 累计、reviewed_clean 追加 81、progress.txt 记 100 行。

## 收件箱 · 夜间批次(4 条)→ 已清零
**账号:** Enough1122 · **处理:** 4/4 标 Done · **处理后未读:** 0
构成: comment 2 + mention 2 · 复审回复: 1 · 收条清空: 1 · 静默跳过: 0 · 列请示: 0

### 🎯 复审回复
- **#101773** fix(skills): preserve picker install identities(KoNit-K,head `2a1f1d7336`)——**部分放行**:①标识缺失拒绝+回归测试属实(skills-hub.tsx 监听器强制 `data.identifier`、去 name 回退;新测试钉住 name-only pick 不触发 install);②作者声称的 "Install unavailable: missing canonical identifier" toast **在 head 不存在**(hermes-bots 目录 134 个 ts/tsx 全扫无此文案,拒绝路径为裸 `return`),唯一 "Install unavailable" 在 website 卡片按钮上——陈旧缓存页恰好看不到,正是原 nit 针对的场景。要求补 toast 或声明静默丢弃为有意。回评:https://github.com/NousResearch/hermes-agent/pull/101773#issuecomment-5715102486
- #110253(KoNit-K)对上轮验收的确认收条,按 §1.2 直接清空,不再回。

### 处置
Done 4 / 失败 0 / 复审回复 1 / 列请示 0。
