# OAS 本地新增文件存档

**原则:不改上游代码,只放我们自己新建的文件。**

`yyssy/OAS` 是 `runhey/OnmyojiAutoScript` 的克隆(1.4G,已被主仓排除),**上游代码保持原样**。
本目录保存的是**我们新建**、而 OAS 自动更新会删掉的东西。

## 文件

| 文件 | 说明 |
|---|---|
| `start_oas.py` | 一键启动脚本:先启动 MuMu,再自动拉起 OAS 并开始挂机。**上游无此文件**,OAS 更新后会被删 |

## 恢复流程(OAS 更新后 start_oas.py 消失)

```bash
cp "D:/Hermes/patches/oas/start_oas.py" "D:/Hermes/yyssy/OAS/"
```

## 历史说明(2026-09-16)

在此之前 OAS 里有**两处上游代码的修改** ——
`tasks/Component/GeneralBattle/general_battle.py`(御魂弹窗改点"确认"、预设切换从第 1 场放宽到前 3 场)、
`tasks/Exploration/base.py`(去掉硬编码的 `lock_team_enable = True`),用途是让"预设 3-1 + 御魂切换"生效。

按「官方仓代码不改」这条原则,**已于 2026-09-16 全部 `git checkout` 还原**,配套补丁文件一并删除。
副作用:预设队伍切换随之失效,回到上游默认行为(锁定阵容、忽略御魂不一致弹窗)。
需要那段改动时,查主仓 `hermes-workspace` 2026-09-16 前后的提交,当时 `patches/oas/tracked-files.diff` 曾入库。

## 附:配置与代码的界限

- **配置**(`config/oas.json` 等)属玩家配置、不被 git 管理 → **可以自由改**
- **上游代码**(`tasks/**`)→ **不改**;确实需要时先确认这条原则是否让步
