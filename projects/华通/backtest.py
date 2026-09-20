# -*- coding: utf-8 -*-
"""世纪华通(002602) 策略回溯与优化建议 — 每3天收盘后运行(no_agent,零 token)
用法: python backtest.py
逻辑: 对近250个交易日逐日检测各技术信号,统计信号发出后 1/3/5 日的涨跌胜率与
      相对全样本基准的超额收益;样本不足(小样本)时不下"高置信"结论,输出优化建议。
"""
from stock_data import get_daily_kline, NAME
from analyze import ma_series, ema_series, rsi_series, kdj_series


def boll_series(closes, n=20, width=2.0):
    out = []
    for i in range(len(closes)):
        if i < n - 1:
            out.append(None)
            continue
        mid = sum(closes[i - n + 1:i + 1]) / n
        var = sum((c - mid) ** 2 for c in closes[i - n + 1:i + 1]) / n
        sd = var ** 0.5
        out.append((mid - width * sd, mid, mid + width * sd))
    return out


def collect_signals(klines):
    closes = [k["close"] for k in klines]
    ma5 = ma_series(closes, 5)
    ma10 = ma_series(closes, 10)
    ef = ema_series(closes, 12)
    es = ema_series(closes, 26)
    dif_s = [a - b for a, b in zip(ef, es)]
    dea_s = ema_series(dif_s, 9)
    rsi_s = rsi_series(closes, 14)
    kk, dd, _ = kdj_series(klines, 9)
    boll_s = boll_series(closes, 20)

    signals = {
        "MA5/10金叉": [], "MA5/10死叉": [],
        "MACD金叉": [], "MACD死叉": [],
        "RSI超卖(<30)": [], "RSI超买(>70)": [],
        "KDJ金叉": [], "KDJ死叉": [],
        "触及布林下轨": [], "触及布林上轨": [],
    }
    for i in range(35, len(klines) - 5):
        if ma5[i - 1] is not None and ma10[i - 1] is not None and ma5[i] is not None and ma10[i] is not None:
            if ma5[i - 1] <= ma10[i - 1] and ma5[i] > ma10[i]:
                signals["MA5/10金叉"].append((i, +1))
            if ma5[i - 1] >= ma10[i - 1] and ma5[i] < ma10[i]:
                signals["MA5/10死叉"].append((i, -1))
        if dif_s[i - 1] <= dea_s[i - 1] and dif_s[i] > dea_s[i]:
            signals["MACD金叉"].append((i, +1))
        if dif_s[i - 1] >= dea_s[i - 1] and dif_s[i] < dea_s[i]:
            signals["MACD死叉"].append((i, -1))
        if rsi_s[i] is not None:
            if rsi_s[i] <= 30:
                signals["RSI超卖(<30)"].append((i, +1))
            if rsi_s[i] >= 70:
                signals["RSI超买(>70)"].append((i, -1))
        if kk[i - 1] <= dd[i - 1] and kk[i] > dd[i]:
            signals["KDJ金叉"].append((i, +1))
        if kk[i - 1] >= dd[i - 1] and kk[i] < dd[i]:
            signals["KDJ死叉"].append((i, -1))
        if boll_s[i]:
            low_b, mid_b, up_b = boll_s[i]
            if klines[i]["close"] <= low_b * 1.005:
                signals["触及布林下轨"].append((i, +1))
            if klines[i]["close"] >= up_b * 0.995:
                signals["触及布林上轨"].append((i, -1))
    return closes, signals


def baseline(klines, lookahead=(1, 3, 5)):
    """全样本基准: 同一持有期内随便一天的均涨跌(%)与上涨占比 —— 用来剔除"漂移"

    没有基准的胜率会骗人: 一段上涨行情里任何"买"信号都显得很准,一段下跌行情里
    任何"卖"信号都显得很准。基准就是那句"什么都不做"的对照线。
    """
    closes = [k["close"] for k in klines]
    out = {}
    for la in lookahead:
        chgs = [(closes[i + la] - closes[i]) / closes[i] * 100
                for i in range(len(closes) - la)]
        out[la] = (sum(chgs) / len(chgs), sum(1 for c in chgs if c > 0) / len(chgs) * 100)
    return out


