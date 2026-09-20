#!/usr/bin/env python3
"""对比本机 config.yaml 与 Hermes 官方默认值(config_defaults.DEFAULT_CONFIG)，列出所有非官方项。

用法: python config_drift.py [--json]
install 目录可用环境变量 HERMES_INSTALL 覆盖。
"""
import json
import os
import sys
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME") or (Path(os.environ["LOCALAPPDATA"]) / "hermes"))
INSTALL = Path(os.environ.get("HERMES_INSTALL") or (HOME / "hermes-agent"))

# 引擎自己写的簿记键，不算"用户配置"
IGNORE_TOP = {
    "_config_version", "known_plugin_toolsets", "known_builtin_toolsets",
    "platform_toolsets", "onboarding", "local_runtime", "desktop",
    "mcp_servers", "custom_providers", "providers", "platforms",
}


def norm(v):
    """宽松归一: 数字字符串 vs 数字、None/'', 空容器 vs 缺失。"""
    if isinstance(v, str):
        s = v.strip()
        try:
            return float(s)
        except ValueError:
            return s
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    if v is None:
        return "<none>"
    if isinstance(v, bool):
        return v
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def diff(user, default, path=""):
    out = []
    if isinstance(default, dict) and isinstance(user, dict):
        for k in sorted(set(user) | set(default)):
            p = f"{path}.{k}" if path else k
            if k not in default:
                out.append((p, user[k], "<键不在官方默认里>"))
            elif k not in user:
                continue  # 用户没写 = 跟随默认
            else:
                out += diff(user[k], default[k], p)
    else:
        if norm(user) != norm(default):
            out.append((path, user, default))
    return out


def main():
    import yaml
    sys.path.insert(0, str(INSTALL))
    from hermes_cli.config_defaults import DEFAULT_CONFIG as D

    cfg = yaml.safe_load((HOME / "config.yaml").read_text(encoding="utf-8")) or {}
    rows = []
    for key, uval in cfg.items():
        if key in IGNORE_TOP or key.startswith("_"):
            continue
        if key not in D:
            rows.append((key, uval, "<非官方键>"))
            continue
        rows += diff(uval, D[key], key)

    if "--json" in sys.argv:
        print(json.dumps([{"key": k, "local": v, "default": d} for k, v, d in rows],
                         ensure_ascii=False, indent=2, default=str))
        return 0

    print(f"非官方项 {len(rows)} 处  (config: {HOME / 'config.yaml'})\n")
    for k, v, d in rows:
        vs = json.dumps(v, ensure_ascii=False, default=str)
        ds = json.dumps(d, ensure_ascii=False, default=str)
        if len(vs) > 60:
            vs = vs[:57] + "..."
        if len(ds) > 40:
            ds = ds[:37] + "..."
        print(f"  {k}")
        print(f"      本机 = {vs}")
        print(f"      官方 = {ds}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
