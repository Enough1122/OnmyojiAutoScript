# -*- coding: utf-8 -*-
"""世纪华通(002602) 行情数据拉取模块
数据源: 腾讯实时行情 + 东方财富日K线(均免费,无需 key)
"""
import json
import time
import urllib.error
import urllib.request

SECID = "0.002602"          # 东财 secid: 0=深市
TENCENT_SYMBOL = "sz002602"  # 腾讯代码
NAME = "世纪华通"


def _http_get(url, referer=None, timeout=10, retries=3, backoff=1.5):
    """带重试的 HTTP GET。

    腾讯/新浪这类免费接口在收盘后(数据拉取高峰)会偶发返回 501/503 风控响应,
    单次失败不该让整个 cron 任务挂掉 —— 退避重试几次通常就过了。
    4xx 是请求本身的问题,重试无意义,直接抛。"""
    last_exc = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": referer or "https://gu.qq.com/",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code < 500:
                raise
        except Exception as e:      # 超时 / 连接被拒 / RemoteDisconnected
            last_exc = e
        if attempt < retries - 1:
            time.sleep(backoff * (attempt + 1))
    raise last_exc


def get_realtime():
    """腾讯实时行情 -> dict"""
    raw = _http_get(f"https://qt.gtimg.cn/q={TENCENT_SYMBOL}")
    text = raw.decode("gbk", errors="ignore")
    payload = text.split('="', 1)[1].rstrip('";\n')
    f = payload.split("~")
    return {
        "name": f[1],
        "code": f[2],
        "price": float(f[3]),
        "prev_close": float(f[4]),
        "open": float(f[5]),
        "volume_hand": int(float(f[6])),
        "time": f[30],
        "change": float(f[31]),
        "change_pct": float(f[32]),
        "high": float(f[33]),
        "low": float(f[34]),
    }


def get_daily_kline(days=120):
    """腾讯日K线(前复权) -> [ {date,open,close,high,low,volume}, ... ] 升序
    用 ifzq.gtimg.cn(与实时行情同源,更稳定)
    注意: web.ifzq.gtimg.cn 已被腾讯WAF拦截(HTTP 501 跳 waf.tencent.com),
    必须用不带 web. 前缀的 ifzq.gtimg.cn(2026-09-16 实测)。"""
    url = (f"https://ifzq.gtimg.cn/appstock/app/fqkline/get?param={TENCENT_SYMBOL},day,,,{days},qfq")
    data = json.loads(_http_get(url, referer="https://gu.qq.com/"))
    stock = data["data"][TENCENT_SYMBOL]
    key = "qfqday" if "qfqday" in stock else "day"
    klines = []
    for p in stock[key]:
        klines.append({
            "date": p[0],
            "open": float(p[1]),
            "close": float(p[2]),
            "high": float(p[3]),
            "low": float(p[4]),
            "volume": float(p[5]),
        })
    return klines


SINA_SYMBOL = "sz002602"    # 新浪代码(与腾讯同格式)


def get_realtime_sina():
    """新浪实时行情 —— 第二数据源,仅用于交叉校验。
    注意: 新浪要求 Referer,否则 403。
    字段: 0名称 1今开 2昨收 3现价 4最高 5最低 ... 30日期 31时间"""
    raw = _http_get(f"https://hq.sinajs.cn/list={SINA_SYMBOL}",
                    referer="https://finance.sina.com.cn/")
    text = raw.decode("gbk", errors="ignore")
    payload = text.split('="', 1)[1].rstrip('";\n')
    f = payload.split(",")
    return {
        "name": f[0],
        "open": float(f[1]),
        "prev_close": float(f[2]),
        "price": float(f[3]),
        "high": float(f[4]),
        "low": float(f[5]),
    }


def cross_check(tx=None, tolerance_pct=1.0):
    """腾讯 vs 新浪 双源交叉校验 -> (ok, lines)

    思路借用 ai-berkshire tools/financial_rigor.py 的 cross_validate:
    单一数据源出错(接口改格式/返回陈旧值/字段错位)时报告会静默出错,
    双源比对是唯一能在事后发现的手段。ok=False 表示分歧超容差。
    单源失败不阻断报告,降级为单源并标注可信度。"""
    try:
        tx = tx or get_realtime()
    except Exception as e:
        return False, [f"❌ 主源(腾讯)失败: {e}"]
    try:
        sn = get_realtime_sina()
    except Exception as e:
        return False, [f"⚠️ 第二源(新浪)不可用: {e} — 本次为腾讯单源,可信度降低"]
    lines, ok = [], True
    for field, label in (("price", "现价"), ("prev_close", "昨收"),
                         ("open", "今开"), ("high", "最高"), ("low", "最低")):
        a, b = tx[field], sn[field]
        dev = abs(a - b) / b * 100 if b else 0.0
        if dev > tolerance_pct:
            ok = False
            lines.append(f"  ❌ {label}两源分歧: 腾讯 {a} vs 新浪 {b} (偏差 {dev:.2f}%)")
    if ok:
        lines.append(f"  ✅ 腾讯/新浪双源一致(5项均 ≤{tolerance_pct}% 容差)")
    return ok, lines


if __name__ == "__main__":
    import datetime
    rt = get_realtime()
    print("实时:", rt)
    ks = get_daily_kline(30)
    print("最近5根K线:")
    for k in ks[-5:]:
        print(" ", k)
