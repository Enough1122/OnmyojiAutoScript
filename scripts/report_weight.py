#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_weight.py — 体重上报一条龙（防呆版）
用法: python report_weight.py <斤数> [备注]
自动完成三步（缺一不可）:
  1. 追加/更新 体重记录.csv 当日行
  2. 更新 diary/YYYY-MM-DD.md 的体重段
  3. 跑 sync_all.py 同步可视化+时间线
任何一步失败都会报错退出,不会静默丢数据。
"""
import sys
import csv
import subprocess
import datetime
import re
from pathlib import Path

CSV_PATH = Path(r"D:\Hermes\健康\体重记录.csv")
DIARY_DIR = Path(r"D:\Hermes\diary")
SYNC_ALL = Path(r"D:\Hermes\scripts\sync_all.py")

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def main():
    if len(sys.argv) < 2:
        print("用法: python report_weight.py <斤数> [备注]")
        return 1
    weight = float(sys.argv[1])
    note = sys.argv[2] if len(sys.argv) > 2 else ""
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    weekday = WEEKDAYS[now.weekday()]
    hhmm = now.strftime("%H:%M")

    # --- Step 1: CSV ---
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    full_note = f"{hhmm} 称 {weight}(用户报) · {note}" if note else f"{hhmm} 称 {weight}(用户报)"
    updated = False
    for r in rows:
        if r and r[0] == today:
            while len(r) < 5:
                r.append("")
            # 智能列分配:晨重列(r[2])已有值 → 写晚重列(r[3]);否则写晨重列(r[2])
            # 凌晨报数(0<=hour<6)且已有晨重 → 写晚重列(睡前口径)
            existing_morning = r[2].strip() if len(r) > 2 else ""
            existing_evening = r[3].strip() if len(r) > 3 else ""
            is_latenight = 0 <= now.hour < 6
            if existing_morning and (is_latenight or existing_morning):
                # 已有晨重 → 写晚重列
                r[1] = weekday
                r[3] = str(weight)  # 晚重列
                # 只在备注里追加,不清空原备注(避免覆盖晨重口径)
                # 注意:判断依据是原备注是否为空,绝不能用备注文本含不含"晨"字
                # (晚重备注常带"较晨重±X",一查就误判覆盖,2026-09-04实锤)
                if r[4]:
                    r[4] = r[4] + f" · {hhmm} 晚重 {weight}({note})" if note else r[4] + f" · {hhmm} 晚重 {weight}"
                else:
                    r[4] = full_note
            else:
                # 空晨重列 → 写晨重列
                r[1], r[2], r[4] = weekday, str(weight), full_note
            updated = True
            break
    if not updated:
        rows.append([today, weekday, str(weight), "", full_note])
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, quoting=csv.QUOTE_MINIMAL).writerows(rows)
    print(f"[1/3] CSV 已写入 {today} {weight}")

    # --- Step 2: Diary ---
    entry = f"- **{weight}**({hhmm} 称"
    if note:
        entry += f"·{note}"
    entry += ")\n"

    diary = DIARY_DIR / f"{today}.md"
    if diary.exists():
        txt = diary.read_text(encoding="utf-8")
        section = "## ⚖️ 体重\n" + entry
        if "## ⚖️ 体重" in txt:
            txt = re.sub(r"## ⚖️ 体重\n(?:- .*?\n)*", section, txt, count=1)
        else:
            txt = txt.rstrip() + "\n\n" + section
        diary.write_text(txt, encoding="utf-8")
    else:
        header = f"# {today} {weekday}\n\n## ⚖️ 体重\n{entry}"
        diary.write_text(header, encoding="utf-8")
    print(f"[2/3] 日记已更新 {diary.name}")

    # --- Step 3: Sync ---
    r = subprocess.run([sys.executable, str(SYNC_ALL)], capture_output=True, text=True)
    out = r.stdout or ""
    ok = ("已重生成" in out or "weight_data.js" in out) and r.returncode == 0
    if ok:
        print("[3/3] sync_all ✅ 完成")
        print("✅ 三步全部完成,可视化已同步")
        return 0
    else:
        print("[3/3] sync_all ❌ 失败")
        print((r.stderr or out)[:500])
        return 1


if __name__ == "__main__":
    sys.exit(main())
