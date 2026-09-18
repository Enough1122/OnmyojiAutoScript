"""
从 D:/Hermes/健康/体重记录.csv 同步生成 weight_data.js。

被 体重可视化/index.html 引用 (<script src="weight_data.js"></script>)。

设计:weight_data.js 内容是
  const RAW = [ ... ];        // daily records (date / morning / evening / note)
  const weeklyData = [ ... ]; // weekly summary (week / label / delta / start / end / color)

weekly summary 由 daily records 重新计算(不只是从 CSV 复制),保证一致性。

用法:
  python sync_visualization.py [--csv PATH] [--out PATH] [--start-week YYYY-MM-DD]

默认参数:
  --csv: D:/Hermes/健康/体重记录.csv
  --out: D:/Hermes/projects/体重可视化/weight_data.js
  --start-week: 7/13/2026 (W13;W14 起点 7/19 由 W13 收盘自动算)
"""

import argparse
import csv
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 颜色轮换(W11-W18,跟 HTML 里的 color 一致)
WEEK_COLORS = [
    "#fbbf24",  # W11-12 黄色(慢速)
    "#4ade80",  # W13-14 绿色(快速)
    "#60a5fa",  # W15-16 蓝色
    "#a78bfa",  # W17-18 紫色
    "#f472b6",  # 粉色
    "#34d399",  # 翠绿
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="D:/Hermes/健康/体重记录.csv")
    p.add_argument("--out", default="D:/Hermes/projects/体重可视化/weight_data.js")
    p.add_argument("--start-week", default="2026-06-29",
                   help="W11 周一(整段可视化的起点,2026-06-29 = 218.4 斤)")
    return p.parse_args()


def load_csv(csv_path: Path):
    """解析 CSV → list of {date, morning, evening, note}

    用标准 csv 模块:备注含英文逗号时字段会被双引号包裹 (如 8/15/8/26),
    原 line.split(',', 4) 手写解析不剥离包裹引号,导致 weight_data.js 的
    note 带首尾 " 残留 (页面数据表/tooltip 显示多余引号)。
    """
    records = []
    if not csv_path.exists():
        sys.exit(f"❌ CSV not found: {csv_path}")

    # utf-8-sig:防 Excel 编辑后注入 BOM,否则 \ufeff2026-04-17 过不了 strptime 会被静默 skip
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头
        for parts in reader:
            if not parts or not any(p.strip() for p in parts):
                continue
            if len(parts) < 3:
                continue
            date_str = parts[0].strip()
            morning_str = parts[2]
            evening_str = parts[3] if len(parts) > 3 else ""
            # 前 4 列固定 (date/星期/晨重/晚重),剩余 parts 全部属于备注:
            # 兼容两种 CSV 写法 —— 带引号字段 (parts 不再拆分) 和
            # 不带引号但含英文逗号的旧格式 (note 被拆成多段,join 复原,
            # 等价于原 split(',', 4) 的语义,不丢内容)
            note = ",".join(parts[4:]) if len(parts) > 4 else ""
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            morning = float(morning_str) if morning_str.strip() else None
            evening = float(evening_str) if evening_str.strip() else None
            # 防御:quoted field 内的换行会被 csv 模块解析进字段,
            # 直接写进 JS 单引号字符串会语法错误 → 换行替换为空格
            note = (note or "").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
            # 转义 note 里的单引号(JS string)
            note_safe = note.replace("\\", "\\\\").replace("'", "\\'")
            records.append({
                "date": date_str,
                "morning": morning,
                "evening": evening,
                "note": note_safe,
            })
    return records


