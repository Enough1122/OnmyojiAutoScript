# -*- coding: utf-8 -*-
import csv, statistics
from datetime import datetime, timedelta

PATH = r"D:\Hermes\健康\体重记录.csv"

rows = []
with open(PATH, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        d = r["日期"].strip()
        w = r["晨重"].strip()
        if not d or not w:
            continue
        try:
            v = float(w)
        except ValueError:
            continue
        rows.append((datetime.strptime(d, "%Y-%m-%d").date(), v))

rows.sort()
print(f"有效晨重数据点: {len(rows)}  {rows[0][0]} -> {rows[-1][0]}")
print()

# ---- 7 日移动平均（按日期插值缺失日） ----
start, end = rows[-1][0] - timedelta(days=45), rows[-1][0]
valmap = dict(rows)
series = []
d = start
while d <= end:
    win = [valmap[x] for x in (d - timedelta(days=i) for i in range(7)) if x in valmap]
    if len(win) >= 4:
        series.append((d, round(statistics.mean(win), 1)))
    d += timedelta(days=1)

print("=== 近 45 天 7 日移动平均（斤）===")
for d, v in series:
    print(f"{d}  {v}")

print()
# ---- 周度（周一收盘）对比 ----
from collections import defaultdict
weeks = defaultdict(list)
for d, v in rows:
    mon = d - timedelta(days=d.weekday())
    weeks[mon].append((d, v))
print("=== 周度（周一为界）收盘 ===")
mons = sorted(weeks)
prev = None
for m in mons[-10:]:
    last = sorted(weeks[m])[-1]
    delta = "" if prev is None else f"{last[1]-prev:+.1f}"
    print(f"周 {m}  收盘 {last[1]:.1f} ({last[0]})  {delta}")
    prev = last[1]

print()
# ---- 阶段速度 ----
def avg_daily(a, b):
    A = [v for d, v in rows if a <= d <= b]
    if not A:
        return None
    return (A[0], A[-1], (A[0]-A[-1]) / max((rows[-1][0]-rows[0][0]).days, 1))

print("=== 减重速度对比 ===")
segs = [
    ("7/13→8/03  高速期", datetime(2026,7,13).date(), datetime(2026,8,3).date()),
    ("8/03→8/24  中速期", datetime(2026,8,3).date(), datetime(2026,8,24).date()),
    ("8/22→9/01  当前期", datetime(2026,8,22).date(), datetime(2026,9,1).date()),
]
for name, a, b in segs:
    A = [v for d, v in rows if a <= d <= b]
    days = (b - a).days
    print(f"{name}: {A[0]:.1f} → {A[-1]:.1f}  {A[-1]-A[0]:+.1f}斤 / {days}天 = {(A[0]-A[-1])/days*7:+.2f} 斤/周")

print()
recent = [v for d, v in rows if d >= datetime(2026,8,22).date()]
print(f"8/22-9/1 共 {len(recent)} 个读数: {recent}")
print(f"均值 {statistics.mean(recent):.1f}  最高 {max(recent):.1f}  最低 {min(recent):.1f}  标准差 {statistics.pstdev(recent):.2f}")
prior = [v for d, v in rows if datetime(2026,8,8).date() <= d <= datetime(2026,8,21).date()]
print(f"8/08-8/21 对比段 均值 {statistics.mean(prior):.1f}")

print()
print(f"累计: 244.0 → {rows[-1][1]} = {rows[-1][1]-244.0:+.1f} 斤")
print(f"距 160 斤还差 {rows[-1][1]-160:.1f} 斤；距 190 斤还差 {rows[-1][1]-190:.1f} 斤")
