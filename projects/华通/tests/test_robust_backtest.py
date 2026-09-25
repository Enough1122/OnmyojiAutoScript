# -*- coding: utf-8 -*-
"""robust_backtest 的行为测试。"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robust_backtest import (
    aggregate_events,
    _fold_stability,
    build_research_report,
    buy_and_hold_costs,
    cash_return,
    cluster_events,
    cost_model,
    event_return,
    evaluate_event_rule,
    executable_event_indices,
    rolling_fold_means,
    select_non_overlapping_events,
    sell_to_cash_excess,
    signal_episodes,
    split_rows,
)


class RobustBacktestTests(unittest.TestCase):
    def test_cluster_events_keeps_first_and_ends_consecutive_episode(self):
        self.assertEqual(cluster_events([2, 3, 4, 8, 10, 11]), [2, 8, 10])

    def test_cost_model_sell_has_stamp_duty_and_round_trip_buy_has_none(self):
        buy, sell = cost_model(commission_rate=0.0002, min_commission=0.0, slippage_bps=10)
        self.assertAlmostEqual(buy, 0.0002 + 0.001)
        self.assertAlmostEqual(sell, 0.0002 + 0.0005 + 0.001)
        self.assertGreater(sell, buy)

    def test_buy_and_hold_costs_charges_each_side_once(self):
        ret = buy_and_hold_costs(100.0, 110.0, buy_cost=0.002, sell_cost=0.002)
        self.assertAlmostEqual(ret, 110 * (1 - 0.002) / (100 * (1 + 0.002)) - 1)

    def test_event_return_enters_next_open_and_exits_after_holding_open(self):
        bars = [
            {"date": "2026-01-01", "open": 10, "close": 10, "high": 10, "low": 10, "volume": 1},
            {"date": "2026-01-02", "open": 11, "close": 12, "high": 12, "low": 11, "volume": 1},
            {"date": "2026-01-03", "open": 12, "close": 13, "high": 13, "low": 12, "volume": 1},
            {"date": "2026-01-04", "open": 14, "close": 14, "high": 14, "low": 14, "volume": 1},
            {"date": "2026-01-05", "open": 15, "close": 15, "high": 15, "low": 15, "volume": 1},
        ]
        ret = event_return(bars, signal_i=0, direction=1, hold_days=3, buy_cost=0.002, sell_cost=0.002)
        self.assertAlmostEqual(ret, 15 * (1 - 0.002) / (11 * (1 + 0.002)) - 1)

    def test_sell_to_cash_excess_compares_cash_path_with_holding_mark_to_market(self):
        # 现金路径只承担本次卖出成本；继续持有路径只比较未来价格变化。
        expected = -0.002 - (8 / 10 - 1)
        self.assertAlmostEqual(sell_to_cash_excess(10, 8, 0.002, 0.002), expected)
        self.assertAlmostEqual(
            sell_to_cash_excess(10, 8, 0.002, 0.002),
            sell_to_cash_excess(10, 8, 0.5, 0.002),
        )

    def test_select_non_overlapping_events_excludes_entry_date_but_allows_exit_date(self):
        # 信号2：入场3、持有3日，退出6；信号3与持仓重叠，信号6可在退出日收盘后确认。
        self.assertEqual(select_non_overlapping_events([2, 3, 6], hold_days=3), [2, 6])

    def test_rolling_fold_means_uses_chronological_equal_event_folds(self):
        values = [float(i) for i in range(12)]
        folds = rolling_fold_means(values, fold_count=3, minimum_events=1)
        self.assertEqual(len(folds), 3)
        self.assertEqual([fold["start"] for fold in folds], [0, 4, 8])
        self.assertEqual([fold["end"] for fold in folds], [4, 8, 12])
        self.assertAlmostEqual(folds[0]["mean"], 1.5)
        self.assertAlmostEqual(folds[1]["mean"], 5.5)
        self.assertAlmostEqual(folds[2]["mean"], 9.5)

    def test_rolling_fold_means_skips_small_folds(self):
        folds = rolling_fold_means([1.0, 2.0, 3.0], fold_count=3, minimum_events=2)
        self.assertEqual(folds, [])

    def test_select_non_overlapping_events_keeps_first_entry_in_each_holding_period(self):
        self.assertEqual(select_non_overlapping_events([2, 4, 6, 10], hold_days=3), [2, 6, 10])
        self.assertEqual(select_non_overlapping_events([2, 4, 6, 10], hold_days=5), [2, 10])
        self.assertEqual(select_non_overlapping_events([2, 4, 6, 10], hold_days=0), [2, 4, 6, 10])

    def test_research_snapshot_reports_dynamic_candidates_and_no_stale_high_confidence_claim(self):
        from robust_backtest import snapshot
        original_get_daily_kline = __import__("robust_backtest").get_daily_kline
        try:
            __import__("robust_backtest").get_daily_kline = lambda days: [
                {
                    "date": f"day-{i:03d}",
                    "open": 100.0 + i,
                    "close": 100.0 + i,
                    "high": 100.0 + i,
                    "low": 100.0 + i,
                    "volume": 1,
                }
                for i in range(1, 131)
            ]
            result = snapshot()
            self.assertEqual(result["as_of"], "day-130")
            self.assertEqual(result["candidates"], [])
            self.assertIn("研究观察", result["report"])
            self.assertIn("研究假设", result["report"])
            self.assertIn("留出仅单独标记", result["report"])
            self.assertNotIn("2026-09-20", result["report"])
            self.assertNotIn("高置信信号", result["report"])
        finally:
            __import__("robust_backtest").get_daily_kline = original_get_daily_kline

    def test_sell_event_is_exit_to_cash_not_unlimited_short_sale(self):
        bars = [
            {"date": "2026-01-01", "open": 10, "close": 10, "high": 10, "low": 10, "volume": 1},
            {"date": "2026-01-02", "open": 10, "close": 10, "high": 10, "low": 10, "volume": 1},
            {"date": "2026-01-03", "open": 8, "close": 8, "high": 8, "low": 8, "volume": 1},
        ]
        got = event_return(bars, 0, -1, 1, 0.002, 0.002)
        self.assertAlmostEqual(got, sell_to_cash_excess(10, 8, 0.002, 0.002))
        self.assertAlmostEqual(got, -0.002 - (8 / 10 - 1))

    def test_aggregate_events_reports_mean_hit_and_median(self):
        result = aggregate_events([
            {"direction": 1, "return": 0.02},
            {"direction": 1, "return": -0.01},
            {"direction": -1, "return": 0.03},
        ])
        self.assertEqual(result["n"], 3)
        self.assertAlmostEqual(result["mean_return"], (0.02 - 0.01 + 0.03) / 3)
        self.assertAlmostEqual(result["hit_rate"], 2 / 3)
        self.assertAlmostEqual(result["median_return"], 0.02)

    def test_split_rows_disjoint_and_complete(self):
        rows = list(range(10))
        first, second = split_rows(rows, 0.6)
        self.assertEqual(first, list(range(6)))
        self.assertEqual(second, list(range(6, 10)))
        self.assertFalse(set(first) & set(second))

    def test_signal_episodes_returns_independent_events_only(self):
        class FakeData:
            def get_daily_kline(self, days):
                return [
                    {"date": f"2026-01-{i:02d}", "open": 100, "close": 100, "high": 100, "low": 100, "volume": 1}
                    for i in range(1, 11)
                ]

        sig = signal_episodes(FakeData(), rule="ma_cross", side="buy")
        events = sig["events"]
        self.assertIn("MA5/10金叉", events)
        self.assertEqual(events["MA5/10金叉"], [])
        # RSI 超卖也会连续多日触发，必须只保留独立事件首日。
        class OversoldData:
            def get_daily_kline(self, days):
                return [
                    {"date": f"day-{i:02d}", "open": 200 - i, "close": 200 - i, "high": 200 - i, "low": 200 - i, "volume": 1}
                    for i in range(1, 71)
                ]
        fake = signal_episodes(OversoldData(), rule={"name": "RSI超卖(<30)", "kind": "rsi", "threshold": 30, "side": 1})
        self.assertEqual(len(fake["events"]["RSI超卖(<30)"]), 1)

    def test_executable_event_indices_drops_incomplete_tail_before_overlap_filter(self):
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(10)
        ]
        # 持有2日：信号7/8无法完成，信号3和6可完成；信号3后仍保留6。
        self.assertEqual(executable_event_indices([3, 6, 7, 8], bars, 2), [3, 6])
        self.assertEqual(executable_event_indices([3, 4], bars, 2), [3, 4])

    def test_research_rows_keeps_quarantine_events_only_for_full_sample_folds(self):
        import robust_backtest as rb
        bars = [{"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1} for i in range(130)]
        rule = {"name": "测试", "side": 1, "kind": "rsi", "threshold": 30}
        original_rules = rb.RULES
        original_episodes = rb.signal_episodes_from_series
        original_split = rb._split_indices
        try:
            rb.RULES = [rule]
            rb.signal_episodes_from_series = lambda _bars, _rule: {
                "series": {}, "events": {"测试": [65, 67, 70, 79, 80, 90, 100, 105, 110, 115, 120, 125]}
            }
            rb._split_indices = lambda _bars, _rule, _hold_days: (
                [65, 67], [79, 80, 90, 100, 105, 110, 115], [120, 125]
            )
            row = rb._research_rows(bars)[0]
            self.assertEqual(row["hold_days"], 1)
            self.assertEqual(row["train_n"], 2)
            self.assertEqual(row["validation_n"], 6)
            self.assertEqual(row["holdout_n"], 2)
            self.assertEqual(row["all_n"], 11)
            # 稳定性筛选只看留出段之前的事件；全历史折仅作描述统计。
            self.assertEqual(row["stability"]["total_folds"], 0)
            self.assertEqual(row["full_stability"]["total_folds"], 3)
        finally:
            rb.RULES = original_rules
            rb.signal_episodes_from_series = original_episodes
            rb._split_indices = original_split

    def test_final_holdout_is_audit_only_not_a_filter_on_research_grade(self):
        import robust_backtest as rb
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(140)
        ]
        rule = {"name": "测试", "side": 1, "kind": "rsi", "threshold": 30}
        original_rules = rb.RULES
        original_episodes = rb.signal_episodes_from_series
        original_split = rb._split_indices
        original_return = rb.event_return
        try:
            rb.RULES = [rule]
            rb.signal_episodes_from_series = lambda _bars, _rule: {
                "series": {},
                "events": {"测试": [60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 100, 102, 104, 106, 108, 120, 122, 124, 126, 128]},
            }
            rb._split_indices = lambda _bars, _rule, _hold_days: (
                [60, 62, 64, 66, 68, 70, 72, 74, 76, 78],
                [100, 102, 104, 106, 108],
                [120, 122, 124, 126, 128],
            )
            rb.event_return = lambda _bars, index, _side, _hold, _buy_cost, _sell_cost: (
                -0.01 if index >= 120 else 0.01
            )
            row = rb._research_rows(bars)[0]
        finally:
            rb.RULES = original_rules
            rb.signal_episodes_from_series = original_episodes
            rb._split_indices = original_split
            rb.event_return = original_return
        self.assertEqual(row["grade"], rb.RESEARCH_OBSERVATION)
        self.assertEqual(row["holdout_audit"], "未通过")

    def test_snapshot_keeps_pre_holdout_observations_separate_from_holdout_audit(self):
        import robust_backtest as rb
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(130)
        ]
        row = {
            "name": "测试", "side": 1, "hold_days": 3,
            "train_n": 10, "train_mean": 0.01,
            "validation_n": 6, "validation_mean": 0.01,
            "holdout_n": 6, "holdout_mean": -0.01,
            "holdout_audit": "未通过", "all_n": 22,
            "stability": {"label": "全折为正", "positive_folds": 3, "total_folds": 3, "folds": []},
            "full_stability": {"label": "全折为正", "positive_folds": 3, "total_folds": 3, "folds": []},
            "cost_sensitivity": [{"cost": "低", "n": 10, "mean_return": 0.01, "hit_rate": 0.6, "median_return": 0.01}],
            "grade": rb.RESEARCH_OBSERVATION,
        }
        original = rb._research_rows
        try:
            rb._research_rows = lambda _bars: [row]
            state = rb.research_state(bars)
            snap = rb.snapshot(bars)
        finally:
            rb._research_rows = original
        self.assertEqual(state["research_observations"], [row])
        self.assertEqual(state["observations"], [])
        self.assertEqual(state["holdout_failed_observations"], [row])
        self.assertEqual(state["holdout_passed_observations"], [])
        self.assertEqual(snap["holdout_failed_observations"], [row])
        self.assertEqual(snap["holdout_passed_observations"], [])
        # 三天一次的回测报告不得把留出未通过的规则写进观察名单。
        self.assertNotIn("研究观察名单（留出通过）：测试/3日", snap["report"])
        self.assertIn("研究观察", snap["report"])

    def test_empty_holdout_does_not_change_pre_holdout_research_grade(self):
        import robust_backtest as rb
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(140)
        ]
        rule = {"name": "测试", "side": 1, "kind": "rsi", "threshold": 30}
        original_rules = rb.RULES
        original_episodes = rb.signal_episodes_from_series
        original_split = rb._split_indices
        original_return = rb.event_return
        try:
            rb.RULES = [rule]
            rb.signal_episodes_from_series = lambda _bars, _rule: {
                "series": {},
                "events": {"测试": [60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 100, 102, 104, 106, 108]},
            }
            rb._split_indices = lambda _bars, _rule, _hold_days: (
                [60, 62, 64, 66, 68, 70, 72, 74, 76, 78],
                [100, 102, 104, 106, 108],
                [],
            )
            rb.event_return = lambda _bars, index, _side, _hold, _buy_cost, _sell_cost: 0.01
            row = rb._research_rows(bars)[0]
        finally:
            rb.RULES = original_rules
            rb.signal_episodes_from_series = original_episodes
            rb._split_indices = original_split
            rb.event_return = original_return
        self.assertEqual(row["grade"], rb.RESEARCH_OBSERVATION)
        self.assertEqual(row["holdout_n"], 0)
        self.assertEqual(row["holdout_audit"], "样本不足")

    def test_final_holdout_audit_does_not_change_research_observation_grade(self):
        import robust_backtest as rb
        # 直接验证：最终留出只输出核验结果，不用它把训练/验证阶段的研究观察改成生产候选。
        self.assertEqual(rb._grade(0.02, 0.01, 10, 8), rb.RESEARCH_OBSERVATION)
        self.assertEqual(rb._final_holdout_audit(0.04, 8), "通过")
        self.assertEqual(rb._final_holdout_audit(-0.01, 8), "未通过")
        self.assertEqual(rb._final_holdout_audit(0.01, 2), "样本不足")

    def test_min_commission_is_not_silently_ignored(self):
        # 百分比成本模型没有本金/手数，无法直接计算最低佣金；
        # 传入该参数时必须拒绝，而不是假装已经计入。
        with self.assertRaises(NotImplementedError):
            cost_model(min_commission=5.0)
        self.assertEqual(cost_model(min_commission=0.0), cost_model())

    def test_cost_sensitivity_uses_the_provided_executable_event_set(self):
        import robust_backtest as rb
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(10)
        ]
        rule = {"name": "测试", "kind": "rsi", "threshold": 30, "side": 1}
        original = rb.signal_episodes_from_series
        try:
            rb.signal_episodes_from_series = lambda _bars, _rule: {
                "series": {}, "events": {"测试": [0, 2, 4, 6, 8]}
            }
            rows = rb._cost_sensitivity(bars, rule, 2, indices=[0, 2, 4])
        finally:
            rb.signal_episodes_from_series = original
        self.assertTrue(all(row["n"] == 2 for row in rows))

    def test_evaluate_event_rule_applies_holding_period_overlap_filter(self):
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(9)
        ]
        rule = {
            "name": "测试重叠",
            "side": 1,
            "events": {"测试重叠": [0, 1, 2, 5]},
            "directions": {"测试重叠": 1},
        }
        result = evaluate_event_rule(bars, rule, [2])
        self.assertEqual(result[0]["n"], 2)  # 信号0和5可成交；1、2与持仓重叠

    def test_evaluate_event_rule_ignores_incomplete_tail_signal(self):
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(6)
        ]
        rule = {
            "name": "测试尾部",
            "side": 1,
            "events": {"测试尾部": [0, 3]},
            "directions": {"测试尾部": 1},
        }
        result = evaluate_event_rule(bars, rule, [2])
        self.assertEqual(result[0]["n"], 1)  # 信号3无法完成到退出开盘

    def test_evaluate_event_rule_does_not_count_sell_as_short_profit(self):
        bars = [
            {"date": "2026-01-01", "open": 10, "close": 10, "high": 10, "low": 10, "volume": 1},
            {"date": "2026-01-02", "open": 10, "close": 10, "high": 10, "low": 10, "volume": 1},
            {"date": "2026-01-03", "open": 9, "close": 9, "high": 9, "low": 9, "volume": 1},
            {"date": "2026-01-04", "open": 9, "close": 9, "high": 9, "low": 9, "volume": 1},
        ]
        rule = {
            "name": "测试",
            "kind": "cross",
            "a": "ma5",
            "b": "ma10",
            "side": -1,
            "events": {"x": [0]},
            "directions": {"x": -1},
        }
        result = evaluate_event_rule(bars, rule, [1], aggregate_split=False)
        by_horizon = {r["hold_days"]: r for r in result}
        # 这里方向是卖出，价格先跌后卖，卖出相对继续持有应得到正超额。
        self.assertGreater(by_horizon[1]["mean_return"], 0)

    def test_math_helpers_do_not_accept_nonfinite_values(self):
        self.assertFalse(math.isfinite(float("nan")))
    def test_split_indices_keeps_train_validation_and_holdout_separated(self):
        import robust_backtest as rb
        bars = [
            {"date": f"day-{i:03d}", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1}
            for i in range(200)
        ]
        rule = {"name": "测试", "side": 1, "kind": "rsi", "threshold": 30}
        original = rb.signal_episodes_from_series
        try:
            rb.signal_episodes_from_series = lambda _bars, _rule: {
                "series": {}, "events": {"测试": [70, 80, 100, 105, 115, 120, 130, 140, 150, 160, 170, 180, 190]}
            }
            train, validation, holdout = rb._split_indices(bars, rule, hold_days=3)
        finally:
            rb.signal_episodes_from_series = original
        # 60%训练、80%起最终留出；两段之间各有10个交易日隔离带。
        self.assertEqual(train, [70, 80, 100, 105])
        self.assertEqual(validation, [120, 130, 140])
        self.assertEqual(holdout, [160, 170, 180, 190])


if __name__ == "__main__":
    unittest.main()
