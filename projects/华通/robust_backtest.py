# -*- coding: utf-8 -*-
"""可成交、事件去重、计入成本的稳健回测。

口径：
- 收盘确认信号，次日开盘执行；
- 连续信号日只保留首日；
- 买入信号报告买入后净收益；
- 卖出信号报告卖出后持币相对继续持有的超额；
- 两者都扣成本；不假设无限卖空。
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from typing import Any, Iterable

from analyze import cross_down, cross_up, ema_series, kdj_series, ma_series, rsi_series
from stock_data import NAME, get_daily_kline

RULES: list[dict[str, Any]] = [
    {"name": "MA5/10金叉", "kind": "cross", "a": "ma5", "b": "ma10", "side": 1},
    {"name": "MA5/10死叉", "kind": "cross", "a": "ma5", "b": "ma10", "side": -1},
    {"name": "MACD金叉", "kind": "cross", "a": "dif", "b": "dea", "side": 1},
    {"name": "MACD死叉", "kind": "cross", "a": "dif", "b": "dea", "side": -1},
    {"name": "RSI超卖(<30)", "kind": "rsi", "threshold": 30, "side": 1},
    {"name": "RSI超买(>70)", "kind": "rsi", "threshold": 70, "side": -1},
    {"name": "KDJ低位金叉(K<50)", "kind": "cross", "a": "k", "b": "d", "k_lt": 50, "side": 1},
    {"name": "KDJ高位死叉(K>50)", "kind": "cross", "a": "k", "b": "d", "k_gt": 50, "side": -1},
    {"name": "触及布林下轨", "kind": "boll", "edge": "lower", "side": 1},
    {"name": "触及布林上轨", "kind": "boll", "edge": "upper", "side": -1},
]
RULE_ALIASES = {
    "ma_cross": "MA5/10金叉",
    "ma_cross_buy": "MA5/10金叉",
    "ma_cross_sell": "MA5/10死叉",
    "rsi_oversold": "RSI超卖(<30)",
    "rsi_overbought": "RSI超买(>70)",
}
HORIZONS = (1, 3, 5, 10)
MIN_EVENTS = 8
BASE_WARMUP = 60
VALIDATION_MIN_EVENTS = 5
HOLDOUT_MIN_EVENTS = 5
TEST_EDGE = 0.003
RESEARCH_OBSERVATION = "研究观察·验证通过"
QUARANTINE_DAYS = 10
TRAIN_FRACTION = 0.6
HOLDOUT_START_FRACTION = 0.8


def cost_model(
    commission_rate: float = 0.0002,
    min_commission: float = 0.0,
    slippage_bps: float = 10,
    stamp_duty_rate: float = 0.0005,
) -> tuple[float, float]:
    """返回买入/卖出单边成本比例。"""
    if min_commission:
        raise NotImplementedError(
            "最低佣金依赖账户本金/成交金额，当前百分比成本模型未实现"
        )
    slippage = slippage_bps / 10000.0
    return commission_rate + slippage, commission_rate + stamp_duty_rate + slippage


def cash_return(buy_cost: float, sell_cost: float) -> float:
    """卖出已有持仓后持币的现金收益；建仓成本属于此前交易。"""
    del buy_cost
    return -sell_cost


def sell_to_cash_excess(
    entry_price: float,
    held_price: float,
    buy_cost: float,
    sell_cost: float,
) -> float:
    """卖出后持币相对继续持有的未来收益差。

    卖出时已经持有股票，不能再次计入买入成本；过去买入成本对两个分支
    都是沉没且相同的成本。现金分支在入场时卖出并持币，继续持有分支只
    比较未来价格变化；因此只扣现金分支本次卖出成本。
    """
    del buy_cost
    return -sell_cost - (held_price / entry_price - 1.0)


def buy_and_hold_costs(
    buy_price: float,
    sell_price: float,
    buy_cost: float,
    sell_cost: float,
) -> float:
    return sell_price * (1.0 - sell_cost) / (buy_price * (1.0 + buy_cost)) - 1.0


def cluster_events(indices: Iterable[int], gap: int = 1) -> list[int]:
    out: list[int] = []
    last_raw: int | None = None
    for index in sorted({int(i) for i in indices}):
        if last_raw is None or index - last_raw > gap:
            out.append(index)
        last_raw = index
    return out


def executable_event_indices(
    indices: Iterable[int],
    bars: list[dict[str, Any]],
    hold_days: int,
) -> list[int]:
    """先丢弃无法完成次日开盘入场的信号，再做持有期去重。"""
    if hold_days < 0:
        raise ValueError("hold_days must be non-negative")
    latest_signal = len(bars) - hold_days - 2
    return [int(index) for index in indices if 0 <= int(index) <= latest_signal]


def select_non_overlapping_events(indices: Iterable[int], hold_days: int) -> list[int]:
    """同一持有期内只保留最早的一笔信号，避免重叠交易重复计数。

    ``cluster_events`` 只去除连续触发日（同一根信号柱反复确认）；本函数
    处理另一种重复：两笔交易尚未平仓又出现新信号。比如持有 3 日时，
    信号 2 的实际平仓点是 2+1+3=6，信号 6 虽然不是连续触发，仍与其重叠，
    统计里不能当作一笔独立交易。

    边界是 ``index >= last_exit``：信号恰好落在上一笔平仓当日时，其最早
    可执行日就是平仓日，按序接在上一笔之后算独立事件。
    """
    if hold_days < 0:
        raise ValueError("hold_days must be non-negative")
    out: list[int] = []
    last_exit: int | None = None
    for index in sorted({int(i) for i in indices}):
        if last_exit is None or index >= last_exit:
            out.append(index)
            last_exit = index + 1 + hold_days
    return out


def event_return(
    bars: list[dict[str, Any]],
    signal_i: int,
    direction: int,
    hold_days: int,
    buy_cost: float,
    sell_cost: float,
) -> float | None:
    """买入方向返回净持有收益；卖出方向返回卖出持币相对持有的超额。"""
    if signal_i < 0 or signal_i >= len(bars) or hold_days < 0:
        return None
    entry_i = signal_i + 1
    exit_i = entry_i + hold_days
    if entry_i >= len(bars) or exit_i >= len(bars):
        return None
    entry = bars[entry_i]["open"]
    exit_price = bars[exit_i]["open"]
    if entry <= 0 or exit_price <= 0:
        return None
    held_return = buy_and_hold_costs(entry, exit_price, buy_cost, sell_cost)
    if direction > 0:
        return held_return
    # 卖出后持币相对继续持有的未来收益差；不重复扣过去的买入成本。
    return sell_to_cash_excess(entry, exit_price, buy_cost, sell_cost)


def aggregate_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    values = sorted(
        event["return"] for event in events
        if event.get("return") is not None and math.isfinite(event["return"])
    )
    if not values:
        return {"n": 0, "mean_return": None, "hit_rate": None, "median_return": None}
    return {
        "n": len(values),
        "mean_return": sum(values) / len(values),
        "hit_rate": sum(value > 0 for value in values) / len(values),
        "median_return": statistics.median(values),
    }


def split_rows(rows: list[Any], train_fraction: float = 0.6) -> tuple[list[Any], list[Any]]:
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    cut = int(len(rows) * train_fraction)
    return rows[:cut], rows[cut:]


def _series(klines: list[dict[str, Any]]) -> dict[str, Any]:
    closes = [bar["close"] for bar in klines]
    ma5, ma10 = ma_series(closes, 5), ma_series(closes, 10)
    ema_fast, ema_slow = ema_series(closes, 12), ema_series(closes, 26)
    dif = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
    rsi = rsi_series(closes, 14)
    k, d, _ = kdj_series(klines, 9)
    boll: list[tuple[float, float, float] | None] = []
    for index in range(len(closes)):
        if index < 19:
            boll.append(None)
            continue
        window = closes[index - 19:index + 1]
        middle = sum(window) / 20
        deviation = statistics.pstdev(window)
        boll.append((middle - 2 * deviation, middle, middle + 2 * deviation))
    return {
        "ma5": ma5,
        "ma10": ma10,
        "dif": dif,
        "dea": ema_series(dif, 9),
        "rsi": rsi,
        "k": k,
        "d": d,
        "boll": boll,
    }


def _condition(rule: dict[str, Any], value: float) -> bool:
    return (
        (rule.get("k_lt") is None or value < rule["k_lt"])
        and (rule.get("k_gt") is None or value > rule["k_gt"])
    )


def _raw_indices(
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
    series: dict[str, Any] | None = None,
) -> list[int]:
    series = series or _series(bars)
    raw: list[int] = []
    for index in range(BASE_WARMUP, len(bars)):
        if rule["kind"] == "cross":
            first, second = series[rule["a"]], series[rule["b"]]
            if first[index - 1] is None or first[index] is None or second[index - 1] is None or second[index] is None:
                continue
            if rule["side"] > 0:
                crossed = first[index - 1] <= second[index - 1] and first[index] > second[index]
            else:
                crossed = first[index - 1] >= second[index - 1] and first[index] < second[index]
            if crossed and _condition(rule, first[index]):
                raw.append(index)
        elif rule["kind"] == "rsi":
            value = series["rsi"][index]
            if value is not None and ((rule["side"] > 0 and value <= rule["threshold"]) or (rule["side"] < 0 and value >= rule["threshold"])):
                raw.append(index)
        elif rule["kind"] == "boll":
            band = series["boll"][index]
            if band and ((rule["edge"] == "lower" and bars[index]["close"] <= band[0] * 1.005) or (rule["edge"] == "upper" and bars[index]["close"] >= band[2] * 0.995)):
                raw.append(index)
    return raw


def _rule_by_name(name: str) -> dict[str, Any]:
    for rule in RULES:
        if rule["name"] == name:
            return rule
    raise KeyError(name)


def signal_episodes_from_series(
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
) -> dict[str, Any]:
    series = _series(bars)
    name = rule["name"]
    return {"series": series, "events": {name: cluster_events(_raw_indices(bars, rule, series))}}


def signal_episodes(
    data_source: Any,
    rule: str | dict[str, Any] | None = None,
    side: int | None = None,
) -> dict[str, Any]:
    bars = data_source.get_daily_kline(750)
    series = _series(bars)
    selected = RULES if side is None else [item for item in RULES if item["side"] == side]
    if isinstance(rule, str):
        selected = [_rule_by_name(RULE_ALIASES.get(rule, rule))]
    elif isinstance(rule, dict):
        selected = [rule]
    return {
        "bars": bars,
        "series": series,
        "events": {item["name"]: cluster_events(_raw_indices(bars, item, series)) for item in selected},
    }


def _event_values(
    bars: list[dict[str, Any]],
    indices: list[int],
    side: int,
    hold_days: int,
    buy_cost: float,
    sell_cost: float,
) -> list[float]:
    values: list[float] = []
    for index in indices:
        value = event_return(bars, index, side, hold_days, buy_cost, sell_cost)
        if value is not None:
            values.append(value)
    return values


def evaluate_event_rule(
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
    horizons: Iterable[int] = HORIZONS,
    aggregate_split: bool = True,
) -> list[dict[str, Any]]:
    """返回每个持有期的净收益/卖出超额统计。"""
    del aggregate_split
    buy_cost, sell_cost = cost_model()
    if "events" in rule and "directions" in rule:
        name = rule.get("name", next(iter(rule["events"])))
        indices_by_name = {key: list(value) for key, value in rule["events"].items()}
        directions = rule["directions"]
    else:
        name = rule["name"]
        indices_by_name = signal_episodes_from_series(bars, rule)["events"]
        directions = {name: rule["side"]}
    results = []
    for hold_days in horizons:
        events = []
        for event_name, indices in indices_by_name.items():
            side = directions[event_name]
            for index in select_non_overlapping_events(
                executable_event_indices(indices, bars, hold_days), hold_days
            ):
                value = event_return(bars, index, side, hold_days, buy_cost, sell_cost)
                if value is not None:
                    events.append({"return": value, "direction": side})
        results.append({"rule": name, "hold_days": hold_days, **aggregate_events(events)})
    return results


def _mean(values: Iterable[float | None]) -> float | None:
    clean = [value for value in values if value is not None and math.isfinite(value)]
    return sum(clean) / len(clean) if clean else None


def rolling_fold_means(
    values: Iterable[float],
    fold_count: int = 3,
    minimum_events: int = 3,
) -> list[dict[str, Any]]:
    """按事件时间顺序等分，返回达到最小样本量的滚动折统计。"""
    if fold_count < 2:
        raise ValueError("fold_count must be at least 2")
    clean = [float(value) for value in values if math.isfinite(value)]
    result: list[dict[str, Any]] = []
    for fold in range(fold_count):
        start = len(clean) * fold // fold_count
        end = len(clean) * (fold + 1) // fold_count
        chunk = clean[start:end]
        if len(chunk) < minimum_events:
            continue
        result.append({
            "start": start,
            "end": end,
            "n": len(chunk),
            "mean": sum(chunk) / len(chunk),
            "median": statistics.median(chunk),
            "hit_rate": sum(value > 0 for value in chunk) / len(chunk),
        })
    return result


def _fold_stability(folds: list[dict[str, Any]]) -> dict[str, Any]:
    if not folds:
        return {"label": "样本不足", "positive_folds": 0, "total_folds": 0, "folds": []}
    positive = sum(fold["mean"] > 0 for fold in folds)
    label = "全折为正" if positive == len(folds) else ("多数为正" if positive * 2 > len(folds) else "多数为负")
    return {"label": label, "positive_folds": positive, "total_folds": len(folds), "folds": folds}


def _cost_sensitivity(
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
    hold_days: int,
    indices: list[int] | None = None,
) -> list[dict[str, Any]]:
    """检验指定事件集合在几档成本下是否仍保持正期望。

    研究筛选只传入留出段之前的事件；完整历史成本统计可以显式传入全量事件。
    """
    if indices is None:
        indices = signal_episodes_from_series(bars, rule)["events"][rule["name"]]
    scenarios = [
        ("低", 0.0001, 0.0),
        ("基准", 0.0002, 0.001),
        ("高", 0.0003, 0.002),
    ]
    rows = []
    for label, commission, slippage in scenarios:
        buy_cost, sell_cost = cost_model(commission_rate=commission, slippage_bps=slippage * 10000)
        selected_indices = select_non_overlapping_events(
            executable_event_indices(indices, bars, hold_days), hold_days
        )
        values = _event_values(bars, selected_indices, rule["side"], hold_days, buy_cost, sell_cost)
        rows.append({"cost": label, **aggregate_events([{"return": value} for value in values])})
    return rows


def _split_indices(
    bars: list[dict[str, Any]],
    rule: dict[str, Any],
    hold_days: int = max(HORIZONS),
) -> tuple[list[int], list[int], list[int]]:
    """按时间切分训练/验证/最终留出，并用隔离带裁掉跨界事件。"""
    if hold_days < 0:
        raise ValueError("hold_days must be non-negative")
    train_cut = int(len(bars) * TRAIN_FRACTION)
    holdout_cut = int(len(bars) * HOLDOUT_START_FRACTION)
    train_end = train_cut - QUARANTINE_DAYS
    validation_end = holdout_cut - QUARANTINE_DAYS
    indices = signal_episodes_from_series(bars, rule)["events"][rule["name"]]
    train = [index for index in indices if index + 1 + hold_days < train_end]
    validation = [
        index for index in indices
        if train_cut <= index and index + 1 + hold_days < validation_end
    ]
    holdout = [index for index in indices if holdout_cut <= index < len(bars) - 1]
    return train, validation, holdout


def _grade(
    train_mean: float | None,
    validation_mean: float | None,
    train_n: int,
    validation_n: int,
) -> str:
    if train_mean is None or validation_mean is None or train_n < MIN_EVENTS or validation_n < VALIDATION_MIN_EVENTS:
        return "样本不足"
    if train_mean > 0 and validation_mean > TEST_EDGE:
        return RESEARCH_OBSERVATION
    if train_mean > 0 and validation_mean > 0:
        return "观察·边际弱"
    if train_mean > 0 and validation_mean < 0:
        return "不稳定"
    if train_mean < 0 and validation_mean < 0:
        return "不利"
    return "反转规则"


def _final_holdout_audit(mean_return: float | None, n: int) -> str:
    if mean_return is None or n < HOLDOUT_MIN_EVENTS:
        return "样本不足"
    return "通过" if mean_return > 0 else "未通过"


def _fmt_pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:+.2f}%"


def _research_rows(bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buy_cost, sell_cost = cost_model()
    rows = []
    for rule in RULES:
        indices = signal_episodes_from_series(bars, rule)["events"][rule["name"]]
        for hold_days in (1, 3, 5):
            # 整段研究统一重选非重叠事件；先保留测试段信号时，训练段边界事件会改变
            # 后续保留集合，因此不能用 train_indices + test_indices 作为 all_indices。
            all_indices = [index for index in indices if index < len(bars) - 1]
            train_indices, validation_indices, holdout_indices = _split_indices(
                bars, rule, hold_days
            )
            executable_indices = executable_event_indices(all_indices, bars, hold_days)
            train_selected = select_non_overlapping_events(
                executable_event_indices(train_indices, bars, hold_days), hold_days
            )
            validation_selected = select_non_overlapping_events(
                executable_event_indices(validation_indices, bars, hold_days), hold_days
            )
            holdout_selected = select_non_overlapping_events(
                executable_event_indices(holdout_indices, bars, hold_days), hold_days
            )
            all_selected = select_non_overlapping_events(executable_indices, hold_days)
            train_values = _event_values(bars, train_selected, rule["side"], hold_days, buy_cost, sell_cost)
            validation_values = _event_values(
                bars, validation_selected, rule["side"], hold_days, buy_cost, sell_cost
            )
            holdout_values = _event_values(
                bars, holdout_selected, rule["side"], hold_days, buy_cost, sell_cost
            )
            all_values = _event_values(bars, all_selected, rule["side"], hold_days, buy_cost, sell_cost)
            train_mean, validation_mean, holdout_mean = (
                _mean(train_values), _mean(validation_values), _mean(holdout_values)
            )
            # 稳定性/成本只使用留出段之前的数据；留出段仅作一次最终核验，
            # 不能反过来影响规则或持有期的筛选。
            pre_holdout_indices = [
                index for index in indices
                if index + 1 + hold_days < int(len(bars) * HOLDOUT_START_FRACTION)
            ]
            pre_holdout_selected = select_non_overlapping_events(
                executable_event_indices(pre_holdout_indices, bars, hold_days), hold_days
            )
            pre_holdout_values = _event_values(
                bars, pre_holdout_selected, rule["side"], hold_days, buy_cost, sell_cost
            )
            full_stability = _fold_stability(
                rolling_fold_means(all_values, fold_count=3, minimum_events=3)
            )
            stability = _fold_stability(
                rolling_fold_means(pre_holdout_values, fold_count=3, minimum_events=3)
            )
            costs = _cost_sensitivity(
                bars, rule, hold_days, pre_holdout_selected
            )
            cost_positive = [row["mean_return"] is not None and row["mean_return"] > 0 for row in costs]
            grade = "样本不足" if train_mean is None or validation_mean is None else _grade(
                train_mean, validation_mean, len(train_values), len(validation_values)
            )
            # 留出集只作一次性审计，不能改写训练/验证得到的研究等级。
            # 稳定性/成本筛选只看留出前事件；留出均值不改写研究等级。
            if grade == RESEARCH_OBSERVATION:
                if stability["label"] != "全折为正" or not all(cost_positive):
                    grade = "观察·稳定性不足"
            rows.append({
                "name": rule["name"],
                "side": rule["side"],
                "hold_days": hold_days,
                "train_n": len(train_values),
                "train_mean": train_mean,
                "validation_n": len(validation_values),
                "validation_mean": validation_mean,
                "holdout_n": len(holdout_values),
                "holdout_mean": holdout_mean,
                "holdout_audit": _final_holdout_audit(holdout_mean, len(holdout_values)),
                "all_n": len(all_values),
                "stability": stability,
                "full_stability": full_stability,
                "cost_sensitivity": costs,
                "grade": grade,
            })
    return rows


def research_state(bars: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """返回报告可直接消费的结构化研究状态，不解析 Markdown。

    ``observations`` 是对外的观察名单口径：既通过训练/验证，也通过最终留出。
    ``research_observations`` 只要求训练/验证通过，用来披露"留出未通过"的规则，
    避免把未通过留出的规则和留出通过的规则说成同一件事。
    """
    bars = get_daily_kline(750) if bars is None else bars
    rows = _research_rows(bars)
    research_observations = [
        row for row in rows if row["grade"] == RESEARCH_OBSERVATION
    ]
    return {
        "as_of": bars[-1]["date"] if bars else None,
        "sample_start": bars[0]["date"] if bars else None,
        "sample_size": len(bars),
        "rows": rows,
        "candidates": [],
        "research_observations": research_observations,
        "observations": [
            row for row in research_observations
            if row["holdout_audit"] == "通过"
        ],
        "holdout_passed_observations": [
            row for row in research_observations
            if row["holdout_audit"] == "通过"
        ],
        "holdout_failed_observations": [
            row for row in research_observations
            if row["holdout_audit"] == "未通过"
        ],
    }


def build_research_report(bars: list[dict[str, Any]] | None = None) -> str:
    bars = bars or get_daily_kline(750)
    if len(bars) < 120:
        return "❌ 数据不足（至少需要120根K线）"
    buy_cost, sell_cost = cost_model()
    lines = [
        f"🔬 {NAME}(002602) 稳健回测/策略研究",
        f"样本：{bars[0]['date']} ~ {bars[-1]['date']}（{len(bars)}根日K）",
        f"执行：收盘确认→次日开盘；成本为研究假设：买入{buy_cost:.2%}/卖出{sell_cost:.2%}（非账户实际费率）。",
        "买入栏是买入后净收益；卖出栏是卖出后持币相对继续持有的超额。",
        "",
        "**一、独立事件回测**",
        "| 规则 | 方向 | 持有 | n | 胜率 | 均值 | 中位数 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for rule in RULES:
        indices = signal_episodes_from_series(bars, rule)["events"][rule["name"]]
        for hold_days in HORIZONS:
            selected_indices = select_non_overlapping_events(
                executable_event_indices(indices, bars, hold_days), hold_days
            )
            values = _event_values(bars, selected_indices, rule["side"], hold_days, buy_cost, sell_cost)
            if not values:
                continue
            summary = aggregate_events([{"return": value} for value in values])
            lines.append(
                f"| {rule['name']} | {'买' if rule['side'] > 0 else '卖'} | {hold_days}日 | "
                f"{summary['n']} | {summary['hit_rate'] * 100:.0f}% | "
                f"{_fmt_pct(summary['mean_return'])} | {_fmt_pct(summary['median_return'])} |"
            )
    rows = _research_rows(bars)
    lines += [
        "",
        "**二、训练/验证/最终留出检验**",
        "按信号日期前60%训练、中间20%验证、后20%最终留出；训练/验证之间及验证/留出之间各留10个交易日。",
        "同一持有期内只保留首个可执行事件，避免重叠持仓被重复计样本。",
        "| 规则 | 持有 | 训练 n/均值 | 验证 n/均值 | 留出 n/均值 | 判定 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | {row['hold_days']}日 | {row['train_n']} / {_fmt_pct(row['train_mean'])} | "
            f"{row['validation_n']} / {_fmt_pct(row['validation_mean'])} | "
            f"{row['holdout_n']} / {_fmt_pct(row['holdout_mean'])} ({row['holdout_audit']}) | {row['grade']} |"
        )
    observation_rows = [
        row for row in rows
        if row["grade"] == RESEARCH_OBSERVATION
        and row["holdout_audit"] == "通过"
    ]
    lines += [
        "",
        "**三、筛选结论**",
    ]
    if observation_rows:
        lines.append("· 研究观察名单（留出通过）：" + "、".join(
            f"{row['name']}/{row['hold_days']}日" for row in observation_rows
        ) + "。")
    else:
        lines.append(
            "· 本轮没有研究观察规则同时通过验证、滚动折和成本敏感性门槛；最终留出只作独立审计。"
        )
    lines += [
        "· 研究观察门槛：训练/验证均正、验证>0.3%；最终留出仅单独标记通过/未通过，滚动折和成本敏感性只使用留出前事件。",
        "· 研究观察不是生产候选；最终留出只作一次性核验，未用于挑选规则或持有期。",
        "· 同一持有期内只保留首个事件，避免重叠持仓被重复计样本。",
        "· 买入栏是买入后净收益；卖出栏是卖出后持币相对继续持有的超额，不假设无限卖空。",
        "· 本回测只评估技术信号，基本面、公告和游戏出海数据另行接入。",
        "· 限制：当前百分比成本模型未实现账户最低佣金，也未模拟停牌、涨跌停、成交量/整手/资金容量。",
    ]
    return "\n".join(lines)


def snapshot(bars: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    bars = bars or get_daily_kline(750)
    rows = _research_rows(bars)
    return {
        "as_of": bars[-1]["date"],
        "sample_start": bars[0]["date"],
        "sample_size": len(bars),
        "cost_model": {
            "buy": cost_model()[0],
            "sell": cost_model()[1],
            "commission": 0.0002,
            "stamp_duty_sell": 0.0005,
            "slippage_bps_each_side": 10,
        },
        "rows": rows,
        "candidates": [],
        "observations": [
            row for row in rows
            if row["grade"] == RESEARCH_OBSERVATION
            and row["holdout_audit"] == "通过"
        ],
        "holdout_passed_observations": [
            row for row in rows
            if row["grade"] == RESEARCH_OBSERVATION
            and row["holdout_audit"] == "通过"
        ],
        "holdout_failed_observations": [
            row for row in rows
            if row["grade"] == RESEARCH_OBSERVATION
            and row["holdout_audit"] == "未通过"
        ],
        "report": build_research_report(bars),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=750)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()
    result = snapshot(get_daily_kline(args.days))
    print(result["report"])
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
