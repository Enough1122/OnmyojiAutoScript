#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
regen_timeline.py
从 D:\Hermes\健康\体重记录.csv (真源) 自动重生成 D:\Hermes\健康\完整体重时间线.md
- 用户改完 CSV 跑一次即可
- cron 23:50 自动跑
- 修复"完整体重时间线 13 天不续补"那种一更新就坏的问题
- 用法: python D:/Hermes/scripts/regen_timeline.py
"""

import csv
from datetime import datetime
from pathlib import Path

CSV_PATH = Path(r"D:\Hermes\健康\体重记录.csv")
MD_PATH = Path(r"D:\Hermes\健康\完整体重时间线.md")
START_WEIGHT = 244.0  # 2026-04-17 真实起点
W_START = datetime(2026, 6, 29)  # 2026-06-29 = W11 (用户口径:7/6=W12,7/27=W15;与 sync_visualization 一致)


def load_rows():
    """读 CSV，过滤噪音/起点/异常，返回按日期升序的晨重行"""
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) < 4:
                continue
            date_str, weekday, morning, evening = row[0], row[1], row[2], row[3]
            note = row[4] if len(row) > 4 else ""
            if not date_str or not morning:
                continue
            if "[起点" in note or "[异常" in note:
                continue
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d")
                w = float(morning)
            except (ValueError, TypeError):
                continue
            rows.append({
                "date": date_str,
                "weekday": weekday,
                "d": d,
                "w": w,
                "evening": evening,
                "note": note,
            })
    rows.sort(key=lambda r: r["d"])
    return rows


def week_of(d):
    """W 编号 = 11 + (days_from_W_start // 7) (6/29=W11,用户口径)"""
    diff = (d - W_START).days
    if diff < 0:
        return None
    return 11 + diff // 7


def detect_milestone(prev_w, curr_w, milestones):
    """检测破里程碑（破 X = 严格 < X）"""
    hit = []
    for m in sorted(milestones):
        if prev_w >= m > curr_w:
            hit.append(m)
    return hit


def render_table(rows):
    """生成完整数据表 markdown"""
    out = ["| 日期 | 星期 | 晨重(斤) | 变化 | 备注 |", "|------|------|----------|------|------|"]
    milestones = [240, 235, 230, 225, 220, 215, 212.5, 210, 205, 200]
    prev = None
    for r in rows:
        delta = ""
        if prev is not None:
            d = round(r["w"] - prev, 1)
            delta = f"{d:+.1f}"
            # 检测破里程碑
            hit = detect_milestone(prev, r["w"], milestones)
            if hit:
                delta += f" 🎯破{[m for m in hit]}"
        # 备注清理（CSV 备注很长，简化）
        note = r["note"]
        # 移除 [QClaw 补录] 标签（默认项）
        note = note.replace("[QClaw 补录] ", "").replace("[QClaw 补录]", "").strip()
        # 短化
        if len(note) > 40:
            note = note[:37] + "..."
        evening = ""
        if r["evening"]:
            try:
                ev = float(r["evening"])
                if prev is not None:
                    ed = round(ev - r["w"], 1)
                    evening = f" 晚重 {ev}（{ed:+.1f}）"
            except ValueError:
                pass
        out.append(f"| {r['date']} | {r['weekday']} | {r['w']} | {delta} | {note}{evening} |".rstrip())
        prev = r["w"]
    return "\n".join(out)


def render_summary(rows):
    """关键节点 + 阶段分析 + 噪音列表"""
    latest = rows[-1]
    total_lost = round(START_WEIGHT - latest["w"], 1)
    min_row = min(rows, key=lambda r: r["w"])

    # 周起跑
    weekly = {}
    for r in rows:
        wn = week_of(r["d"])
        if wn is None:
            continue
        if wn not in weekly:
            weekly[wn] = r

    # 阶段
    phases = [
        ("4/17 真实起点 → 5/22 起跑基准", "2026-04-17", "2026-05-22", 229.8, "主动减肥期"),
        ("5/22 → 6/29 W11", "2026-05-22", "2026-06-29", 218.4, "替尔泊肽早期"),
    ]

    s = []
    s.append("## 关键节点(自动生成)")
    s.append("")
    s.append(f"- **历史最高**: {START_WEIGHT} 斤(2026-04-17 真实起点)")
    s.append(f"- **当前({latest['date']})**: {latest['w']} 斤")
    s.append(f"- **总减重**: {START_WEIGHT} - {latest['w']} = **{total_lost} 斤**")
    s.append(f"- **最低点**: {min_row['w']} 斤 ({min_row['date']})")
    s.append(f"- **距 200 大关**: {round(latest['w']-200, 1)} 斤")
    s.append("")
    s.append("## 阶段分析(自动生成)")
    s.append("")
    s.append(f"- **4/17 起点 → 5/22 起跑基准**: {START_WEIGHT} → 229.8 = -14.2 斤 / 35 天(主动减肥)")
    s.append(f"- **5/22 → 6/29 W11**: 229.8 → 218.4 = -11.4 斤 / 38 天(替尔泊肽早期)")
    # 每周
    wn_list = sorted(weekly.keys())
    for i, wn in enumerate(wn_list):
        if wn < 11:
            continue
        r = weekly[wn]
        if i + 1 < len(wn_list):
            next_wn = wn_list[i + 1]
            end_r = weekly[next_wn]
            end_w = end_r["w"]
            end_label = f"W{next_wn} 起跑"
        else:
            end_w = latest["w"]
            end_label = f"{latest['date']}(当前)"
        delta = round(r["w"] - end_w, 1)
        days = (latest["d"] - r["d"]).days if i + 1 >= len(wn_list) else 7
        delta_txt = f"-({delta})" if delta >= 0 else f"+{-delta}"
        s.append(f"- **W{wn}**: {r['date']} {r['w']} → {end_label} {end_w} = {delta_txt} 斤")
    s.append("")
    s.append("## 已排除的噪音(CSV 已标记)")
    s.append("")
    s.append("见 `体重记录.csv` 中含 `[噪音]` / `[异常]` / `[起点]` 标签的行")
    s.append("")
    return "\n".join(s)


def main():
    if not CSV_PATH.exists():
        print(f"❌ CSV 不存在: {CSV_PATH}")
        return 1
    rows = load_rows()
    if not rows:
        print("❌ CSV 无有效数据")
        return 1
    print(f"✅ 加载 {len(rows)} 个数据点 ({rows[0]['date']} → {rows[-1]['date']})")

    table = render_table(rows)
    summary = render_summary(rows)

    # 备份
    if MD_PATH.exists():
        bak = MD_PATH.with_suffix(MD_PATH.suffix + ".bak")
        bak.write_text(MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"📦 备份 → {bak.name}")

    # 生成
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""# 完整体重时间线(自动生成)

> 自动生成: {today} (运行: `python D:/Hermes/scripts/regen_timeline.py`)
> 数据源: `D:\\Hermes\\健康\\体重记录.csv` (唯一真源)
> 数据点: {len(rows)} 个
> 时间跨度: {rows[0]['date']} → {rows[-1]['date']}

> ⚠️ **本文件由脚本自动生成,不要手改!** 改 `体重记录.csv` 后跑 `regen_timeline.py` 即可。

## 完整数据

{table}

{summary}
"""
    MD_PATH.write_text(content, encoding="utf-8")
    print(f"✅ 已重生成: {MD_PATH}")
    print(f"   当前: {rows[-1]['w']} 斤 ({rows[-1]['date']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
