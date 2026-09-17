# -*- coding: utf-8 -*-
"""事件面 —— 妙想资讯检索(东方财富权威信源),带文件缓存与失败降级。

设计原则:
  1. 30 分钟缓存 —— 盘中每小时刷新一次报告,但资讯不必每次重查 API;
  2. 只显示最近 N 天的新条目,老新闻不重复刷屏;
  3. 任何失败(超时/接口变动/无 key)**不得影响报告本身** —— 返回空列表并静默。

用法: python news.py [天数] [条数]
"""
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta

from stock_data import _http_get as http_get   # 带重试/UA 的 GET(与行情同源工具)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data", "news_cache.json")
MX_SEARCH = os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "hermes", "skills", "finance", "mx-search", "mx_search.py")

TTL_SEC = 1800          # 缓存 30 分钟
TIMEOUT = 90            # 单次调用上限

SECID = "002602"        # 世纪华通(深市)
EM_ANN_API = ("https://np-anotice-stock.eastmoney.com/api/security/ann"
              "?sr=-1&page_size=20&page_index=1&ann_type=A&client_source=web&stock_list=")
EM_REFERER = "https://data.eastmoney.com/"


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


_NOISE = ("雪球", "股吧", "荐股", "教育基地", "$世纪华通(SZ")
# 程序性附件:是真是文件,但没有信息量,占用条目位不如留给正文
_LOW_VALUE = ("法律意见书", "保荐", "会计师事务所", "独立财务顾问")
_EVENT_KEYS = ("公告", "持股计划", "股东会", "业绩", "财报", "年报", "中报", "季报",
               "增持", "减持", "回购", "分红", "中标", "签约", "合同", "订单",
               "停牌", "复牌", "重组", "收购", "诉讼", "问询", "监管", "限售", "解禁")


def _clean_title(t):
    """去掉 mx_search 输出里的 "N. " 序号前缀与尾部装饰"""
    return re.sub(r"^\d+\.\s*", "", t.strip()).rstrip("-").strip()


def is_noise(title):
    return any(k in title for k in _NOISE)


def is_low_value(title):
    return any(k in title for k in _LOW_VALUE)


def _fetch_announcements():
    """东财公告接口 -> [{title, date, source}] —— 事件面主源(免费,无 key)

    公司公告是"公司自己说的话",权威性和可交易性都高于媒体解读,所以放在主源。
    2026-09-17 起启用:此前的 mx-search 从未装到本机,news.py 一直在调一个不存在的
    脚本 —— subprocess 返回码 2、stdout 为空,被 parse() 解析成 [] 后照常写缓存,
    于是事件面从未渲染过,且失败完全静默。
    """
    raw = http_get(EM_ANN_API + SECID, referer=EM_REFERER, timeout=15)
    data = json.loads(raw.decode("utf-8", errors="ignore"))
    out = []
    for it in data.get("data", {}).get("list", []):
        title = re.sub(r"^世纪华通[:：]\s*", "", (it.get("title") or "").strip())
        date = (it.get("notice_date") or "")[:10]
        if title and date:
            out.append({"title": title, "date": date, "source": "公告"})
    return out


def is_event(title):
    """公司事件类(公告/股东会/业绩/增减持…)优先于行情转述与媒体解读"""
    return any(k in title for k in _EVENT_KEYS)


def parse(text):
    """解析 mx_search.py 的 stdout -> [{title, date, source}]"""
    items = []
    for part in text.split("\n--- ")[1:]:
        lines = [l.rstrip() for l in part.split("\n") if l.strip()]
        if not lines:
            continue
        title = _clean_title(lines[0])
        m = re.search(r"日期:\s*(\d{4}-\d{2}-\d{2})", part)
        src = re.search(r"（文章来源：(.+?)）", part)
        if title and m:
            items.append({"title": title, "date": m.group(1),
                          "source": src.group(1) if src else None})
    return items


def _fetch(query):
    out = subprocess.run([sys.executable, MX_SEARCH, query],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=TIMEOUT)
    return parse(out.stdout or "")


def recent(days=3, max_items=3, query="世纪华通", force=False):
    """最近 days 天内的公告/资讯(事件类优先,其次日期倒序,最多 max_items 条);失败返回 []"""
    cache = _read_cache()
    if force or not cache or time.time() - cache.get("ts", 0) >= TTL_SEC:
        items = []
        try:
            items.extend(_fetch_announcements())        # 主源: 公司公告
        except Exception:
            pass
        if os.path.exists(MX_SEARCH):                   # 备源: 妙想资讯(装了就一起用)
            try:
                items.extend(_fetch(query))
            except Exception:
                pass
        if items:                                       # 抓不到就保留旧缓存,绝不写空
            cache = {"ts": time.time(), "items": items}
            _write_cache(items)
        elif not cache:                                 # 无缓存且全失败 -> 静默降级
            return []
    items = cache.get("items", [])
    cut = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    fresh, seen = [], set()
    for i in items:
        title = i.get("title") or ""
        if not i.get("date") or i["date"] < cut:
            continue
        if is_noise(title) or is_low_value(title) or title in seen:
            continue
        seen.add(title)
        fresh.append(i)
    # 公司事件优先,其次按日期倒序
    fresh.sort(key=lambda x: (is_event(x["title"]), x["date"]), reverse=True)
    return fresh[:max_items]


def line(days=3, max_items=3):
    """格式化成报告用的一行(无新内容则返回 None)"""
    items = recent(days, max_items)
    if not items:
        return None
    txt = " · ".join(f"{i['title'][:34]}({i['date'][5:]})" for i in items)
    return f"近{days}日: {txt}"


if __name__ == "__main__":
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    got = recent(d, n, force=True)
    print(f"最近 {d} 天共 {len(got)} 条:")
    for i in got:
        print(f"  [{i['date']}] {i['title'][:70]}  ({i.get('source') or '—'})")
    if not got:
        print("  (无)")
