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

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "data", "news_cache.json")
MX_SEARCH = os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "hermes", "skills", "finance", "mx-search", "mx_search.py")

TTL_SEC = 1800          # 缓存 30 分钟
TIMEOUT = 90            # 单次调用上限


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
_EVENT_KEYS = ("公告", "持股计划", "股东会", "业绩", "财报", "年报", "中报", "季报",
               "增持", "减持", "回购", "分红", "中标", "签约", "合同", "订单",
               "停牌", "复牌", "重组", "收购", "诉讼", "问询", "监管", "限售", "解禁")


def _clean_title(t):
    """去掉 mx_search 输出里的 "N. " 序号前缀与尾部装饰"""
    return re.sub(r"^\d+\.\s*", "", t.strip()).rstrip("-").strip()


def is_noise(title):
    return any(k in title for k in _NOISE)


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
    """最近 days 天内的资讯(按日期倒序,最多 max_items 条);失败返回 []"""
    cache = _read_cache()
    if force or not cache or time.time() - cache.get("ts", 0) >= TTL_SEC:
        try:
            cache = {"ts": time.time(), "items": _fetch(query)}
            _write_cache(cache["items"])
        except Exception:
            if not cache:                       # 无缓存且抓取失败 -> 静默降级
                return []
    items = cache.get("items", [])
    cut = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    fresh = [i for i in items
             if i.get("date") and i["date"] >= cut and not is_noise(i["title"])]
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
