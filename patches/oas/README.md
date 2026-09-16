# OAS 本地改动存档

**上游**: `runhey/OnmyojiAutoScript`(我们无权推送,所以改动不能靠 fork 保存)

旁边的 `yyssy/OAS` 是上游克隆(1.4G,已被主仓排除)—— **本目录保存的才是「我们自己的那部分」**。
OAS 自动更新/重置会还原代码、删掉自建文件,这里就是恢复源。

## 文件说明

| 文件 | 内容 |
|---|---|
| `tracked-files.diff` | 对上游已跟踪文件的修改(`tasks/Component/GeneralBattle/general_battle.py`、`tasks/Exploration/base.py`) |
| `start_oas.py` | 自建启动脚本(上游无此文件,OAS 更新会删它) |
| `preset-fixes.patch` | 更早一版的预设修复补丁(2026-09-10 恢复包,保留作回退) |
| `start_oas.py.bak` | 上述补丁配套的启动脚本副本 |
| `OAS-commit.txt` | 生成这些改动时的上游 commit 号 —— 补丁打不上时用它定位基线 |

## 恢复流程(OAS 被更新吞掉改动后)

```bash
cd D:/Hermes/yyssy/OAS
git checkout .                                          # 回到上游状态
git apply "D:/Hermes/patches/oas/preset-fixes.patch"    # 载入补丁
cp "D:/Hermes/patches/oas/start_oas.py" .               # 放回启动脚本
```

补丁因上游变动打不上时,拿 `tracked-files.diff` 手工对照当前文件改。

## 何时刷新本目录

**每次改完 OAS 的本地代码就刷新一次**,否则这里会落后于实际改动:

```bash
cd D:/Hermes/yyssy/OAS
git diff > D:/Hermes/patches/oas/tracked-files.diff
cp start_oas.py D:/Hermes/patches/oas/
```

本目录由主仓 `hermes-workspace` 跟踪,改动会自动进版本历史并异地备份。