def compute_weekly_summary(records, start_week_monday: str):
    """
    从 records 计算 weekly summary。
    - W_n 周一 = W_(n-1) 周日收盘 + 1
    - weekly 的 start = 每周周一(如有数据)或上一周日收盘
    - weekly 的 end = 下周一晨重(结算日);未出则取本周最后一条 → in_progress
    - delta = end - start (label 的日期范围与之同口径:周一 → 下周一)
    - target = 从该周周一起跑日备注里提取 "W15目标203" 这种 token,缺失则 None

    第一周从 start_week_monday (默认 2026-06-29 = W11 周一) 开始,按周一到周日切。
    """
    if not records:
        return []

    # 索引 (按日期)
    by_date = {r["date"]: r for r in records}

    # 从 start_week_monday 开始,每周一一个周
    first_monday = datetime.strptime(start_week_monday, "%Y-%m-%d")
    weeks = []
    mondays = []
    cur = first_monday
    while cur.strftime("%Y-%m-%d") <= max(by_date.keys()):
        mondays.append(cur)
        cur += timedelta(days=7)

    week_index = 11  # 2026-06-29 = W11 (用户口径:W15 = 07/27-08/02 当前周)

    # 预编译:匹配 "W15目标203" / "W15目标 203" / "W12周一起跑(目标211.2)" 这种 token
    # (CSV 备注实际格式是 "W15 Day5 ..." 或 "W12周一起跑(目标211.2)",目标 token 在括号里)
    target_re = re.compile(r"W(\d+)[^\d]*?目标\s*([\d.]+)")

    for i, monday in enumerate(mondays):
        sunday = monday + timedelta(days=6)
        s_date = monday.strftime("%Y-%m-%d")
        e_date = sunday.strftime("%Y-%m-%d")

        # 这一周内的 records
        in_week = [by_date[d] for d in by_date if s_date <= d <= e_date]
        in_week_with_morning = [r for r in in_week if r["morning"] is not None]

        if not in_week_with_morning:
            continue

        # 用户口径 (2026-07-31 确认): 每周一称重,到下周一早上称重,为一个周期
        # start = 该周周一晨重 (周一无数据则用该周第一条)
        # end   = 下周一晨重 (下周一未到/无数据则用该周最后一条,即进行中周)
        monday_rec = by_date.get(s_date)
        if monday_rec and monday_rec["morning"] is not None:
            start_w = monday_rec["morning"]
        else:
            start_w = in_week_with_morning[0]["morning"]

        next_monday_dt = monday + timedelta(days=7)
        next_monday = next_monday_dt.strftime("%Y-%m-%d")
        next_rec = by_date.get(next_monday)
        settled = next_rec is not None and next_rec["morning"] is not None
        if settled:
            end_w = next_rec["morning"]
        else:
            end_w = in_week_with_morning[-1]["morning"]

        # target = 该周任一天备注里的 "W15目标203" token (周一起跑日一般没定)
        wk_num = week_index + i
        target_w = None
        for r in in_week:
            if r.get("note"):
                m = target_re.search(r["note"])
                if m and int(m.group(1)) == wk_num:
                    target_w = float(m.group(2))
                    break  # 同周多个目标以第一条为准

        delta = round(end_w - start_w, 1)
        # 标签口径: delta 量的是"周一晨重 → 下周一晨重",label 也必须写到下周一,
        # 否则 label 写周日而 end 取下周一的值,页面上每一周都差一天 (2026-08-29 修)
        s_short = s_date[5:].replace("-", "/")
        e_short = next_monday[5:].replace("-", "/")
        # 进行中 = 结算日(下周一)晨重还没出来。
        # 原判据 days_in < 7 会在**周日**就把周判成已收盘,执行率卡直接下达标/未达标结论,
        # 到周一 end 换成下周一晨重、delta 又变一次 (2026-08-29 修)
        in_progress = not settled
        days_in = min(7, (datetime.strptime(
            max(d for d in by_date if s_date <= d <= e_date), "%Y-%m-%d") - monday).days + 1)
        label = f"{s_short}-{e_short}"
        if in_progress:
            label += f" ({days_in}天)"

        weeks.append({
            "week": f"W{week_index + i}",
            "label": label,
            "delta": delta,
            "start": start_w,
            "end": end_w,
            "color": WEEK_COLORS[i % len(WEEK_COLORS)],
            "target": target_w,  # None 表示该周未设目标
            "inProgress": in_progress,
        })

    # 只有最后一周才可能处于"进行中";历史周即使数据缺失(如周末未称重)
    # 也不算进行中,否则 W12 这类周会被误标
    for w in weeks[:-1]:
        w["inProgress"] = False

    return weeks


def js_escape(s):
    """Python 字符串 → JS 字符串字面量 (换行防御:JS 单引号字符串不允许字面换行)"""
    return (s.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
             .replace("\\", "\\\\").replace("'", "\\'"))


