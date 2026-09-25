# -*- coding: utf-8 -*-
"""AI 早报取材：确定性抓取 + 去重账本（cron 898a874152ca 的 pre-run 脚本）

分工：脚本负责"抓到什么、什么时间、报没报过"，agent 只负责筛选、改写、判断重要性。
信息源覆盖面由代码保证（每天同一批源），不靠模型临场想起来去搜。

输出给 agent 的上下文分四段：
  1. 账本段：LAST_PUSH / 时间窗 / 已报 key（去重真值）
  2. CANDIDATES 段：窗口内的原始候选，带来源、日期、链接（agent 的事实基础）
  3. COVERAGE 段：每个源抓到几条、哪些源失败（agent 必须自己补搜失败的源）
  4. 已报 key 清单

账本：记录\\ai_news_seen.json  {items:[{key,title,first_seen,last_seen}], updated_at}
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

CST = timezone(timedelta(hours=8))
JOB_ID = "898a874152ca"
LEDGER = r"D:\Hermes\记录\ai_news_seen.json"
MAX_ITEMS = 400
SCAN_FILES = 30          # 回看最近 N 份历史输出
RECENT_TITLE_COUNT = 20  # 打印给 agent 的近期标题条数
WIN_MAX_H = 30           # 每天一次，窗口要能覆盖前一天晚上
WIN_DEFAULT_H = 24       # 无历史时的默认窗口
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
KEY_RE = re.compile(r"#ai-([a-z0-9][a-z0-9._-]{1,60})")
TAG_RE = re.compile(r"<[^>]+>")
AI_KW = re.compile(
    r"\b(ai|a\.i\.|llm|gpt|claude|gemini|grok|qwen|deepseek|agent|agentic|agents|ml|"
    r"neural|transformer|diffusion|rag|embed|embedding|inference|infer|finetune|"
    r"fine-?tun|copilot|open-?source|chatbot|multimodal|reasoning|token|context window|"
    r"prompt|eval|benchmark|dataset|model|models|training|weights|inference|sora|"
    r"midjourney|perplexity|hugging\s?face|artificial intelligence)\b|"
    r"人工智能|大模型|智能体|深度学习|神经网络|算力|多模态|大语言模型", re.I)


def _slot_label(dt):
    """只有 08:30 一个槽位；其余小时触发的是手动补跑或错过补跑。"""
    return "早报" if 4 <= dt.hour < 12 else "补报"


def _out_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "hermes", "cron", "output", JOB_ID)


# ---------------------------------------------------------------- 抓取层

def _fetch(url, *, timeout=25, as_json=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "*/*", "Accept-Language": "en,zh-CN;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    text = raw.decode("utf-8", "replace")
    return json.loads(text) if as_json else text


def _rss_items(xml, limit=30):
    """极简 RSS/Atom 取 title/link/date，不引第三方依赖。"""
    out = []
    blocks = re.findall(r"<item[ >].*?</item>|<entry[ >].*?</entry>", xml, re.S)
    for block in blocks[:limit * 2]:
        t = re.search(r"<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block, re.S)
        m = re.search(r"<link[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", block, re.S)
        if not m:
            m = re.search(r'<link[^>]*href="([^"]+)"', block)
        d = re.search(r"<pubDate>(.*?)</pubDate>", block, re.S) or \
            re.search(r"<updated>(.*?)</updated>", block, re.S) or \
            re.search(r"<published>(.*?)</published>", block, re.S)
        if not (t and m):
            continue
        out.append({"title": TAG_RE.sub("", t.group(1)).strip()[:180],
                    "link": (m.group(1) if m.lastindex else m.group(0)).strip(),
                    "date": d.group(1).strip() if d else ""})
        if len(out) >= limit:
            break
    return out


def _parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    for fn in (lambda: parsedate_to_datetime(s),
               lambda: datetime.fromisoformat(s.replace("Z", "+00:00"))):
        try:
            dt = fn()
            return dt.replace(tzinfo=CST) if dt.tzinfo is None else dt.astimezone(CST)
        except Exception:
            continue
    return None


def src_hf_papers(win_from, now):
    """HF Daily Papers：无参数调用 = 当前日榜。日期字段用 paper.submittedOnDailyAt
    （顶层 publishedAt 是论文首次提交日，不是上榜日；用它会把当天全榜误判成旧闻）。"""
    data = _fetch("https://huggingface.co/api/daily_papers", as_json=True, timeout=30)
    out = []
    for row in data:
        pap = row.get("paper") or {}
        dt = _parse_date(pap.get("submittedOnDailyAt") or row.get("publishedAt"))
        if dt and dt > now + timedelta(hours=12):
            continue
        up = pap.get("upvotes", 0) or 0
        stars = pap.get("githubStars", 0) or 0
        out.append({
            "src": "HF论文", "date": dt.strftime("%m-%d %H:%M") if dt else "当天",
            "title": pap.get("title", "")[:150],
            "why": "HF日榜 %d 赞" % up + (" · %d★" % stars if stars else ""),
            "link": "https://huggingface.co/papers/%s" % pap.get("id", ""),
        })
    out.sort(key=lambda x: -int(re.search(r"(\d+)", x["why"]).group(1)))
    return out[:12]


def src_github_new(win_from, now):
    """GitHub 新星：官方 search API（HTML trending 页已改版，正则抓不稳）。
    近几天新建 + 高星 + AI 主题的仓库。"""
    since = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    out, seen = [], set()
    queries = [
        "created:>%s stars:>=20 topic:ai" % since,
        "created:>%s stars:>=20 topic:llm" % since,
        "created:>%s stars:>=20 topic:agent" % since,
        "created:>%s stars:>=20 topic:machine-learning" % since,
    ]
    for q in queries:
        url = ("https://api.github.com/search/repositories?q=%s&sort=stars&order=desc&per_page=8"
               % q.replace(" ", "+").replace(">", "%3E"))
        try:
            data = _fetch(url, as_json=True, timeout=25)
        except Exception:
            continue
        for it in (data.get("items") or []):
            full = it.get("full_name", "")
            if not full or full in seen:
                continue
            seen.add(full)
            out.append({
                "src": "GitHub新星", "date": "近3日新仓",
                "title": "%s（★%s）" % (full, it.get("stargazers_count", 0)),
                "why": (it.get("description") or "AI 相关新仓库")[:110],
                "link": it.get("html_url") or ("https://github.com/" + full),
            })
    out.sort(key=lambda x: -int(re.search(r"★(\d+)", x["title"]).group(1)))
    return out[:10]


def src_hn(win_from, now):
    """Hacker News：frontpage 全量按关键词筛（newest?points= 常空）。"""
    xml = _fetch("https://hnrss.org/frontpage", timeout=25)
    out = []
    for it in _rss_items(xml, limit=40):
        dt = _parse_date(it["date"])
        if dt and (dt < win_from or dt > now + timedelta(hours=6)):
            continue
        if not AI_KW.search(it["title"]):
            continue
        out.append({"src": "HackerNews", "date": dt.strftime("%m-%d %H:%M") if dt else "无时间戳",
                    "title": it["title"], "why": "", "link": it["link"]})
    return out[:10]


def src_rss(name, url, win_from, now, limit=12):
    """通用 RSS 源：按时间窗筛 + AI 关键词过滤。"""
    xml = _fetch(url, timeout=25)
    out = []
    for it in _rss_items(xml, limit=limit * 4):
        dt = _parse_date(it["date"])
        if dt and (dt < win_from or dt > now + timedelta(hours=12)):
            continue
        if not AI_KW.search(it["title"]):
            continue
        out.append({
            "src": name, "date": dt.strftime("%m-%d %H:%M") if dt else "\u65e0\u65f6\u95f4\u6233",
            "title": it["title"], "why": "", "link": it["link"],
        })
        if len(out) >= limit:
            break
    return out


def src_qbitai(win_from, now):
    """量子位：中文源，标题常不含 AI 词，只按时间窗筛。"""
    xml = _fetch("https://www.qbitai.com/feed", timeout=25)
    out = []
    for it in _rss_items(xml, limit=24):
        dt = _parse_date(it["date"])
        if dt and (dt < win_from or dt > now + timedelta(hours=12)):
            continue
        out.append({"src": "量子位", "date": dt.strftime("%m-%d %H:%M") if dt else "无时间戳",
                    "title": it["title"], "why": "", "link": it["link"]})
    return out[:10]


# 源清单：前 2 个是主力（必到），其余失败只记 COVERAGE 并要求 agent 补搜
SOURCES = [
    ("HF论文", src_hf_papers, True),
    ("GitHub新星", src_github_new, True),
    ("OpenAI官方", lambda w, n: src_rss("OpenAI官方", "https://openai.com/news/rss.xml", w, n, 8), False),
    ("GoogleAI博客", lambda w, n: src_rss("GoogleAI博客", "https://blog.google/technology/ai/rss/", w, n, 8), False),
    ("DeepMind博客", lambda w, n: src_rss("DeepMind博客", "https://deepmind.google/blog/rss.xml", w, n, 6), False),
    ("HuggingFace博客", lambda w, n: src_rss("HuggingFace博客", "https://huggingface.co/blog/feed.xml", w, n, 6), False),
    ("BAIR博客", lambda w, n: src_rss("BAIR博客", "https://bair.berkeley.edu/blog/feed.xml", w, n, 5), False),
    ("量子位", src_qbitai, False),
    ("TechCrunchAI", lambda w, n: src_rss("TechCrunchAI",
        "https://techcrunch.com/category/artificial-intelligence/feed/", w, n, 10), False),
    ("HackerNews", src_hn, False),
    ("RedditLLM", lambda w, n: src_rss("RedditLLM",
        "https://www.reddit.com/r/LocalLLaMA/new/.rss?limit=30", w, n, 10), False),
]


# ---------------------------------------------------------------- 账本层

def _read_ledger():
    try:
        with open(LEDGER, "r", encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict) and isinstance(d.get("items"), list):
            return d
    except Exception:
        pass
    return {"items": []}


def _write_ledger(items):
    payload = {"updated_at": datetime.now(CST).isoformat(timespec="seconds"),
               "items": items[:MAX_ITEMS]}
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LEDGER)


def _response_of(path):
    """只取输出文件的 ## Response 段，避免把 prompt 里的示例 key 算进去。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        return ""
    idx = text.rfind("## Response")
    return text[idx:] if idx >= 0 else ""


