# -*- coding: utf-8 -*-
"""基本面/估值数据层 —— 数据源:东方财富妙想 mx-data(离线缓存 + 本地计算)

设计:
  财务数据(营收/净利/ROE/EPS/股本)变化极慢(一个季度一次),缓存到
  data/fundamentals.json;估值(市值/PE/PB/前瞻PE)用【现价 × 缓存财务】
  本地算,因此每次报告零 API 调用 —— 这是把"数据获取"与"每小时刷新"解耦。

刷新缓存:改 data/fundamentals.json(或重跑妙想 mx_data.py 后人工更新),
          三季报(约 10 月底)、年报(约 4 月)后必须更新。
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data", "fundamentals.json")


def load():
    with io.open(CACHE, encoding="utf-8") as f:
        return json.load(f)


def snapshot(price, period="2026H1"):
    """用现价 + 缓存财务算估值 -> (经营行, 估值行)

    例:('2026H1 营收221.2亿(+28.5%) · 净利45.0亿(+69.5%) · ROE13.87%',
         '市值1110亿 | PE(TTM)14.9x | PB3.24x | 26E净利89.8亿(+59.9%)→前瞻PE12.4x')
    """
    d = load()
    sh = d["shares_yi"]
    mcap = price * sh                                    # 亿元
    pe = price / d["eps_ttm"] if d.get("eps_ttm") else None
    pb = price / d["bps"] if d.get("bps") else None

    p = d["periods"].get(period) or {}
    biz = (f"{period} 营收{p.get('rev_yi', 0):.1f}亿({p.get('rev_yoy', 0):+.1f}%)"
           f" · 净利{p.get('ni_yi', 0):.1f}亿({p.get('ni_yoy', 0):+.1f}%)"
           f" · ROE{p.get('roe', 0):.2f}% · 毛利{p.get('gross', 0):.1f}%")

    f26 = (d.get("forecast") or {}).get("2026E") or {}
    val = f"市值{mcap:.0f}亿"
    if pe:
        val += f" | PE(TTM){pe:.1f}x"
    if pb:
        val += f" | PB{pb:.2f}x"
    if f26.get("ni_yi"):
        fpe = mcap / f26["ni_yi"]
        val += f" | 26E净利{f26['ni_yi']:.1f}亿({f26.get('yoy', 0):+.1f}%)→前瞻PE{fpe:.1f}x"
    return biz, val


def yoy_note(price, period="2026H1"):
    """一句话增速评价(基于缓存数据的机械判断,不做预测)"""
    d = load()
    p = d["periods"].get(period) or {}
    ni_yoy = p.get("ni_yoy", 0)
    pe = price / d["eps_ttm"] if d.get("eps_ttm") else None
    f26 = (d.get("forecast") or {}).get("2026E") or {}
    fpe = (price * d["shares_yi"] / f26["ni_yi"]) if f26.get("ni_yi") else None
    if ni_yoy > 50 and fpe and fpe < 20:
        return f"高增长低估值区间(净利{ni_yoy:+.0f}%、前瞻PE{fpe:.1f}x)"
    if ni_yoy > 0 and fpe and fpe < 25:
        return f"增长与估值大体匹配(净利{ni_yoy:+.0f}%、前瞻PE{fpe:.1f}x)"
    return f"增速{ni_yoy:+.0f}%、前瞻PE {fpe:.1f}x" if fpe else f"增速{ni_yoy:+.0f}%"


if __name__ == "__main__":
    import sys
    px = float(sys.argv[1]) if len(sys.argv) > 1 else 15.06
    b, v = snapshot(px)
    print("经营:", b)
    print("估值:", v)
    print("点评:", yoy_note(px))
