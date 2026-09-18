# -*- coding: utf-8 -*-
"""check_weight_data.py — 体重数据全链路校验。

真源 体重记录.csv → 完整体重时间线.md / 体重可视化/weight_data.js 的一致性检查:
A 结构(日期/星期/数值)  B 晚重列出处  C 备注增减数字对账  D 插值算术
E 时间线 md 逐行  F weight_data.js 逐字段  G META/weekly 抽验

用法: python D:/Hermes/scripts/check_weight_data.py
退出码: 0=全部通过, 1=有 FAIL
"""
import csv, re, sys, datetime

CSV_PATH = r"D:/Hermes/健康/体重记录.csv"
MD_PATH = r"D:/Hermes/健康/完整体重时间线.md"
JS_PATH = r"D:/Hermes/projects/体重可视化/weight_data.js"

FAILS, WARNS, OKS = [], [], []
def bad(sec, msg): FAILS.append("[%s] %s" % (sec, msg))
def warn(sec, msg): WARNS.append("[%s] %s" % (sec, msg))

# ---------- A. CSV 结构 ----------
rows = list(csv.reader(open(CSV_PATH, encoding="utf-8-sig")))
data = rows[1:]
wd_map = {"星期一":0,"星期二":1,"星期三":2,"星期四":3,"星期五":4,"星期六":5,"星期日":6}
recs = []
prev = None
for r in data:
    if not r or not r[0].strip():
        continue
    d = r[0]
    wd = r[1] if len(r) > 1 else ""
    am = r[2] if len(r) > 2 else ""
    pm = r[3] if len(r) > 3 else ""
    note = ",".join(r[4:]) if len(r) > 4 else ""  # 未引号含逗号旧格式复原,同 sync_visualization 口径
    dt = datetime.date.fromisoformat(d)
    if wd_map.get(wd) != dt.weekday():
        bad("A-结构", "%s 星期%s错,应为星期%s" % (d, wd, "一二三四五六日"[dt.weekday()]))
    for col, v in (("晨重", am), ("晚重", pm)):
        if v and not 90 <= float(v) <= 260:
            bad("A-结构", "%s %s=%s 越界" % (d, col, v))
    if prev and dt <= prev:
        bad("A-结构", "%s 乱序/重复" % d)
    prev = dt
    recs.append({"date": dt, "ds": d, "wd": wd,
                 "am": float(am) if am else None,
                 "pm": float(pm) if pm else None, "note": note})
OKS.append("A: %d 行结构/星期/数值全部通过 (跨度 %s -> %s)" % (len(recs), recs[0]["ds"], recs[-1]["ds"]))
by_ds = {r["ds"]: r for r in recs}

# ---------- B. 晚重列出处 (咨询级: 取最新/差值可推导的行无字面值,属正常) ----------
n = 0
for r in recs:
    if r["pm"] is None:
        continue
    n += 1
    s = r["pm"]
    if not any(c in r["note"] for c in ("%g" % s, "%s" % s, "%.1f" % s, "%.0f" % s)):
        warn("B-晚重", "%s 晚重列 %s 备注无字面出处(可推导则无碍)" % (r["ds"], s))
OKS.append("B: %d 行晚重列检查完毕" % n)

