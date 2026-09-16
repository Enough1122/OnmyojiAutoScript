## 现象
RealmRaid 在突破券打空后，没有优雅退出做下一个任务，而是连续 3 次 `GameStuckError: Wait too long`，触发 `Task RealmRaid failed 3 or more times` → `Request human takeover` → 进程退出。

## 复现链（2026-09-09 日志实测）
1. 14:42 `check_ticket` 正确识别到无券：`script_task.py:0313 WARNING Execute raid failed, no ticket`，该轮正常结束。
2. 之后三轮 RealmRaid（14:43 / 14:45 / 14:50）在票数为 0 的情况下依然 `fire` 点火成功（`Click fire 1 success`），但游戏内根本没有进入战斗。
3. `run_general_battle` 空等 60s → `device.py:0156 WARNING Wait too long` → `GameStuckError: Wait too long`，攒满 3 次进程退出。

## 根因定位
- `run_2` 主循环的 `check_ticket(number_base)` 本意是对的（没券 break → TaskEnd），但依赖 `O_NUMBER.ocr` 一次读数；券空后 OCR 偶发误读（读出 total>0、cu+res 对不上），返回 True 放行。
- 放行后 `fire(index)` 点的进攻按钮因无券无响应，`run_general_battle` 对"点了火但没进战斗"这个分支没有任何确认/超时自退，直接等到 60s 全局超时。
- 另外 `find_one` 在无券时仍能找到昨日残留列表里的勋章目标，也是放行的帮凶之一。

日志关键行：
```
2026-09-09 14:42:28.150 | script_task.py:0313 | WARNING | Execute raid failed, no ticket
2026-09-09 14:54:27.071 | script_task.py:0528 | INFO | Click fire 1 success
2026-09-09 14:55:26.604 | device.py:0156 | WARNING | Wait too long
2026-09-09 14:55:26.658 | ERROR | GameStuckError: Wait too long
2026-09-09 14:55:39.471 | script.py:0703 | CRITICAL | Task `RealmRaid` failed 3 or more times.
2026-09-09 14:55:39.480 | CRITICAL | Request human takeover
```

## 环境
- 分支 dev（commit 5767e485），MuMu 模拟器，1280x720，截图 ADB
- 调度：Exploration + RealmRaid 无限循环，券空前 15 战 15 胜

## 建议修复方向（供参考）
`fire` 之后加一级"确认真的进了战斗"的检查（比如 N 秒内出现 BATTLE_STATUS，否则主动回退），而不是等 60s 全局超时。这样即使 OCR 误读放行，也能干净退出做下一个任务。
