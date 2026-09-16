#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本机 Claude Code 真实用量统计（v3：按 message.id 去重）

背景：Claude Code 会把同一条模型回复按内容块拆成多行重复记账（usage 在多行里重复出现），
      直接按行累加会虚高（实测约 2.8 倍）。v3 按 message.id 去重，取该条回复的最终 usage，
      输出真实请求数与 token 用量。

用法：
    python token_usage.py                 # 全部历史
    python token_usage.py 2026-09-04      # 指定起始日期

数据源：~/.claude/projects 下所有 .jsonl（含子代理 subagents 目录）
口径：
    请求数 = 去重后的 message.id 数（≈ 实际发给模型的 API 请求数）
    输出 = 模型生成的 token（含思考）
    未缓存输入 = 每次请求新读入的部分
    缓存读取 = 命中提示缓存的重复前缀（按 0.1× 计费）
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone, timedelta

BJ = timezone(timedelta(hours=8))


def main():
    since = sys.argv[1] if len(sys.argv) > 1 else None
    files = []
    for dp, dn, fn in os.walk(os.path.expanduser("~/.claude/projects")):
        for f in fn:
            if f.endswith(".jsonl"):
                files.append(os.path.join(dp, f))

    best = {}          # mid -> [grp, i, o, cr]
    turns = tool_results = 0
    oldest = newest = None
    for p in files:
        grp = "sub" if (os.sep + "subagents" + os.sep) in p else "main"
        for line in open(p, encoding="utf-8", errors="replace"):
            if ('"usage":' not in line and '"type":"user"' not in line
                    and '"type": "user"' not in line):
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = d.get("timestamp")
            if ts:
                if oldest is None or ts < oldest:
                    oldest = ts
                if newest is None or ts > newest:
                    newest = ts
                if since and ts[:10] < since:
                    continue
            t = d.get("type")
            m = d.get("message") if isinstance(d.get("message"), dict) else {}
            if t == "user":
                c = m.get("content")
                if isinstance(c, list) and any(
                        isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
                    tool_results += 1
                else:
                    turns += 1
            elif t == "assistant":
                u = m.get("usage")
                if isinstance(u, dict):
                    mid = m.get("id") or d.get("uuid")
                    if not mid:
                        continue
                    i = u.get("input_tokens") or 0
                    o = u.get("output_tokens") or 0
                    cr = u.get("cache_read_input_tokens") or 0
                    cur = best.get(mid)
                    if cur is None or o > cur[2]:
                        best[mid] = [grp, i, o, cr]

    calls = len(best)
    tin = sum(v[1] for v in best.values())
    tout = sum(v[2] for v in best.values())
    tcr = sum(v[3] for v in best.values())
    total = tin + tout + tcr
    c_main = sum(1 for v in best.values() if v[0] == "main")
    c_sub = calls - c_main

    print(f"统计范围: {since or (oldest or '')[:10]} ~ {(newest or '')[:10]}   ({len(files)} 个日志文件)")
    print(f"用户轮次:     {turns:,}")
    print(f"工具结果消息: {tool_results:,}")
    print("-" * 46)
    print(f"请求数(去重): {calls:,}   (主会话 {c_main:,} + 子代理 {c_sub:,})")
    print(f"输出 token:   {tout:,}   ({tout/1e4:.0f} 万)")
    print(f"未缓存输入:   {tin:,}   ({tin/1e6:.1f}M)")
    print(f"缓存读取:     {tcr:,}   ({tcr/1e9:.2f}B)")
    print("-" * 46)
    print(f"合计 token:   {total:,}   ({total/1e9:.2f}B)")
    print(f"缓存读取占比: {tcr/max(total,1)*100:.1f}%")
    print()
    print("注:数值已按 message.id 去重(Claude Code 会把一条回复拆成多行重复记账,按行累加会虚高)。")
    print("    以上为名义 token,实际计费按你所用模型的价格,别直接乘 Claude 标价。")


if __name__ == "__main__":
    main()
