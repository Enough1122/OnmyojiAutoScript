# -*- coding: utf-8 -*-
"""世纪华通(002602) 三段式报告 — 供每小时 cron 投递(no_agent,零 token)
用法: python report.py
输出: 飞书友好文本(技术面 / 基本面 / 事件面),直接 print 到 stdout

设计:
  技术面 = 实时行情 + 技术指标(腾讯主源,新浪交叉校验)
  基本面 = 缓存财务 + 现价本地算估值(零 API 调用,见 fundamentals.py)
  事件面 = 妙想权威资讯(30 分钟缓存 + 噪音过滤,见 news.py)
  三段任一失败都静默降级,不阻断报告 —— 宁可少一段,不可整份消失。
"""
import datetime
from stock_data import get_realtime, get_daily_kline, NAME, cross_check
from analyze import generate_signal, direction_label
from fundamentals import snapshot as fund_snapshot
from news import line as news_line


def is_trading_now(rt):
    """判断当前是否 A 股交易时段(含集合竞价与收盘),非交易日返回 False"""
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return False
    hh, mm = now.hour, now.minute
    t = hh * 60 + mm
    return (9 * 60 + 15) <= t <= (15 * 60 + 0)


def build_advice(d, price, m, inv):
    """建议文案由【实际条件】生成,不用固定模板。

    旧版是写死的:"多头信号为主:站上 MA5 且 MACD 红柱走强可关注;跌破 MA10 则信号失效。"
    —— 文案里的失效条件一旦与现实相反,报告就自相矛盾:2026-09-14 全天价格都在 MA10 下方
    (最低 -3.66%),文案每天照念"跌破 MA10 则信号失效",而信号一次都没失效。"""
    ma5, ma10, ma20 = m["ma5"], m["ma10"], m["ma20"]
    pos5 = f"站上MA5({ma5:.2f})" if price > ma5 else f"跌破MA5({ma5:.2f})"
    pos10 = f"站上MA10({ma10:.2f})" if price > ma10 else f"跌破MA10({ma10:.2f})"
    loc = f"{pos5}、{pos10}"

    if d in ("+2", "+1"):
        if inv.get("bull_intact"):
            return f"{loc};多头成立 —— 回踩 MA10({ma10:.2f}) 不破可持,跌破即失效离场。"
        return (f"{loc};⚠️ 价格已在 MA10({ma10:.2f}) 下方 —— 多头信号按规则不成立,"
                f"等站回 MA10 上方再谈。")
    if d in ("+0.5", "0"):
        return (f"{loc};多空抵消/纠缠,方向未定 —— 等 MA5({ma5:.2f}) 与 MA10({ma10:.2f}) "
                f"给出方向再动,别猜。")
    return (f"{loc};反弹到 MA10({ma10:.2f})/MA20({ma20:.2f}) 是压力位,"
            f"站不回 MA10 之前按弱势处理。")


def signal_tag(d, price, m):
    """方向标签 + 位置冲突标注。

    评分是历史信号(过去趋势的残影),价格位置是当下事实,两者可以冲突。
    冲突本身就是最有价值的信息 —— 不隐藏、也不强行对齐:两个"对齐"方案
    (gate/add)都已被 compare_signals.py 的历史检验否掉(多头命中率反而下降)。"""
    label = direction_label(d)
    ma10 = m["ma10"]
    if d in ("+2", "+1") and price < ma10:
        return f"{label} ⚠️已破 MA10"
    if d in ("-2", "-1") and price > ma10:
        return f"{label} ⚠️已上 MA10"
    return label


def build_report():
    rt = get_realtime()
    ks = get_daily_kline(120)
    sig = generate_signal(ks)
    m = sig["metrics"]
    trading = is_trading_now(rt)

    price = rt["price"]
    pct = rt["change_pct"]
    session = "盘中速报" if trading else "收盘复盘"

    lines = []
    lines.append(f"📈 {NAME}({rt['code']}) {session}")
    lines.append(f"现价 **{price:.2f}** ({pct:+.2f}%) | 开 {rt['open']:.2f} 高 {rt['high']:.2f} 低 {rt['low']:.2f}")

    # 双源交叉校验:正常静默,只有分歧/降级才显形(报告不因校验变长)
    cok, clines = cross_check(rt)
    if not cok:
        lines.append("🔍 数据校验:")
        lines.extend(clines)

    # ---------- 三段式:技术面 / 基本面 / 事件面 ----------
    d = sig["direction"]
    advice = build_advice(d, price, m, sig.get("invalidation", {}))

    # ① 技术面(一句话 + 一行指标)
    head = f"【技术面】{signal_tag(d, price, m)}(评分 {sig['score']:+.0f})"
    if sig["reasons"]:
        head += " ｜ " + " ｜ ".join(sig["reasons"][:3])
    lines.append(head)
    lines.append(f"　MA5 {m['ma5']:.2f}/MA10 {m['ma10']:.2f}/MA20 {m['ma20']:.2f}/MA60 {m['ma60']:.2f}"
                 f" ｜ MACD柱 {m['hist']:+.3f} RSI {m['rsi14']:.0f}"
                 f" ｜ KDJ {m['kdj'][0]:.0f}/{m['kdj'][1]:.0f}/{m['kdj'][2]:.0f}")

    # ② 基本面(本地计算,零 API 调用;失败静默降级)
    try:
        biz, val = fund_snapshot(price)
        lines.append(f"【基本面】{biz}")
        lines.append(f"　{val}")
    except Exception:
        pass

    # ③ 事件面(妙想权威资讯,30 分钟缓存;失败静默降级)
    try:
        nl = news_line(days=3, max_items=2)
        if nl:
            lines.append(f"【事件面】{nl}")
    except Exception:
        pass

    lines.append(f"💡 {advice}")
    lines.append("📊 信号历史检验:多头5日超额+0.3pt(样本31天,不显著)·空头无预测力 —— 信号是坐标,不是买卖依据。")
    lines.append("⚠️ 自动化分析仅供参考，不构成投资建议。")
    return "\n".join(lines)


if __name__ == "__main__":
    print(build_report())
