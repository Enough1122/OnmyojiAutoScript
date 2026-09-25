# -*- coding: utf-8 -*-
"""技术指标计算 + 买卖信号生成(世纪华通 002602)"""
import math


# ---------- 序列指标 ----------

def ma_series(closes, n):
    """MA(n) 序列, 前 n-1 个为 None"""
    out, s = [], 0.0
    for i, c in enumerate(closes):
        s += c
        if i >= n:
            s -= closes[i - n]
        out.append(s / n if i >= n - 1 else None)
    return out


def ema_series(values, n):
    """EMA(n) 序列(首值播种)"""
    k = 2.0 / (n + 1)
    e = values[0]
    out = [e]
    for v in values[1:]:
        e = v * k + e * (1 - k)
        out.append(e)
    return out


def macd(closes, fast=12, slow=26, signal=9):
    """返回 (dif_series, dea_series, hist_series)"""
    if len(closes) < slow:
        return None, None, None
    ef = ema_series(closes, fast)
    es = ema_series(closes, slow)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema_series(dif, signal)
    hist = [(a - b) * 2 for a, b in zip(dif, dea)]
    return dif, dea, hist


def rsi_series(closes, n=14):
    """RSI(n) 序列, 前 n 个为 None"""
    if len(closes) <= n:
        return [None] * len(closes)
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    out = [None] * (n + 1)
    avg_g, avg_l = sum(gains[:n]) / n, sum(losses[:n]) / n
    out.append(100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l))
    for i in range(n, len(gains)):
        avg_g = (avg_g * (n - 1) + gains[i]) / n
        avg_l = (avg_l * (n - 1) + losses[i]) / n
        out.append(100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l))
    return out


def kdj_series(klines, n=9):
    """KDJ(9) -> (k_series, d_series, j_series)"""
    k, d = 50.0, 50.0
    ks, ds, js = [], [], []
    for i in range(len(klines)):
        lo = min(klines[max(0, i - n + 1):i + 1], key=lambda x: x["low"])["low"]
        hi = max(klines[max(0, i - n + 1):i + 1], key=lambda x: x["high"])["high"]
        rsv = (klines[i]["close"] - lo) / (hi - lo) * 100 if hi != lo else 50.0
        k = (2.0 / 3) * k + (1.0 / 3) * rsv
        d = (2.0 / 3) * d + (1.0 / 3) * k
        ks.append(k); ds.append(d); js.append(3 * k - 2 * d)
    return ks, ds, js


def boll(closes, n=20, width=2.0):
    """BOLL(n) -> (lower, mid, upper) 最新一根"""
    if len(closes) < n:
        return None
    mid = sum(closes[-n:]) / n
    var = sum((c - mid) ** 2 for c in closes[-n:]) / n
    sd = math.sqrt(var)
    return mid - width * sd, mid, mid + width * sd


# ---------- 交叉判断 ----------

def cross_up(a, b):
    """a 上穿 b: 前值 a<=b 且现值 a>b"""
    if len(a) < 2 or a[-2] is None or a[-1] is None or b[-2] is None or b[-1] is None:
        return False
    return a[-2] <= b[-2] and a[-1] > b[-1]


def cross_down(a, b):
    """a 下穿 b"""
    if len(a) < 2 or a[-2] is None or a[-1] is None or b[-2] is None or b[-1] is None:
        return False
    return a[-2] >= b[-2] and a[-1] < b[-1]


# ---------- 信号生成 ----------

