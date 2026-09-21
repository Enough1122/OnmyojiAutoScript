# -*- coding: utf-8 -*-
"""前瞻事件面 —— 已知的公司行动(分红/送转/除权除息),带缓存与失败降级。

为什么要它: 事件面(news.py)只看**过去** N 天的公告,而除权除息这类事件的影响在
**将来** —— 2026-09-24 世纪华通除权除息(10派0.80元),开盘参考价会自然下移约
0.08 元/股(≈0.55%)。若报告不提前说,当天看到"跌 0.55%"会误判成破位。
公告标题里只有"2026年中期权益分派实施公告",日期在正文里,所以走东财数据中心的
结构化接口(RPT_SHAREBONUS_DET),直接拿 股权登记日/除权除息日/每10股派息。

设计:
  1. 12 小时缓存 —— 公司行动极低频,没必要每小时查;
  2. 只在**窗口内**(默认未来 7 天,或就是今天)才渲染,平时完全静默不占行;
  3. 任何失败静默返回 None —— 与 news.py 一致,宁可少一段不可整份消失。

命名注意: 本文件**不能**叫 calendar.py —— 会遮蔽标准库 calendar(pandas 依赖它)。

用法: python corp_actions.py [窗口天数]
"""
import io
import json
import os
import sys
import time
from datetime import datetime, timedelta

from stock_data import _http_get as http_get

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data", "corp_actions_cache.json")

TTL_SEC = 12 * 3600          # 缓存 12 小时
SECID = "002602"

# 东财数据中心: 分红送配明细(比公告正文接口稳 —— 正文接口 2026-09-21 实测返回空串)
EM_BONUS_API = ("https://datacenter-web.eastmoney.com/api/data/v1/get?"
                "reportName=RPT_SHAREBONUS_DET&columns=ALL&quoteColumns="
                "&pageNumber=1&pageSize=5&sortColumns=NOTICE_DATE&sortTypes=-1"
                "&filter=(SECURITY_CODE%3D%22002602%22)")
EM_REFERER = "https://data.eastmoney.com/"

_WD = "一二三四五六日"


def _read_cache():
    try:
        with io.open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(items):
    try:
        with io.open(CACHE, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "items": items}, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def _fetch():
    """东财分红送配 -> [{record_date, ex_date, per_share, plan, notice_date}]

    per_share = 每股税前派息(元) —— 接口给的是每 10 股(PRETAX_BONUS_RMB),
    送转股(PRETAX_BONUS_RMB 为 None)时记 None,描述退回用 IMPL_PLAN_PROFILE。
    """
    raw = http_get(EM_BONUS_API, referer=EM_REFERER, timeout=15)
    data = json.loads(raw.decode("utf-8", errors="ignore"))
    out = []
    for r in ((data.get("result") or {}).get("data") or []):
        ex = (r.get("EX_DIVIDEND_DATE") or "")[:10]
        rec = (r.get("EQUITY_RECORD_DATE") or "")[:10]
        if not ex and not rec:
            continue
        per10 = r.get("PRETAX_BONUS_RMB")
        out.append({
            "notice_date": (r.get("NOTICE_DATE") or "")[:10],
            "record_date": rec,
            "ex_date": ex,
            "per_share": (per10 / 10.0) if isinstance(per10, (int, float)) else None,
            "plan": r.get("IMPL_PLAN_PROFILE") or "",
        })
    return out


def _records(force=False):
    cache = _read_cache()
    if force or not cache or time.time() - cache.get("ts", 0) >= TTL_SEC:
        try:
            items = _fetch()
        except Exception:
            items = []
        if items:
            _write_cache(items)
            cache = {"ts": time.time(), "items": items}
        elif not cache:
            return []
    return cache.get("items", []) or []


def _fmt_date(d):
    """'2026-09-24' -> '9/24(四)'"""
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        return d
    return f"{dt.month}/{dt.day}({_WD[dt.weekday()]})"


def line(days=7, force=False):
    """窗口内最近的除权除息 -> 一行文案;无则 None

    三种形态:
      今天就是除权除息日 -> 提示参考价已下移,别把自然下移当破位;
      今天就是股权登记日 -> 提示明天除权除息;
      其余(未来 days 天内)  -> 预告日期与幅度。
    """
    today = datetime.now().date()
    best = None
    for r in _records(force=force):
        ex = r.get("ex_date") or r.get("record_date")
        if not ex:
            continue
        try:
            d = datetime.strptime(ex, "%Y-%m-%d").date()
        except Exception:
            continue
        # 登记日已过且除权日已过 -> 事件结束,不再提示
        if d < today and (not r.get("ex_date") or r["ex_date"] < str(today)):
            continue
        if best is None or d < best[0]:
            best = (d, r)
    if best is None:
        return None
    d, r = best
    if (d - today).days > days:
        return None

    plan = (r.get("plan") or "").split("(")[0].strip() or (r.get("plan") or "")
    per = r.get("per_share")
    shift = f"开盘参考价下移约 {per:.2f} 元/股" if per else "开盘参考价将按方案调整"

    rec = r.get("record_date") or ""
    ex = r.get("ex_date") or ""
    try:
        is_ex_today = bool(ex) and datetime.strptime(ex, "%Y-%m-%d").date() == today
        is_rec_today = bool(rec) and datetime.strptime(rec, "%Y-%m-%d").date() == today
    except Exception:
        is_ex_today = is_rec_today = False

    if is_ex_today:
        return f"📅 今日除权除息({plan}): {shift} —— 自然下移,不是破位"
    if is_rec_today:
        tail = f" · 明日 {_fmt_date(ex)} 除权除息" if ex else ""
        return f"📅 今日股权登记日({plan}){tail}"
    txt = f"📅 除权除息预告: {_fmt_date(ex or rec)} {plan} —— {shift}"
    if rec and rec != (ex or ""):
        txt += f" · 登记日 {_fmt_date(rec)}"
    return txt


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    win = int(args[0]) if args else 7
    force = "--force" in sys.argv or "-f" in sys.argv
    recs = _records(force=force)
    print(f"分红送配记录 {len(recs)} 条(缓存 {'刷新' if force else '命中/按需'}):")
    for r in recs:
        print(f"  公告 {r['notice_date']} | 登记 {r['record_date']} | 除权 {r['ex_date']}"
              f" | 每股 {r['per_share']} | {r['plan']}")
    print()
    print("窗口内提示:", line(win, force=False) or "(无)")
