# -*- coding: utf-8 -*-
"""世纪华通(002602) 三段式报告 — 供每小时 cron 投递(no_agent,零 token)
用法: python report.py
输出: 飞书友好文本(技术面 / 基本面 / 事件面),直接 print 到 stdout

设计:
  技术面 = 实时行情 + 技术指标(腾讯主源,新浪交叉校验)
  基本面 = 缓存财务 + 现价本地算估值(零 API 调用,见 fundamentals.py)
  事件面 = 东财公司公告(30 分钟缓存 + 噪音过滤,见 news.py)
  三段任一失败都静默降级,不阻断报告 —— 宁可少一段,不可整份消失。
"""
import datetime
from robust_backtest import research_state
from stock_data import get_realtime, get_daily_kline, NAME, cross_check
from analyze import generate_signal
from fundamentals import snapshot as fund_snapshot
from news import line as news_line
from corp_actions import line as corp_actions_line


# A 股时段(分钟): 集合竞价 9:15 起, 午休 11:30–13:00, 尾盘 15:00 收
_AM = (9 * 60 + 15, 11 * 60 + 30)
_PM = (13 * 60, 15 * 60)


def session_state():
    """当前时段 -> 'open'(可成交) / 'break'(午间休市) / 'closed'(盘前盘后·周末)

    午休必须单列: 11:30–13:00 行情是冻结的早盘收盘价,继续标"盘中速报"会让人
    以为价格还在动(2026-09-17 12:00 那班就是这样,14.49 其实是 11:30 的价)。
    """
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return "closed"
    t = now.hour * 60 + now.minute
    if _AM[0] <= t <= _AM[1] or _PM[0] <= t < _PM[1]:
        return "open"
    if _AM[1] < t < _PM[0]:
        return "break"
    return "closed"


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
            return f"{loc};技术面呈多头观察状态 —— 仅记录，不构成交易指令。"
        return (f"{loc};⚠️ 技术面多头观察与价格位置冲突（现价在 MA10({ma10:.2f}) 下方），"
                "仅记录，不构成交易指令。")
    if d in ("+0.5", "0"):
        return (f"{loc};多空抵消/纠缠，方向未定 —— 仅记录观察，不构成交易指令。")
    return (f"{loc};技术面呈弱势观察状态，MA10({ma10:.2f})/MA20({ma20:.2f}) 是观察位，"
            "不构成交易指令。")


def signal_tag(d, price, m):
    """方向标签只描述技术观察坐标，不输出买卖指令。"""
    label = {
        "+2": "🟢 技术偏多",
        "+1": "🟢 技术偏多",
        "+0.5": "🟡 技术略偏多",
        "0": "⚪ 技术中性",
        "-0.5": "🟠 技术略偏空",
        "-1": "🔴 技术偏空",
        "-2": "🔴 技术偏空",
    }.get(d, "⚪ 技术中性")
    ma10 = m["ma10"]
    if d in ("+2", "+1") and price < ma10:
        return f"{label} ⚠️已破 MA10·非交易指令"
    if d in ("-2", "-1") and price > ma10:
        return f"{label} ⚠️已上 MA10·非交易指令"
    return f"{label}·观察·非交易指令"


def research_digest(research_bars):
    """从结构化研究状态生成小时报摘要；不解析 Markdown，也不回退旧快照。"""
    try:
        state = research_state(research_bars)
        observations = state.get("holdout_failed_observations", [])
        as_of = state.get("as_of") or (research_bars[-1]["date"] if research_bars else "未知")
        sample_size = state.get("sample_size", len(research_bars))
        if observations:
            details = []
            for row in observations:
                detail = f"{row.get('name', '未命名')}/{row.get('hold_days', '?')}日（留出未通过）"
                details.append(detail)
            return (
                f"📊 稳健回测({as_of}, {sample_size}根K): 研究观察留出未通过："
                f"{'、'.join(details)}；仅作影子观察，不等于生产信号，不自动下单；"
                "成本为研究假设，非账户实际费率。"
            )
        if state.get("observations"):
            passed = "、".join(
                f"{row.get('name', '未命名')}/{row.get('hold_days', '?')}日（留出通过）"
                for row in state["observations"]
            )
            return (
                f"📊 稳健回测({as_of}, {sample_size}根K): 研究观察：{passed}；"
                "仅作影子观察，不等于生产信号，不自动下单；"
                "成本为研究假设，非账户实际费率。"
            )
        return (
            f"📊 稳健回测({as_of}, {sample_size}根K): 本轮研究观察名单为空；"
            "技术评分不等于生产信号，仅作观察，不自动下单。"
        )
    except Exception:
        return "📊 稳健回测暂不可用；本轮不引用旧快照，技术评分仅作观察。"


def build_report():
    rt = get_realtime()
    research_bars = get_daily_kline(750)
    state = session_state()
    # 盘中/午休的最后一根日K可能仍在形成；正式技术信号只用上一根完整日K。
    signal_bars = research_bars[-121:-1] if state in ("open", "break") and len(research_bars) > 1 else research_bars[-120:]
    sig = generate_signal(signal_bars)
    m = sig["metrics"]

    price = rt["price"]
    pct = rt["change_pct"]
    session = {"open": "盘中速报", "break": "午间休市速览", "closed": "收盘复盘"}[state]

    lines = []
    lines.append(f"📈 {NAME}({rt['code']}) {session}")
    lines.append(f"现价 **{price:.2f}** ({pct:+.2f}%) | 开 {rt['open']:.2f} 高 {rt['high']:.2f} 低 {rt['low']:.2f}")
    if state == "break":
        lines.append("⏸ 午间休市: 以上为 11:30 早盘收盘价,13:00 恢复交易")

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

    # ③ 事件面(东财公司公告,30 分钟缓存;失败静默降级)
    try:
        nl = news_line(days=3, max_items=2)
        if nl:
            lines.append(f"【事件面】{nl}")
    except Exception:
        pass

    # ④ 前瞻事件面(除权除息等已知公司行动 —— news.py 只看过去,这里看将来)
    try:
        ca = corp_actions_line(days=7)
        if ca:
            lines.append(ca)
    except Exception:
        pass

    lines.append(f"💡 {advice}")
    lines.append(research_digest(research_bars))
    lines.append("⚠️ 自动化分析仅供参考，不构成投资建议。")
    return "\n".join(lines)


if __name__ == "__main__":
    print(build_report())