def generate_signal(klines, price_mode="off"):
    """综合买卖信号
    返回 dict: score(int), direction(str), reasons[list], metrics(dict), invalidation(dict)
    direction: +2强买 +1偏买 0观望 -1偏卖 -2强卖
    price_mode: 如何处理"价格 vs 短期均线的当下位置"
      'off'  = 旧逻辑,均线排列只看 MA5>MA10>MA20,不看价格在哪
      'gate' = 门控:排列必须配合"价站上 MA5"才算成立,否则判为排列瓦解中
      'add'  = 叠加:在旧逻辑上新增 价vsMA5/MA10 的加减分项
    默认 'off'(改动须先跑 compare_signals.py 验证优于基线)
    """
    closes = [k["close"] for k in klines]
    price = closes[-1]
    score = 0
    reasons = []
    metrics = {}

    # 均线系统
    ma5 = ma_series(closes, 5)
    ma10 = ma_series(closes, 10)
    ma20 = ma_series(closes, 20)
    ma60 = ma_series(closes, 60)
    metrics["ma5"], metrics["ma10"], metrics["ma20"], metrics["ma60"] = ma5[-1], ma10[-1], ma20[-1], ma60[-1]

    if ma5[-1] and ma10[-1] and ma20[-1]:
        if ma5[-1] > ma10[-1] > ma20[-1]:
            if price_mode == "gate" and price <= ma5[-1]:
                score -= 1
                reasons.append(f"多头排列瓦解中:价({price:.2f})已跌破 MA5({ma5[-1]:.2f})")
            else:
                score += 1
                reasons.append(f"均线多头排列 MA5({ma5[-1]:.2f})>MA10({ma10[-1]:.2f})>MA20({ma20[-1]:.2f})")
        elif ma5[-1] < ma10[-1] < ma20[-1]:
            if price_mode == "gate" and price >= ma5[-1]:
                score += 1
                reasons.append(f"空头排列瓦解中:价({price:.2f})已站上 MA5({ma5[-1]:.2f})")
            else:
                score -= 1
                reasons.append(f"均线空头排列 MA5({ma5[-1]:.2f})<MA10({ma10[-1]:.2f})<MA20({ma20[-1]:.2f})")
    if cross_up(ma5, ma10):
        score += 1; reasons.append("MA5 上穿 MA10(金叉)")
    if cross_down(ma5, ma10):
        score -= 1; reasons.append("MA5 下穿 MA10(死叉)")

    # MACD
    dif, dea, hist = macd(closes)
    metrics["dif"], metrics["dea"], metrics["hist"] = (dif[-1], dea[-1], hist[-1]) if dif else (None, None, None)
    if dif:
        # MACD 交叉与红绿柱翻正是同一波动的重复表达；交叉计分，柱体只解释。
        if cross_up(dif, dea):
            score += 1
            reasons.append("MACD 金叉")
        if cross_down(dif, dea):
            score -= 1
            reasons.append("MACD 死叉")
        if hist[-1] > 0 and hist[-2] <= 0:
            reasons.append("MACD 红柱翻正")
        if hist[-1] < 0 and hist[-2] >= 0:
            reasons.append("MACD 绿柱翻负")
        if dif[-1] > 0:
            score += 0.5 if hist[-1] > hist[-2] else 0
        else:
            score -= 0.5 if hist[-1] < hist[-2] else 0

    # RSI
    rsi = rsi_series(closes, 14)
    metrics["rsi14"] = rsi[-1]
    if rsi[-1] is not None:
        if rsi[-1] >= 70:
            score -= 1; reasons.append(f"RSI 超买({rsi[-1]:.0f})")
        elif rsi[-1] <= 30:
            score += 1; reasons.append(f"RSI 超卖({rsi[-1]:.0f})")

    # KDJ
    kk, dd, jj = kdj_series(klines, 9)
    metrics["kdj"] = (kk[-1], dd[-1], jj[-1])
    if cross_up(kk, dd) and kk[-1] < 50:
        score += 1; reasons.append(f"KDJ 低位金叉(K{kk[-1]:.0f}/{dd[-1]:.0f})")
    if cross_down(kk, dd) and kk[-1] > 50:
        score -= 1; reasons.append(f"KDJ 高位死叉(K{kk[-1]:.0f}/{dd[-1]:.0f})")

    # 布林带
    bb = boll(closes, 20)
    metrics["boll"] = bb
    if bb:
        low_b, mid_b, up_b = bb
        if price <= low_b * 1.005:
            score += 1; reasons.append(f"触及布林下轨({low_b:.2f}),超卖区")
        elif price >= up_b * 0.995:
            score -= 1; reasons.append(f"触及布林上轨({up_b:.2f}),超买区")

    # 收盘相对位置
    if ma20[-1]:
        if price > ma20[-1]:
            score += 0.5
        else:
            score -= 0.5

    # 价格 vs 短期均线的"当下位置" —— 与上面的均线排列是两件事。
    # 排列是过去趋势的残影(急涨后能滞后一周以上:9/4 的 +7.96% 撑着一周后的
    # "多头排列",而价格已连跌 5 天),价格位置才是当下的多空事实。
    # 破位侧权重更高:宁可迟报买点,不可在破位时还喊多头。
    if price_mode == "add":
        if ma5[-1]:
            if price > ma5[-1]:
                score += 0.5
                reasons.append(f"站上 MA5({ma5[-1]:.2f})")
            else:
                score -= 1.0
                reasons.append(f"跌破 MA5({ma5[-1]:.2f})")
        if ma10[-1] and price < ma10[-1]:
            score -= 1.0
            reasons.append(f"跌破 MA10({ma10[-1]:.2f})")

    score = round(score)
    if score >= 3:
        direction = "+2"
    elif score == 2:
        direction = "+1"
    elif score == 1:
        direction = "+0.5"
    elif score <= -3:
        direction = "-2"
    elif score == -2:
        direction = "-1"
    elif score == -1:
        direction = "-0.5"
    else:
        direction = "0"

    return {"score": score, "direction": direction, "reasons": reasons,
            "metrics": metrics,
            "invalidation": {"ma5": ma5[-1], "ma10": ma10[-1], "ma20": ma20[-1],
                             "bull_intact": bool(ma10[-1] and price > ma10[-1])}}


def direction_label(direction):
    return {
        "+2": "🟢 强买",
        "+1": "🟢 偏买",
        "+0.5": "🟡 谨慎偏多",
        "0": "⚪ 观望",
        "-0.5": "🟠 谨慎偏空",
        "-1": "🔴 偏卖",
        "-2": "🔴 强卖",
    }.get(direction, "⚪ 观望")
