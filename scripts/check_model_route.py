#!/usr/bin/env python3
"""分辨 opencode-go 的 DeepSeek 请求实际落在哪条路由上（v4.1-flash vs v4-flash）。

用法:
  python check_model_route.py                 # 探测 3 个型号各 2 次 + Hermes 侧记录
  python check_model_route.py --runs 3
  python check_model_route.py --models deepseek-v4.1-flash,deepseek-v4-flash

判别依据（实测稳定）:
  * 响应 id 命名空间:  'router-xxxx' = v4-flash 那条路由；纯 uuid = v4.1 家族后端
  * usage 额外字段:    prompt_cache_hit_tokens / prompt_cache_miss_tokens
                       + completion_tokens_details.reasoning_tokens = v4.1 家族后端
  注意: 响应里的 "model" 字段只是把请求里的 id 原样回显，不能当证据（别名
        deepseek-flash 也是原样回显）。真正的证据是上面两条指纹。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_MODELS = ["deepseek-v4.1-flash", "deepseek-v4-flash", "deepseek-flash"]


def hermes_home() -> str:
    env = os.environ.get("HERMES_HOME")
    if env:
        return env
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes")


def read_env_key(path: str, key: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def read_cfg(path: str) -> dict:
    """Tiny regex reader - we only need model.provider/default/base_url."""
    out = {"provider": "", "default": "", "base_url": ""}
    if not os.path.exists(path):
        return out
    txt = open(path, "r", encoding="utf-8", errors="replace").read()
    m = re.search(r"^model:\s*$(.*?)(?=^\S)", txt, re.M | re.S)
    block = m.group(1) if m else ""
    for key in ("provider", "default", "base_url"):
        mm = re.search(r"^\s+%s:\s*(.+?)\s*$" % key, block, re.M)
        if mm:
            val = mm.group(1).strip().strip('"').strip("'")
            out[key] = val
    return out


def probe(base_url: str, key: str, model: str, timeout: int = 90) -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": "say ok"}],
            "max_tokens": 24,
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "x-opencode-session": "route-probe-%d" % int(time.time() * 1000 % 10**9),
            "User-Agent": "hermes-route-probe/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")[:300]
        return {"ok": False, "err": "HTTP %s %s" % (exc.code, raw)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, exc)}
    if "error" in body:
        return {"ok": False, "err": json.dumps(body["error"], ensure_ascii=False)[:300]}
    rid = str(body.get("id") or "")
    usage = body.get("usage") or {}
    extras = {k: v for k, v in usage.items()
              if k not in ("prompt_tokens", "completion_tokens", "total_tokens")}
    native_cache = "prompt_cache_hit_tokens" in usage or "prompt_cache_miss_tokens" in usage
    reasoning = bool((usage.get("completion_tokens_details") or {}).get("reasoning_tokens"))
    return {
        "ok": True,
        "id": rid,
        "id_ns": "router-" if rid.startswith("router-") else "uuid",
        "model_echo": body.get("model"),
        "cfgid": body.get("model"),
        "native_cache": native_cache,
        "reasoning": reasoning,
        "extras": extras,
    }


def verdict(row: dict) -> str:
    if not row.get("ok"):
        return "探测失败"
    if row["id_ns"] == "router-" and not row["native_cache"]:
        return "v4-flash 路由 (router- 命名空间 / 无 cache 字段)"
    if row["id_ns"] == "uuid" and row["native_cache"]:
        return "v4.1 家族后端 (uuid / DeepSeek 原生 cache 字段)"
    return "指纹混合，未匹配已知路由，请人工看原始字段"


def hermes_side(home: str, limit: int = 12) -> None:
    db = os.path.join(home, "state.db")
    print("\n[Hermes 侧记录] 最近 %d 条 session_model_usage（记录的是 Hermes 发出的型号）" % limit)
    if not os.path.exists(db):
        print("  未找到 state.db")
    else:
        try:
            con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
            rows = list(con.execute(
                "select session_id, model, task, api_call_count, last_seen "
                "from session_model_usage order by last_seen desc limit ?", (limit,)))
            for sid, model, task, calls, last in rows:
                ts = time.strftime("%m-%d %H:%M", time.localtime(last or 0))
                print("  %s  %-26s %-16s calls=%-4s %s" % (ts, model, task or "-", calls, sid[:24]))
            con.close()
        except Exception as exc:  # noqa: BLE001
            print("  读取失败:", exc)

    log = os.path.join(home, "logs", "agent.log")
    print("\n[回退检查] agent.log 里的模型回退事件")
    if not os.path.exists(log):
        print("  未找到 agent.log")
        return
    hits = []
    with open(log, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            low = line.lower()
            if ("fallback" in low and "model" in low) or "switching to" in low or "fell back" in low:
                hits.append(line.rstrip())
    if not hits:
        print("  无（没有发生模型回退）")
    else:
        for h in hits[-5:]:
            print("  " + h[:200])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--home", default=hermes_home())
    args = ap.parse_args()

    home = args.home
    cfg = read_cfg(os.path.join(home, "config.yaml"))
    key = read_env_key(os.path.join(home, ".env"), "OPENCODE_ZEN_API_KEY")
    base_url = cfg["base_url"] or "https://opencode.ai/zen/go/v1"

    print("[配置] Hermes 请求型号: %s  provider=%s" % (cfg["default"] or "?", cfg["provider"] or "?"))
    print("[配置] base_url: %s" % base_url)
    if not key:
        print("! 未在 %s/.env 找到 OPENCODE_ZEN_API_KEY" % home)
        return 1

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    print("\n[指纹探测] 每个型号发 %d 次请求（--runs 可调）" % args.runs)
    for model in models:
        rows = [probe(base_url, key, model) for _ in range(args.runs)]
        print("\n  ── %s" % model)
        for r in rows:
            if not r["ok"]:
                print("     ✗ %s" % r["err"])
                continue
            print("     id=%-8s native_cache=%-5s reasoning=%-5s usage_extra=%s"
                  % (r["id_ns"], r["native_cache"], r["reasoning"],
                     json.dumps(r["extras"], ensure_ascii=False)[:110]))
        good = [r for r in rows if r["ok"]]
        if good:
            print("     → %s" % verdict(good[0]))

    if cfg["default"]:
        print("\n[结论] Hermes 现在请求的是 %s：看上面同一行的指纹是否落在 v4.1 家族（uuid + cache 字段）。"
              % cfg["default"])

    hermes_side(home)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