# ---------- C. 备注增减数字对账 ----------
checked = skipped = 0
WEIGHT_RE = re.compile(r"(?<![\d.])(\d{3}(?:\.\d)?)(?![\d.])")  # 3位数体重; \b 在 CJK 邻接数字时失效,用环视排除日期/时刻
for idx, r in enumerate(recs):
    note = r["note"]
    note_nums = [float(x) for x in WEIGHT_RE.findall(note)]
    def ok_claim(subjects, ref, claimed):
        pool = [s for s in subjects if s is not None] + note_nums
        return any(abs((s - ref) - claimed) <= 0.06 for s in pool)
    for m in re.finditer(r"较(\d{1,2})/(\d{1,2})(晨|晚)?(?:\(([\d.]+)\)|([\d.]+))?\s*([+-])(\d+(?:\.\d+)?)", note):
        mm, dd, tod, pref, inline, sign, dv = m.groups()
        ref_ds = "2026-%02d-%02d" % (int(mm), int(dd))
        base = by_ds.get(ref_ds)
        if not base or base["am"] is None:
            skipped += 1
            continue
        actual = base["pm"] if (tod == "晚" and base["pm"] is not None) else base["am"]
        claimed = float(dv) * (1 if sign == "+" else -1)
        refs = ([float(pref)] if pref else []) + ([float(inline)] if inline else []) + [actual]
        if any(ok_claim([r["am"]] if ref_ds != r["ds"] else [], rr, claimed) for rr in refs):
            checked += 1
        else:
            bad("C-对账", "%s 备注『%s』: 基准%s(%s) 推不出 %s" % (r["ds"], m.group(0).strip(), "/".join("%g" % x for x in refs), ref_ds, claimed))
    for m in re.finditer(r"较(昨日|昨晨|昨晚)\(?([\d.]+)\)?\s*([+-])(\d+(?:\.\d+)?)", note):
        which, pref, sign, dv = m.groups()
        if idx == 0:
            skipped += 1
            continue
        base = recs[idx - 1]
        actual = base["pm"] if which == "昨晚" and base["pm"] is not None else base["am"]
        if actual is None:
            skipped += 1
            continue
        claimed = float(dv) * (1 if sign == "+" else -1)
        refs = ([float(pref)] if pref else []) + [actual]
        if any(abs((r["am"] - ref) - claimed) <= 0.06 for ref in refs):
            checked += 1
        else:
            bad("C-对账", "%s 备注『%s』: %s-%s != %s" % (r["ds"], m.group(0).strip(), r["am"], actual, claimed))
    for m in re.finditer(r"起点\((\d{1,2})/(\d{1,2})\s+([\d.]+)\)\s*([+-])(\d+(?:\.\d+)?)", note):
        mm, dd, ref, sign, dv = m.groups()
        ref_ds = "2026-%02d-%02d" % (int(mm), int(dd))
        base = by_ds.get(ref_ds)
        if base and base["am"] is not None and abs(base["am"] - float(ref)) > 0.06:
            bad("C-对账", "%s 『%s』括号ref %s != %s 实际晨重 %s" % (r["ds"], m.group(0)[:30], ref, ref_ds, base["am"]))
        claimed = float(dv) * (1 if sign == "+" else -1)
        if ok_claim([r["am"]], float(ref), claimed):
            checked += 1
        else:
            bad("C-对账", "%s 『%s』%s-%s != %s" % (r["ds"], m.group(0)[:30], r["am"], ref, claimed))
OKS.append("C: 备注增减对账 %d 条通过, %d 条无法解析跳过" % (checked, skipped))

# ---------- D. 插值算术 ----------
for idx, r in enumerate(recs):
    if "[插值" in r["note"] and 0 < idx < len(recs) - 1 and r["am"] is not None and "取平" in r["note"]:
        a, b = recs[idx - 1]["am"], recs[idx + 1]["am"]
        if a and b:
            exp = round((a + b) / 2, 1)
            if abs(exp - r["am"]) <= 0.06:
                OKS.append("D: %s 插值取平 (%s+%s)/2=%s" % (r["ds"], a, b, exp))
            else:
                bad("D-插值", "%s 应为 %.1f 实为 %s" % (r["ds"], (a + b) / 2.0, r["am"]))
seg = [r for r in recs if "2026-04-18" <= r["ds"] <= "2026-05-12"]
diffs = [round(seg[i]["am"] - seg[i + 1]["am"], 2) for i in range(len(seg) - 1)]
if max(diffs) - min(diffs) <= 0.02 and all(d > 0 for d in diffs):
    OKS.append("D: 4/18-5/12 等差插值段步长一致 (%s~%s/天)" % (min(diffs), max(diffs)))
else:
    bad("D-插值", "4/18-5/12 步长不均匀 %s" % diffs[:5])

# ---------- E. 时间线 md vs CSV ----------
md = open(MD_PATH, encoding="utf-8").read()
tbl = re.findall(r"^\| (2026-\d\d-\d\d) \| (星期.) \| ([\d.]+) \| ([^|]*) \|", md, re.M)
exp_rows = [r for r in recs if r["am"] is not None and "[起点" not in r["note"] and "[异常" not in r["note"]]
if len(tbl) != len(exp_rows):
    bad("E-时间线", "md表 %d 行 != 预期 %d 行" % (len(tbl), len(exp_rows)))
else:
    mism = 0
    for (d, wd, w, dl), r in zip(tbl, exp_rows):
        if d != r["ds"] or wd != r["wd"] or abs(float(w) - r["am"]) > 1e-9:
            mism += 1
            bad("E-时间线", "%s md(%s,%s) != CSV(%s,%s)" % (d, wd, w, r["wd"], r["am"]))
    if not mism:
        OKS.append("E: 时间线表 %d 行与 CSV 逐行一致" % len(tbl))
hdr_pts = re.search(r"数据点: (\d+) 个", md)
if hdr_pts and int(hdr_pts.group(1)) != len(exp_rows):
    bad("E-时间线", "头部数据点 %s != %d" % (hdr_pts.group(1), len(exp_rows)))
