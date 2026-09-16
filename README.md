# D:/Hermes 工作空间

个人资料唯一真源（真源直管版控，不做镜像）。本目录自身即 git 仓，每日 23:00 自动 `git add -A → commit → push` → 私有仓 `Enough1122/hermes-workspace`（脚本 `scripts/backup_life.py`；成功静默，失败才响）。**仓库永久 private。**

## 顶层布局

| 路径 | 内容 | 进备份 |
|---|---|---|
| `记录/` | 食材池、食物标准、体重史、替尔泊肽注射记录、跑团存档 | ✅ |
| `健康/` | `体重记录.csv`（体重数据唯一真源）+ 可视化资产 | ✅ |
| `diary/` | 每日日记 `YYYY-MM-DD.md` | ✅ |
| `scripts/` | 入口脚本（`report_weight.py` / `sync_all.py` / `backup_life.py` / OAS 工具…） | ✅ |
| `projects/` | 自己的项目：`github-tools/`（PR 工具）、`华通/`（股票）、`体重可视化/`、`pelican-bike/` | ✅ |
| `reviews/` | PR 批量评审归档（按批次） | ✅ |
| `patches/` | 对克隆仓的本地改动存档（如 OAS 补丁与恢复说明） | ✅ |
| `skills/` | 从团队 hub 下载的技能包暂存（`baidu-search`） | ✅ |
| `repos/` | **外部/独立仓专区**：`hermes-agent-fix`（fork）、`lark-coding-agent-bridge`、`ai-berkshire`、`OAS`、`OASX`。整夹被 `.gitignore` 排除——**不备份**，丢了各自从远端重拉；新克隆一律丢这里 | ❌ |
| `backups/` `cache/` `tmp/` `data/` `env/` `.hermes/` `.claude/` `.firecrawl/` | 备份/缓存/临时/运行时 | ❌ |

## 约定

- 新用户文件默认落本目录；外部仓 → `repos/`（`.gitignore` 一条 `repos/` 整夹排除，新克隆丢进去即可，无需逐仓维护）。
- 凭证类（`.env*`、`*.key`、`*.pem`、`auth.json`、`*token*.json`…）一律不入库。
- 大仓只管「该被版本控制、且没有自己 remote」的内容。
- **重装/交接**:见 `HERMES-重装指南.md` —— 重装 Hermes 后的恢复清单(专门设置 / 记忆 / 定时任务的保留项)。

_2026-09-16 起维护；结构改动见 git log。_