def evaluate(klines, lookahead=(1, 3, 5)):
    closes, signals = collect_signals(klines)
    base = baseline(klines, lookahead)
    rows = []
    for name, items in signals.items():
        if not items:
            continue
        for dname, direction in (("买", +1), ("卖", -1)):
            group = [it for it in items if it[1] == direction]
            if len(group) < 3:
                continue
            for la in lookahead:
                wins, total, pnl = 0, 0, 0.0
                for idx, _ in group:
                    if idx + la >= len(closes):
                        continue
                    chg = (closes[idx + la] - closes[idx]) / closes[idx]
                    pnl += chg if direction == +1 else -chg
                    if (chg > 0) == (direction == +1):
                        wins += 1
                    total += 1
                if total >= 3:
                    avg = pnl / total * 100
                    rows.append((name, dname, la, wins, total, avg,
                                 avg - direction * base[la][0]))
    return rows, base


def build_report():
    ks = get_daily_kline(250)      # 120 天时交叉类信号只有 3~4 个样本,统计上等于没有
    if not ks:
        return "❌ 无法获取行情数据"
    last_date = ks[-1]["date"]
    rows, base = evaluate(ks)
    MIN_N = 8                      # 低于这个样本数一律不下结论(原来是"胜率≥60%就高置信")
    lines = []
    lines.append(f"🔁 {NAME}(002602) 策略回溯报告(截至 {last_date},近{len(ks)}个交易日)")
    lines.append("统计各信号发出后 1/3/5 日收盘涨跌胜率;超额 = 均收益 - 全样本基准:")
    lines.append("")
    lines.append("| 信号 | 方向 | 持有 | 胜率 | 样本 | 均收益 | 超额 |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, dname, la, wins, total, avg_pnl, excess in rows:
        rate = wins / total * 100
        flag = "✅" if (rate >= 60 and excess > 0) else ("🟡" if rate >= 50 else "❌")
        lines.append(f"| {name} | {dname} | {la}日 | {rate:.0f}%{flag} | {total} | "
                     f"{avg_pnl:+.2f}% | {excess:+.2f}% |")
    lines.append("")
    lines.append("基准(全样本同期 均涨跌/上涨占比): "
                 + " · ".join(f"{la}日 {base[la][0]:+.2f}%/{base[la][1]:.0f}%" for la in (1, 3, 5)))

    # 优化建议:按 (信号,方向) 分组,每组只归一类(避免同一信号既高置信又低效)
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        groups[(r[0], r[1])].append(r)

    lines.append("")
    lines.append("**优化建议:**")
    good, bad, thin = [], [], []
    for (name, dname), rs in groups.items():
        label = f"{name}({dname})"
        max_n = max(x[4] for x in rs)
        if max_n < MIN_N:
            thin.append((label, max_n))
            continue
        if any(x[3] / x[4] >= 0.6 and x[5] > 0 and x[6] > 0 for x in rs):
            good.append((label, max_n))
        elif all(x[3] / x[4] < 0.5 or x[6] <= 0 for x in rs):
            bad.append((label, max_n))
    if good:
        good.sort(key=lambda x: -x[1])
        lines.append("· 高置信信号: " + "、".join(l for l, _ in good[:6]) + " —— 保留并优先采信")
    else:
        lines.append(f"· 暂无高置信信号(门槛: 样本≥{MIN_N} 且 胜率≥60% 且 超额>0)")
    if bad:
        lines.append("· 低效信号: " + "、".join(f"{l}(n={n})" for l, n in bad[:6]) + " —— 建议降权或忽略")
    if thin:
        lines.append(f"· 样本不足(最大样本 <{MIN_N}): "
                     + "、".join(f"{l} n={n}" for l, n in thin[:8]) + " —— 本期不下结论")
    lines.append(f"· 样本<{MIN_N} 的信号统计意义有限,勿重仓押单一信号;多信号共振(≥2个同向)再行动")
    lines.append("⚠️ 历史胜率不代表未来,仅供参考。")
    return "\n".join(lines)


if __name__ == "__main__":
    print(build_report())
