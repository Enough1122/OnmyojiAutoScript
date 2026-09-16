# HERMES 重装指南 × 状态交接

_2026-09-16 · 本文件给"重装后的 Hermes"读_

> **给未来的 Hermes**:这是用户 2026-09-16 完成的「干净化 / 默认化 / 官方默认化」行动的完整交接单。
> 用户意图 = **官方默认 + 用户记忆 + 工作空间 + 少量专门设置**。除此之外的历史包袱一律不要恢复。
> 读完后:按 §3 核对/重建专门设置 → §4 确认不做的事 → §5 验收。

## §1 一句话背景

用户决定「重新训练、从头再来」:把历年积累的自定义(用户侧 95 个 skill、全部技能备份、记忆中的历史痕迹)全部清零,并**重装 Hermes 回到官方默认**。本文件是重装后唯一需要读取的交接物。

## §2 重装前必须搬走的 6 件(源:`C:\Users\admin\AppData\Local\hermes\`)

> 重装前先把它们拷到临时目录;重装后按下表放回。若安装器保留了旧数据(非全新环境),则只需核对。

| 文件/目录 | 重要性 | 说明 |
|---|---|---|
| `memories/` 的 `MEMORY.md` + `USER.md` | ★★★ | **用户的记忆,不搬就永久丢失** |
| `.env` | ★★★ | 全部密钥(飞书 / OpenCode Go+Zen / 商汤 / 百度 / mx / GitHub…)。搬回后删掉十几个死键(`WEIXIN_*`、`HINDSIGHT_*`、`*_TOOLS_DEBUG`) |
| `cron/jobs.json` | ★★ | 9 条定时任务完整定义(见 §3.5) |
| `scripts/`(整个目录) | ★★ | cron 转发壳脚本;真正业务脚本在 `D:/Hermes/scripts/`(随工作空间) |
| `config.yaml` | ★ | 备用参考;只需恢复 §3 列出的区块 |
| `auth.json` | ★ | OAuth 凭据(可选,搬回可免重新登录) |

## §3 重装后重建的「专门设置」(仅这些)

### 3.1 模型接线(必须)
```yaml
model:
  provider: opencode-go
  default: deepseek-v4.1-flash
  base_url: https://opencode.ai/zen/go/v1
  api_mode: chat_completions
```
- `custom_providers`:**Token.sensenova.cn**(base_url `https://token.sensenova.cn/v1`,模型含 sensenova-6.8-flash-lite / deepseek-v4-flash / glm-5.2 / kimi-k3 等;api_key 见商汤后台或旧 config.yaml)
- `providers.igg-paid`:**IGG 公司 relay**(base_url `https://crs.skyunion.net/v1`,模型 claude-opus-5 / cc-deepseek-v4-flash 等;key_env `HERMES_CUSTOM_IGG_PAID_API_KEY`)
- **fallback 必须保持空链**(用户原则:不信任 fallback;未经明确要求不得添加)
- 切模型:`hermes config set model.default <x>` + `model.provider <y>`;注意模型按会话钉定,旧会话要 `/model` 或 `/new`

### 3.2 飞书通道(必须)
```yaml
platforms:
  feishu:
    enabled: true
    home_channel: {platform: feishu, chat_id: oc_533d3573e87e60cfab2c37aa66c4d1f4, user_id: ou_3d6066e1fa2bc452341ad4813ab4103c}
display:
  platforms:
    feishu: {streaming: true, show_reasoning: false, tool_progress: new}
```
- `.env`:`FEISHU_APP_ID` / `FEISHU_APP_SECRET` / `FEISHU_HOME_CHANNEL` / `GATEWAY_ALLOW_ALL_USERS`
- 平台侧配置只显式开需要的,其余保持官方默认(用户偏好)

### 3.3 记忆(必须)
- `memories/MEMORY.md` + `USER.md` 放回原位;`memory.provider` 保持默认 `''`

### 3.4 工作环境(建议)
- `terminal.cwd: D:/Hermes`
- 时区:`.env` 里 `HERMES_TIMEZONE`(Asia/Shanghai)
- 浏览器:`browser.use_real_profile: true`(用户 2026-09-14 点头过)

### 3.5 定时任务 9 条(拷回 `jobs.json` 即全恢复)
| 任务 | 日程 | 形式 |
|---|---|---|
| 减重周计划 | 周一 9:30 | agent,投飞书 |
| 记忆清理 | 周一 3:00 | script `mem_audit.py` |
| 华通每小时买卖分析 | 工作日 10-15 点 | script `ht_report.py`(零 token) |
| 华通策略回溯 | 每 3 天 16:00 | script `ht_backtest.py` |
| 会话清理 | 周日 3:00 | script `clean_sessions.py` |
| AI 圈大新闻早报 | 每天 8:30 | agent,投飞书 |
| OAS 看门狗 | 每 5 分钟(停用) | script `oas_watchdog.py` |
| OAS 早 6 点停 | 已完结(停用) | — |
| 工作空间备份 | 每天 23:00 | script `backup_life.py` |

### 3.6 其余一切
approvals / checkpoints / tts / display 杂项 / compression / moa / MCP / 自定义 toolsets… **全部保持新装官方默认即可,不重建。**

## §4 明确不要做的事(用户立场)

1. **不装回**:旧的用户 skill 库(95 个已全删、不保留备份)、官方可选包 ascii-art / comfyui(除用户点名)、任何「保险包 / 回滚包 / _archive」
2. **不建**:用户已明确删除的东西的备份(删了就删了)
3. **官方 skill 保持原样**:45 个 builtin 默认件,不修改
4. **非官方默认的新东西尽量不引入**(用户的「官方默认化」方向)

## §5 验收基线(重装后自检)

- `hermes skills list` → **45 个 builtin、0 hub-installed、0 local**
- 定时任务:`cron/jobs.json` 里 `jobs` 数组长度 = **9**
- 记忆:`MEMORY.md` 有内容(体重史 / 偏好 / 生活事实)
- 模型:`hermes status` → provider = `opencode-go`,model = `deepseek-v4.1-flash`
- 飞书:能正常收发消息(流式开)

---
_工作空间本体见 `README.md`;本文件在 `D:/Hermes/` 随 git 管理。_
