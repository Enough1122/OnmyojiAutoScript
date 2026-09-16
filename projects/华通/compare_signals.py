# -*- coding: utf-8 -*-
"""信号逻辑 A/B 对比工具 —— 改评分规则前必须跑这个,别拍脑袋上线。

三种模式(见 analyze.generate_signal 的 price_mode):
  off   纯均线排列(现行基线)
  gate  排列需"价站上 MA5"才成立(空头排列同理)—— 修判定条件,不新增权重
  add   在基线之上叠加 价vsMA5/MA10 的加减分项 —— 权重是拍脑袋给的

判优标准(缺一不可):
  (1) 多头信号日后应偏涨(命中率>50% 且均值>0)
  (2) 空头信号日后应偏跌(命中率>50%)
  (3) 信号分布不能极端(把大多数日子都推成同一边 = 无区分度)
  (4) 前半段与后半段方向一致(否则只是拟合了这段噪声)

用法: python compare_signals.py [天数, 默认250]
"""
import sys
from stock_data import get_daily_kline, NAME
from analyze import generate_signal

MODES = ("off", "gate", "add")
LABEL = {"off": "off 纯排列(现行)", "gate": "gate 排列需价站上MA5", "add": "add 叠加位置权重"}
BULL, BEAR = {"+2", "+1"}, {"-2", "-1"}


def cls(d):
    return "多" if d in BULL else ("空" if d in BEAR else "中")


def collect(days=250, warmup=60):
    ks = get_daily_kline(days)
    rows = []
    for i in range(warmup, len(ks)):
        sub = ks[:i + 1]
        price = sub[-1]["close"]
        rec = {"date": sub[-1]["date"], "price": price, "fwd": {}}
        for m in MODES:
            rec[m] = generate_signal(sub, price_mode=m)["direction"]
        for la in (1, 3, 5):
            rec["fwd"][la] = ((ks[i + la]["close"] - price) / price * 100
                              if i + la < len(ks) else None)
        rows.append(rec)
    return rows, ks


def bucket(rows, mode, la, subset=None):
    rs = rows if subset is None else subset
    b = {"多": [], "空": [], "中": []}
    for r in rs:
        v = r["fwd"][la]
        if v is None:
            continue
        b[cls(r[mode])].append(v)
    out = {}
    for k, vals in b.items():
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        if k == "多":
            hit = sum(1 for v in vals if v > 0) / len(vals)
        elif k == "空":
            hit = sum(1 for v in vals if v < 0) / len(vals)
        else:
            hit = None
        out[k] = (len(vals), avg, hit)
    return out


def score_of(rows, mode):
    """综合分 = 各周期 多/空命中率 偏离50%的累计(越高越好)"""
    devs = []
    for la in (1, 3, 5):
        b = bucket(rows, mode, la)
        for k in ("多", "空"):
            if k in b and b[k][2] is not None:
                devs.append(b[k][2] - 0.5)
    return sum(devs) / len(devs) if devs else -9


def build_report(days=250):
    rows, ks = collect(days)
    if not rows:
        return "❌ 数据不足"
    L = [f"🔬 {NAME}(002602) 信号逻辑三模式对比 —— {rows[0]['date']} ~ {rows[-1]['date']}({len(rows)}个交易日)", ""]

    L.append("**① 信号分布**")
    L.append("| 模式 | 多 | 中 | 空 |")
    L.append("|---|---|---|---|")
    for m in MODES:
        c = {"多": 0, "中": 0, "空": 0}
        for r in rows:
            c[cls(r[m])] += 1
        L.append(f"| {LABEL[m]} | {c['多']} | {c['中']} | {c['空']} |")
    L.append("")

    L.append("**② 信号有效性**(多头信号日后应偏涨、空头应偏跌)")
    L.append("| 模式 | 周期 | 多·命中/均值 | 空·命中/均值 |")
    L.append("|---|---|---|---|")
    for m in MODES:
        for la in (1, 3, 5):
            b = bucket(rows, m, la)
            def cell(k):
                if k not in b:
                    return "—"
                n, avg, hit = b[k]
                return f"{hit*100:.0f}% / {avg:+.2f}%"
            L.append(f"| {LABEL[m]} | {la}日 | {cell('多')} | {cell('空')} |")
    L.append("")

    half = len(rows) // 2
    L.append("**③ 分半一致性**(前/后半段各自的多空命中偏离)")
    for m in MODES:
        s1, s2 = score_of(rows[:half], m), score_of(rows[half:], m)
        agree = "一致" if (s1 > 0) == (s2 > 0) else "⚠️ 不一致"
        L.append(f"    {LABEL[m]}: 前半 {s1*100:+.1f}pt / 后半 {s2*100:+.1f}pt → {agree}")
    L.append("")

    L.append("**④ 综合排序**(多空命中率偏离50%的均值,越高越好)")
    rank = sorted(MODES, key=lambda m: -score_of(rows, m))
    for i, m in enumerate(rank, 1):
        L.append(f"    {i}. {LABEL[m]}  {score_of(rows, m)*100:+.1f}pt")
    best = rank[0]
    base = score_of(rows, "off")
    L.append("")

    L.append(f"**⑤ 分歧日抽查**(off 与 {LABEL[best]} 判断不同、且有后续数据的日子,后续3日)")
    diffs = [r for r in rows
             if cls(r["off"]) != cls(r[best]) and r["fwd"][3] is not None
             and (cls(r["off"]) != "中" or cls(r[best]) != "中")]
    if diffs:
        good = 0
        for r in diffs[:10]:
            L.append(f"    {r['date']} 价{r['price']:.2f} | off {r['off']} → {best} {r[best]} | 后续3日 {r['fwd'][3]:+.2f}%")
        # 统计谁在分歧日更准
        for r in diffs:
            v = r["fwd"][3]
            if cls(r[best]) == "空" and v < 0:
                good += 1
            elif cls(r[best]) == "多" and v > 0:
                good += 1
        L.append(f"    合计 {len(diffs)} 个硬分歧日,{LABEL[best]} 判对 {good} 天({good/len(diffs)*100:.0f}%)")
    else:
        L.append("    无硬分歧日")
    L.append("")
    L.append(f"**结论**:综合最优 = {LABEL[best]}(基线 {base*100:+.1f}pt → {score_of(rows,best)*100:+.1f}pt)")
    L.append("⚠️ 历史不代表未来;样本有限时只看方向性差异,勿当精确胜率。")
    return "\n".join(L)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    print(build_report(n))