def _scan_history():
    """从历史输出回收 #ai-<key> 标记，返回 [(key, title, mtime)]，按 mtime 新→旧。"""
    files = glob.glob(os.path.join(_out_dir(), "*.md"))
    files.sort(key=os.path.getmtime, reverse=True)
    hits = []
    for p in files[:SCAN_FILES]:
        for line in _response_of(p).splitlines():
            m = KEY_RE.search(line)
            if not m:
                continue
            title = line.strip().lstrip("#*0123456789.、 ").split("\u2014\u2014")[0].strip()
            hits.append((m.group(1).rstrip(".,;\uff0c"), title[:60],
                         datetime.fromtimestamp(os.path.getmtime(p), CST)))
    return hits


# ---------------------------------------------------------------- 主流程

def main():
    now = datetime.now(CST)
    ledger = _read_ledger()
    known = {it["key"]: it for it in ledger["items"]
             if isinstance(it, dict) and it.get("key")}

    # 时间窗：以最近一份真实产出（历史输出文件）为界；跑失败没产出 → 窗口自然变长
    files = glob.glob(os.path.join(_out_dir(), "*.md"))
    last_push = (datetime.fromtimestamp(max(os.path.getmtime(p) for p in files), CST)
                 if files else None)
    if last_push is None:
        win_h, win_from = float(WIN_DEFAULT_H), now - timedelta(hours=WIN_DEFAULT_H)
    else:
        win_h = min(WIN_MAX_H, max(1.0, (now - last_push).total_seconds() / 3600))
        win_from = last_push

    # 回收历史 key → 账本
    today = now.date().isoformat()
    today_keys = set()
    stamp = now.isoformat(timespec="seconds")
    for key, title, mtime in _scan_history():
        prev = known.get(key)
        if prev:
            prev["last_seen"] = stamp
            if title and not prev.get("title"):
                prev["title"] = title
        else:
            known[key] = {"key": key, "title": title, "first_seen": stamp, "last_seen": stamp}
        if mtime.date().isoformat() == today:
            today_keys.add(key)
    try:
        _write_ledger(sorted(known.values(), key=lambda x: x.get("last_seen", ""), reverse=True))
    except Exception:
        pass  # 账本写失败不阻塞推送

    # 抓取：单源失败只记进 COVERAGE，不影响其他源
    pool, coverage = [], []
    for name, fn, critical in SOURCES:
        try:
            got = list(fn(win_from, now) or [])
            pool.extend(got)
            coverage.append((name, len(got), "ok"))
        except Exception as e:
            coverage.append((name, 0, "FAILED: %s" % type(e).__name__))
            if critical:
                print("[warn] \u4e3b\u529b\u6e90 %s \u6293\u53d6\u5931\u8d25: %s" % (name, e), file=sys.stderr)
    # 同一链接去重（主力源优先，按 SOURCES 顺序）
    seen_links, uniq = set(), []
    for it in pool:
        k = it["link"].split("?")[0]
        if k in seen_links:
            continue
        seen_links.add(k)
        uniq.append(it)

    keys_sorted = sorted(known, key=lambda k: known[k].get("last_seen", ""), reverse=True)
    recent = [known[k].get("title") or k for k in keys_sorted[:RECENT_TITLE_COUNT]]

    print("=== AI \u65e9\u62a5\u53d6\u6750\u4e0a\u4e0b\u6587\uff08\u811a\u672c\u751f\u6210\uff0c\u4ee5\u4e0b\u4e3a\u4e8b\u5b9e\u57fa\u7840\uff09===")
    print("NOW(CST): " + now.strftime("%Y-%m-%d %H:%M"))
    print("ISSUE: %s %s\uff08\u5b9a\u65f6\u69fd\u4f4d \u6bcf\u5929 08:30 \u65e9\u62a5\uff09"
          % (now.strftime("%Y-%m-%d"), _slot_label(now)))
    print("LAST_PUSH(CST): " + win_from.strftime("%Y-%m-%d %H:%M"))
    print("WINDOW: \u53ea\u62a5 %s \u4e4b\u540e\u81f3\u4eca\uff08\u7ea6 %.1f \u5c0f\u65f6\uff09\u7684\u65b0\u4e8b\u4ef6\uff1b"
          "\u66f4\u65e9\u7684\u4e00\u5f8b\u4e0d\u7b97\u672c\u671f\u65b0\u95fb\uff0c\u4e5f\u4e0d\u8bb8\u7528"
          "\u201c\u56de\u987e/\u80cc\u666f/\u4e0a\u671f\u63d0\u5230\u201d\u7684\u65b9\u5f0f\u91cd\u63d0"
          % (win_from.strftime("%m-%d %H:%M"), win_h))
    print("ALREADY_REPORTED_COUNT: %d  (TODAY_COUNT: %d)" % (len(keys_sorted), len(today_keys)))
    print("")
    print("--- CANDIDATES\uff08\u7a0b\u5e8f\u5df2\u6293\u5230\u7684\u7a97\u53e3\u5185\u5019\u9009\uff0c\u4ee5\u6b64\u4e3a\u4e8b\u5b9e\u57fa\u7840\uff09---")
    by_src = {}
    for it in uniq:
        by_src.setdefault(it["src"], []).append(it)
    for name, _fn, _c in SOURCES:
        got = by_src.get(name)
        if not got:
            continue
        print("[%s] %d \u6761" % (name, len(got)))
        for it in got:
            why = "  // %s" % it["why"] if it["why"] else ""
            print("  - (%s) %s%s || %s" % (it["date"], it["title"], why, it["link"]))
    print("")
    print("--- COVERAGE\uff08\u8986\u76d6\u5ea6\u81ea\u68c0\uff09---")
    for name, n, st in coverage:
        print("  %s: %d \u6761 [%s]" % (name, n, st))
    failed = [n for n, _, s in coverage if s != "ok"]
    if failed:
        print("  !! \u6293\u53d6\u5931\u8d25\u7684\u6e90\uff1a%s \u2014\u2014 \u4f60\u5fc5\u987b\u7528 web_search / "
              "web_extract \u4eb2\u81ea\u8865\u641c\u8fd9\u4e9b\u6e90\u7684\u5bf9\u5e94\u5185\u5bb9\uff0c"
              "\u4e0d\u8981\u56e0\u4e3a\u811a\u672c\u6ca1\u6293\u5230\u5c31\u5f53\u6ca1\u6709\u65b0\u95fb\u3002" % ", ".join(failed))
    print("")
    print("RULE1: \u4e0b\u5217 key \u4e00\u5f8b\u4e0d\u5f97\u91cd\u590d\u4e0a\u62a5\uff0c\u9664\u975e\u51fa\u73b0\u5b9e\u8d28\u53d8\u5316"
          "\uff08\u6b63\u5f0f\u53d1\u5e03\u3001\u6743\u91cd/\u4ee3\u7801\u5f00\u6e90\u3001\u4ef7\u683c\u6216\u6570\u636e\u66f4\u65b0\uff09\uff0c"
          "\u6b64\u65f6\u6807\u9898\u524d\u52a0\u3010\u8fdb\u5c55\u66f4\u65b0\u3011\u5e76\u5199\u6e05\u53d8\u4e86\u4ec0\u4e48\u3002")
    print("KEYS: " + (", ".join(keys_sorted) if keys_sorted else "(\u7a7a)"))
    print("RECENT_TITLES: " + (" / ".join(recent) if recent else "(\u7a7a)"))


if __name__ == "__main__":
    main()