cur = exp_rows[-1]
mn = min(exp_rows, key=lambda r: r["am"])
for pat, want, name in [(r"总减重.*?\*\*([\d.]+) 斤\*\*", round(244.0 - cur["am"], 1), "总减重"),
                        (r"当前\(2026-\d\d-\d\d\)\*\*: ([\d.]+) 斤", cur["am"], "当前")]:
    m = re.search(pat, md)
    if not m:
        bad("E-时间线", "关键节点缺 %s" % name)
    elif abs(float(m.group(1)) - want) > 1e-9:
        bad("E-时间线", "%s %s 应为 %s" % (name, m.group(1), want))
m = re.search(r"最低点\*\*: ([\d.]+) 斤 \(([\d-]+)\)", md)
if m and (float(m.group(1)) != mn["am"] or m.group(2) != mn["ds"]):
    bad("E-时间线", "最低点 %s(%s) 应为 %s(%s)" % (m.group(1), m.group(2), mn["am"], mn["ds"]))
if not any(x.startswith("[E-") for x in FAILS):
    OKS.append("E: 关键节点(总减重/当前/最低点)与 CSV 复算一致")

# ---------- F. weight_data.js vs CSV ----------
js = open(JS_PATH, encoding="utf-8").read()
raw = re.findall(r"\{date:'([\d-]+)', morning:(null|[\d.]+), evening:(null|[\d.]+), note:'(.*)'\},?", js)
if len(raw) != len(recs):
    bad("F-可视化", "RAW %d 条 != CSV %d 行" % (len(raw), len(recs)))
else:
    mism = 0
    for (d, m_, e_, nt), r in zip(raw, recs):
        am_j = None if m_ == "null" else float(m_)
        pm_j = None if e_ == "null" else float(e_)
        unesc = nt.replace("\\'", "'").replace("\\\\", "\\")
        if d != r["ds"] or am_j != r["am"] or pm_j != r["pm"] or unesc != r["note"]:
            mism += 1
            bad("F-可视化", "%s 字段不一致" % d)
    if not mism:
        OKS.append("F: RAW %d 条与 CSV 逐字段一致(含备注)" % len(raw))

# ---------- G. META/weekly 抽验 ----------
meta = dict(re.findall(r"^  (\w+): (null|[\d.\-]+|'[^']*'),", js, re.M))
# ma 口径: 排除 [插值/[噪音/[起点 (同 sync_visualization real_mornings)
real_mornings = [r for r in recs if r["am"] is not None
                 and "[噪音]" not in r["note"] and "[插值" not in r["note"] and "[起点" not in r["note"]]
latest_ds = real_mornings[-1]["ds"]
latest_dt = datetime.date.fromisoformat(latest_ds)
win7 = [r for r in real_mornings if r["ds"] >= (latest_dt - datetime.timedelta(days=6)).isoformat()]
exp_meta = {"currentWeight": cur["am"], "totalDelta": round(244.0 - cur["am"], 1),
            "peakWeight": 244.0,
            "ma7": round(sum(x["am"] for x in win7) / len(win7), 1),
            "monthlyDelta": round(198.4 - cur["am"], 1)}
meta_ok = True
for k, want in exp_meta.items():
    got = meta.get(k)
    if got is None or got == "null" or abs(float(got) - want) > 0.06:
        bad("G-META", "%s=%s 应为 %s" % (k, got, want))
        meta_ok = False
if meta_ok:
    OKS.append("G: META 抽验 5 项通过 (ma7=%s)" % meta.get("ma7"))
wk = re.findall(r"\{week:'(W\d+)', label:'([^']+)', delta:([\d.\-]+), start:([\d.]+), end:([\d.]+), color:'[^']+', target:(null|[\d.]+), inProgress:(true|false)\}", js)
w22 = [w for w in wk if w[0] == "W22"]
if w22:
    w = w22[0]
    if w[1].startswith("09/14-09/21") and w[6] == "true" and abs(float(w[3]) - 192.6) < 0.01 and abs(float(w[2]) - 2.1) < 0.01:
        OKS.append("G: weeklyData W22 进行中周口径正确 (192.6->194.7, +2.1)")
    else:
        bad("G-WEEK", "W22 %s start=%s delta=%s inProg=%s" % (w[1], w[3], w[2], w[6]))
elif not wk:
    bad("G-WEEK", "weeklyData 未解析到")
else:
    bad("G-WEEK", "缺 W22, 只有 %s" % [w[0] for w in wk])

# ---------- 汇总 ----------
print("=" * 50)
for x in OKS:
    print("OK ", x)
if WARNS:
    print("-" * 50)
    for x in WARNS:
        print("WARN", x)
print("=" * 50)
print("FAIL: %d" % len(FAILS))
for x in FAILS:
    print("  !!", x)
sys.exit(1 if FAILS else 0)