def write_js(out_path: Path, records, weekly, injections):
    """生成 weight_data.js"""
    lines = []
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # 兜底:整段 build 任一处出错时,尽可能把已 build 的 lines 写出去
    # (至少有 RAW 段,页面不会完全空;META 段下次 cron 再补)
    try:
      _build_js_content(lines, records, weekly, injections)
    except Exception as e:
      print(f"⚠ write_js build 异常: {e}", file=sys.stderr)
      print(f"  已 build {len(lines)} 行,尽力写出", file=sys.stderr)
    try:
      out_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
      print(f"⚠ write_js 末尾写入失败: {e}", file=sys.stderr)


def _build_js_content(lines, records, weekly, injections):
    """build lines 内容(抽出来便于 try/except 兜底)"""
    lines.append("// Auto-generated by sync_visualization.py — do not edit by hand.")
    lines.append(f"// Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # RAW 数组
    lines.append("const RAW = [")
    for r in records:
        m = "null" if r["morning"] is None else f"{r['morning']}"
        e = "null" if r["evening"] is None else f"{r['evening']}"
        note = js_escape(r["note"])
        lines.append(
            f"  {{date:'{r['date']}', morning:{m}, evening:{e}, note:'{note}'}},"
        )
    lines.append("];")
    lines.append("")

    # weeklyData 数组
    lines.append("const weeklyData = [")
    for w in weekly:
        target = "null" if w["target"] is None else f"{w['target']}"
        in_progress = "true" if w.get("inProgress") else "false"
        lines.append(
            f"  {{week:'{w['week']}', label:'{w['label']}', delta:{w['delta']}, "
            f"start:{w['start']}, end:{w['end']}, color:'{w['color']}', target:{target}, "
            f"inProgress:{in_progress}}},"
        )
    lines.append("];")
    lines.append("")

    # 排除 [插值 / [噪音 / [起点 标记的数据(不参与 MA7/streak/回归/恢复力统计;
    # 但仍参与图表绘制,只是非"实测"序列)。
    # ⚠️ 口径必须与前端 app.js 的 isRealPoint() 完全一致 —— 前端排除 [起点,
    #    sync 侧原来没排,导致"实测序列"两边差一个点 (恢复力基准从 244 起算)
    def is_excluded(record):
        note = record.get("note", "") or ""
        return "[噪音]" in note or "[插值" in note or "[起点" in note

    # peakWeight 例外:**不排除 [起点**,因为起点 244 就是历史最高,
    # 排除后会被 5/13 的 233.8 顶替 → peakWeight 错
    def is_excluded_for_peak(record):
        note = record.get("note", "") or ""
        return "[噪音]" in note or "[插值" in note

    real_mornings_for_peak = [r for r in records if r["morning"] is not None and not is_excluded_for_peak(r)]
    real_mornings = [r for r in records if r["morning"] is not None and not is_excluded(r)]
    if real_mornings:
        latest = real_mornings[-1]
        # peakWeight 从"全数据(不排除[起点]"里取
        peak = max(real_mornings_for_peak, key=lambda r: r["morning"])

        # MA7 / MA14:按自然日窗口 (最新日期往前 6/13 个自然日内的实测点平均)
        # 数据稀疏时点数少但时间口径准确;按"数据点窗口"在缺口期会跨太远失真
        latest_dt = datetime.strptime(latest["date"], "%Y-%m-%d")

        def natural_window(days_back):
            cutoff = (latest_dt - timedelta(days=days_back)).strftime("%Y-%m-%d")
            win = [r for r in real_mornings if r["date"] >= cutoff]
            return win

        last7 = natural_window(6)
        ma7 = sum(r["morning"] for r in last7) / len(last7) if last7 else None
        last14 = natural_window(13)
        ma14 = sum(r["morning"] for r in last14) / len(last14) if last14 else None
        # 近 14 天日均减重:两点端差 → OLS 最小二乘回归斜率 (2026-08-26 改)
        # 端差法被端点噪音绑架 (如起点恰是反弹日会虚高/虚低估),
        # 回归用全窗口 14 个实测点拟合,对水分波动更稳健,更能代表趋势中枢
        if len(real_mornings) >= 14:
            win = real_mornings[-14:]
            x0 = datetime.strptime(win[0]["date"], "%Y-%m-%d")
            xs = [(datetime.strptime(r["date"], "%Y-%m-%d") - x0).days for r in win]
            ys = [r["morning"] for r in win]
            n = len(xs)
            sx, sy = sum(xs), sum(ys)
            sxx = sum(x * x for x in xs)
            sxy = sum(x * y for x, y in zip(xs, ys))
            denom = n * sxx - sx * sx
            slope = (n * sxy - sx * sy) / denom if denom else 0.0
            daily_drop_14d = round(-slope, 2)
        else:
            daily_drop_14d = None

        # 近 7 天回归斜率 (前端情景预测/模拟器预设用,同口径)
        win7r = [r for r in real_mornings if r["date"] >= (latest_dt - timedelta(days=6)).strftime("%Y-%m-%d")]
        if len(win7r) >= 3:
            x0 = datetime.strptime(win7r[0]["date"], "%Y-%m-%d")
            xs7 = [(datetime.strptime(r["date"], "%Y-%m-%d") - x0).days for r in win7r]
            ys7 = [r["morning"] for r in win7r]
            n7 = len(xs7)
            sx7, sy7 = sum(xs7), sum(ys7)
            sxx7 = sum(x * x for x in xs7)
            sxy7 = sum(x * y for x, y in zip(xs7, ys7))
            denom7 = n7 * sxx7 - sx7 * sx7
            daily_drop_7d = round(-((n7 * sxy7 - sx7 * sy7) / denom7) if denom7 else 0.0, 2)
        else:
            daily_drop_7d = None

        # streak(连续下降天数)
        streak = 0
        for i in range(len(real_mornings) - 1, 0, -1):
            if real_mornings[i]["morning"] < real_mornings[i-1]["morning"]:
                streak += 1
            else:
                break

        # 本月减重: 当月1号(或之前最近) → 今天的晨重差
        latest_date = datetime.strptime(latest["date"], "%Y-%m-%d")
        month_start_str = latest_date.strftime("%Y-%m-01")
        # 找当月1号或之前最近的实测晨重
        month_start_morning = None
        for r in real_mornings:
            if r["date"] <= month_start_str:
                month_start_morning = r["morning"]
            else:
                break
        # 如果当月1号之前没数据(比如4月),用当月第一条
        if month_start_morning is None:
            for r in real_mornings:
                if r["date"].startswith(latest_date.strftime("%Y-%m")):
                    month_start_morning = r["morning"]
                    break
        if month_start_morning is not None:
            monthly_delta = round(month_start_morning - latest["morning"], 1)
        else:
            monthly_delta = None

        # 最佳单周: weeklyData 里 delta 最小(掉最多)的那周
        if weekly:
            best_week = min(weekly, key=lambda w: w["delta"])
            best_week_delta = best_week["delta"]
            best_week_label = best_week["week"]
        else:
            best_week_delta = None
            best_week_label = ""

        # 反弹恢复力: 每次反弹后重新跌破"反弹当时的历史低点"所需天数的中位数
        # ⚠️ 原实现只在反弹分支里推进 running_min,循环外那段追 min 是死代码,
        #    基准长期停在旧低点 → 算出的天数偏小且语义不是注释写的"回到新低" (2026-08-29 修)
        recovery_times = []
        rebound_total = 0
        run_min = real_mornings[0]["morning"] if real_mornings else None
        for i in range(1, len(real_mornings)):
            cur = real_mornings[i]
            prev = real_mornings[i-1]
            if cur["morning"] > prev["morning"]:
                rebound_total += 1
                base = run_min  # 反弹发生时的历史低点
                cur_date = datetime.strptime(cur["date"], "%Y-%m-%d")
                for j in range(i+1, len(real_mornings)):
                    if real_mornings[j]["morning"] < base:
                        new_low_date = datetime.strptime(real_mornings[j]["date"], "%Y-%m-%d")
                        recovery_times.append((new_low_date - cur_date).days)
                        break
            # running-min 逐点推进 (无论涨跌)
            if cur["morning"] < run_min:
                run_min = cur["morning"]

        if recovery_times:
            recovery_times.sort()
            mid = len(recovery_times) // 2
            if len(recovery_times) % 2 == 0:
                recovery_median = round((recovery_times[mid-1] + recovery_times[mid]) / 2, 1)
            else:
                recovery_median = recovery_times[mid]
        else:
            recovery_median = None

        # 周均减重 (较起点 244,已在下方 META 输出时直接算)

        lines.append("const META = {")
        lines.append(f"  currentWeight: {latest['morning']},")
        lines.append(f"  currentDate: '{latest['date']}',")
        lines.append(f"  startWeight: 244.0,  // QClaw 减肥计划起点")
        lines.append(f"  startDate: '2026-04-17',")
        # 业务目标参数 (前端 CONFIG 从 META 覆盖,避免 index.html 与数据双份硬编码)
        lines.append(f"  targetDate: '2026-11-22',  // 预测目标日")
        lines.append(f"  target160: 160.0,  // 过渡目标")
        lines.append(f"  target145: 145.0,  // 终极目标")
        lines.append(f"  milestone200: 200.2,  // 超越 2022-10-20")
        lines.append(f"  milestone188: 188.0,  // 历史最低")
        lines.append(f"  peakWeight: {peak['morning']},  // 全 CSV 历史最高 (排除 [噪音]/[插值],保留 [起点])")
        lines.append(f"  peakWeightHistorical: 244.0,  // 同 startWeight (历史峰值=起点)")
        lines.append(f"  totalDelta: {round(244.0 - latest['morning'], 1)},  // 较起点 244 (主指标)")
        days_from_start = (datetime.strptime(latest['date'], "%Y-%m-%d") -
                           datetime.strptime('2026-04-17', "%Y-%m-%d")).days
        lines.append(f"  days: {days_from_start},")
        lines.append(f"  avgWeekly: {round((244.0 - latest['morning']) / max(1, days_from_start / 7), 2)},")
        lines.append(f"  ma7: {round(ma7, 1)},")
        lines.append(f"  ma14: {round(ma14, 1) if ma14 is not None else 'null'},")
        lines.append(f"  dailyDrop14d: {daily_drop_14d if daily_drop_14d is not None else 'null'},  // 近 14 天日均减重 [OLS 回归] (斤/天)")
        lines.append(f"  dailyDrop7d: {daily_drop_7d if daily_drop_7d is not None else 'null'},  // 近 7 天日均减重 [OLS 回归] (斤/天)")
        lines.append(f"  streak: {streak},")
        lines.append(f"  monthlyDelta: {monthly_delta if monthly_delta is not None else 'null'},  // 本月减重 (当月1号→今天)")
        lines.append(f"  bestWeekDelta: {best_week_delta if best_week_delta is not None else 'null'},  // 最佳单周 delta")
        lines.append(f"  bestWeekLabel: '{best_week_label}',  // 最佳单周 W编号")
        lines.append(f"  recoveryMedian: {recovery_median if recovery_median is not None else 'null'},  // 反弹恢复力 (中位数天)")
        lines.append(f"  recoveryCount: {len(recovery_times)},  // 反弹后重回新低的样本数")
        lines.append(f"  reboundTotal: {rebound_total},  // 反弹总次数 (分母)")
        lines.append("};")
        lines.append("")

    # INJECTIONS_DATA 数组 (从替尔泊肽-注射记录.md 自动解析)
    lines.append("const INJECTIONS_DATA = [")
    for inj in injections:
        note_part = f", note:'{inj['note']}'" if inj.get("note") else ""
        lines.append(
            f"  {{date:'{inj['date']}', dose:{inj['dose']}, color:'{inj['color']}'{note_part}}},"
        )
    lines.append("];")
    lines.append("")

    lines.append(f"window.__SYNC_TIME__ = '{{}}';".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def parse_injections(md_path: Path):
    """解析替尔泊肽注射记录.md 的「实际注射记录」表格 → list of {date, dose, color, note}.

    表格格式 (markdown pipe table):
    | 针次 | 日期 | 剂量 | 间隔(天) | 备注 |
    | ① | 5/29(五)晚约20:00 | 2.5mg | — | 首针 |
    ...
    """
    if not md_path.exists():
        return []

    text = md_path.read_text(encoding="utf-8")
    # 只解析 "## 实际注射记录" 之后、"## 后续计划" 之前的部分
    m = re.search(r"##\s*实际注射记录(.*?)(?=##\s*后续计划|$)", text, re.DOTALL)
    if not m:
        return []
    section = m.group(1)

    # 剂量 → 颜色映射 (跟原 HTML 硬编码一致)
    DOSE_COLORS = {
        2.5: "#84cc16",
        5: "#eab308",
        6.75: "#f97316",
        7.5: "#f97316",
        10: "#ef4444",
    }

    injections = []
    # 匹配表格行: | ① | 5/29(五)晚约20:00 | 2.5mg | — | 首针 |
    # 日期可能是 "5/29(五)晚约20:00" 或 "7/22(三)晚" 等
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        # parts[0] = "" (leading |), parts[-1] = "" (trailing |)
        parts = [p for p in parts if p]
        if len(parts) < 4:
            continue
        # 跳过表头
        if parts[0] in ("针次", ":---:"):
            continue

        # parts[1] = 日期, parts[2] = 剂量, parts[4] = 备注 (如果有)
        date_raw = parts[1]
        dose_raw = parts[2]
        note = parts[4] if len(parts) > 4 else ""

        # 解析日期: "**7/16(四)晚约 18:00**" → "2026-07-16"
        # 用 search 而非 match,因为日期可能被 ** 包裹
        date_match = re.search(r"(\d+)/(\d+)", date_raw)
        if not date_match:
            continue
        month, day = int(date_match.group(1)), int(date_match.group(2))
        # 所有注射记录都是 2026 年
        date_str = f"2026-{month:02d}-{day:02d}"

        # 解析剂量: "2.5mg" → 2.5, "**10mg**" → 10
        # ⑥ 的剂量是 "5mg→**6.75mg（混合）**",取 → 后面的实际剂量
        if "→" in dose_raw:
            dose_raw = dose_raw.split("→")[-1]
        dose_match = re.search(r"([\d.]+)\s*mg", dose_raw)
        if not dose_match:
            continue
        dose = float(dose_match.group(1))

        # 跳过"已作废"或标记为"计划"的行
        # ⚠️ 只看**日期列**的"计划/预计"标记和整行 ~~ 删除线,不看备注列关键词:
        #    ⑨ 7/16 的备注"原 7/18 计划作废"讲的是旧计划作废(这针实际打了),
        #    原实现备注含"作废"/"计划"即跳过 → ⑨ 被误杀,INJECTIONS_DATA
        #    少 1 条(17→16),时间线 7/11→7/22 出现 11 天注射空窗 (2026-08-31 修)
        row_all = "|".join(parts)
        if "~~" in row_all:
            continue
        if "预计" in date_raw or "计划" in date_raw:
            continue

        color = DOSE_COLORS.get(dose, "#f97316")
        # 防御换行 + 转义 note + 剥离 markdown 星号 (tooltip 是 canvas 绘制,星号会原样显示)
        note_safe = (note.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                     .replace("**", "").replace("\\", "\\\\").replace("'", "\\'").strip())
        # 截断过长的 note (只取前 60 字;避免截在成对符号中间)
        if len(note_safe) > 60:
            cut = note_safe[:57]
            # 避免截在半截单词/剂量数字中间 (如 "7.5m..."),回退到最后一个分隔位
            if cut and cut[-1].isascii() and cut[-1].isalnum():
                m_cut = re.search(r"^.*[\s·,;；、，。（(]", cut)
                if m_cut and len(m_cut.group(0)) >= 40:
                    cut = m_cut.group(0)
            note_safe = cut.rstrip("·,;；、") + "..."

        injections.append({
            "date": date_str,
            "dose": dose,
            "color": color,
            "note": note_safe,
        })

    return injections


def main():
    args = parse_args()
    csv_path = Path(args.csv)
    out_path = Path(args.out)

    print(f"📖 Reading {csv_path}")
    records = load_csv(csv_path)
    print(f"  {len(records)} daily records (morning={sum(1 for r in records if r['morning'] is not None)})")

    print(f"📊 Computing weekly summary from {args.start_week}")
    weekly = compute_weekly_summary(records, args.start_week)
    print(f"  {len(weekly)} weeks:")
    for w in weekly:
        print(f"    {w['week']} {w['label']:20}  {w['start']:>5} → {w['end']:>5}  Δ {w['delta']:+.1f}")

    # 解析注射记录
    inj_path = Path("D:/Hermes/记录/替尔泊肽-注射记录.md")
    injections = parse_injections(inj_path)
    print(f"\n💉 Parsing {inj_path}")
    print(f"  {len(injections)} injections:")
    for inj in injections:
        note = f" ({inj['note']})" if inj.get("note") else ""
        print(f"    {inj['date']}  {inj['dose']}mg  {inj['color']}{note}")

    print(f"\n✏️  Writing {out_path}")
    write_js(out_path, records, weekly, injections)
    print(f"  ✓ {out_path} ({out_path.stat().st_size} bytes)")
    print(f"\n👉 Open {out_path.parent / 'index.html'} in browser to view.")


if __name__ == "__main__":
    main()
