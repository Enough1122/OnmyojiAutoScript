#!/usr/bin/env python3
"""技能体积体检 — 防"skill 内容爆炸"。

背景（2026-09-20 复盘）：曾有 github-oss-contribution-workflow 被打过 150 个 patch，
外加 5 个近义 GitHub 技能（71/53/27/26/16 个 patch），同一套知识在多个技能里反复增补。
这是 skill 爆炸的真身。

成本有两笔账，方向不同：
  ① 索引税(每轮)：每个技能的名称+描述进系统提示。随技能【数量】涨，与正文无关。
     官方口径 Level 0 ≈ 3k token。
  ② 正文税(加载后每轮)：skill_view 加载的正文【不会离开上下文】，
     会跟着之后每一轮请求重发，直到被压缩。随单个技能【体积】涨。

用法:
    python skill_size_audit.py            # 体检
    python skill_size_audit.py --json     # 机器可读
"""
import json
import os
import re
import sys
from pathlib import Path

BODY_WARN = 12_000      # 单个 SKILL.md 正文软上限(字符)
BODY_HARD = 20_000      # 硬上限: 超了必须拆 references/
PATCH_WARN = 30         # 单个技能 patch 次数告警(失控信号)
INDEX_WARN = 6_000      # 索引税告警(字符)


def home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "hermes"
    return Path.home() / ".hermes"


def bundled_names(skills_dir: Path) -> set:
    out = set()
    try:
        for line in (skills_dir / ".bundled_manifest").read_text(encoding="utf-8").splitlines():
            if ":" in line:
                out.add(line.split(":", 1)[0].strip())
    except OSError:
        pass
    return out


def main() -> int:
    sd = home() / "skills"
    bundled = bundled_names(sd)
    rows, index_chars = [], 0
    for p in sd.rglob("SKILL.md"):
        if ".curator_backups" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        name = p.parent.name
        m = re.search(r'^description:\s*"?(.*?)"?\s*$', text, re.M)
        desc = m.group(1).strip() if m else ""
        index_chars += len(name) + len(desc) + 4
        rows.append({
            "name": name,
            "rel": str(p.relative_to(sd)).replace("\\", "/"),
            "body_chars": len(text),
            "bundled": name in bundled,
        })

    try:
        usage = json.loads((sd / ".usage.json").read_text(encoding="utf-8"))
    except OSError:
        usage = {}

    for r in rows:
        u = usage.get(r["name"], {})
        r["patch_count"] = u.get("patch_count", 0)
        r["use_count"] = u.get("use_count", 0)

    rows.sort(key=lambda r: -r["body_chars"])
    report = {
        "skill_count": len(rows),
        "body_total_chars": sum(r["body_chars"] for r in rows),
        "index_chars": index_chars,
        "index_warn_at": INDEX_WARN,
        "body_warn_at": BODY_WARN,
        "over_body_warn": [r for r in rows if r["body_chars"] > BODY_WARN],
        "over_body_hard": [r for r in rows if r["body_chars"] > BODY_HARD],
        "over_patch_warn": sorted([r for r in rows if r["patch_count"] > PATCH_WARN],
                                  key=lambda r: -r["patch_count"]),
        "biggest": rows[:15],
    }
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"技能 {len(rows)} 个 | 正文合计 {report['body_total_chars']:,} 字符 "
          f"(不占上下文) | 索引税 {index_chars:,} 字符(每轮都在)")
    if index_chars > INDEX_WARN:
        print(f"  ⚠ 索引税偏高: 技能越多每轮越贵 -> 优先合并/删除近义技能")

    print("\n最大的 12 个正文:")
    for r in rows[:12]:
        flag = "⛔" if r["body_chars"] > BODY_HARD else ("⚠" if r["body_chars"] > BODY_WARN else "  ")
        tag = "[自带]" if r["bundled"] else "[自建]"
        print(f"  {flag} {r['body_chars']:7,}  {tag} {r['rel']}")

    if report["over_body_hard"]:
        print("\n⛔ 超硬上限(必须拆 references/):")
        for r in report["over_body_hard"]:
            print(f"   {r['body_chars']:,}  {r['rel']}")
    if report["over_patch_warn"]:
        print(f"\n⚠ patch 次数 >{PATCH_WARN} (失控信号, 该拆分或重组):")
        for r in report["over_patch_warn"]:
            print(f"   patch={r['patch_count']}  {r['name']}")
    if not report["over_body_hard"] and not report["over_patch_warn"]:
        print("\n✅ 无超限项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
