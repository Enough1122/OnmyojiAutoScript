# -*- coding: utf-8 -*-
"""华通小时报的动态研究摘要测试。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from report import research_digest, session_state


class ReportTests(unittest.TestCase):
    def test_research_digest_uses_structured_state_and_caller_sample(self):
        with patch("report.research_state", return_value={
            "as_of": "day-750",
            "sample_size": 1,
            "observations": [
                {"name": "MACD金叉", "hold_days": 3, "holdout_audit": "通过"}
            ],
            "holdout_failed_observations": [],
        }) as research_state:
            result = research_digest([{"date": "day-750"}])

        research_state.assert_called_once_with([{"date": "day-750"}])
        self.assertIn("MACD金叉/3日", result)
        self.assertIn("day-750", result)
        self.assertIn("研究观察", result)
        self.assertIn("影子观察", result)
        self.assertIn("留出通过", result)
        self.assertIn("不等于生产信号", result)
        self.assertIn("研究假设", result)
        self.assertIn("非账户实际费率", result)
        self.assertIn("自动下单", result)

    def test_research_digest_marks_failed_holdout_audit(self):
        with patch("report.research_state", return_value={
            "as_of": "day-750",
            "sample_size": 1,
            "observations": [],
            "holdout_failed_observations": [
                {"name": "测试规则", "hold_days": 1, "holdout_audit": "未通过"}
            ],
        }):
            result = research_digest([{"date": "day-750"}])
        self.assertIn("研究观察留出未通过", result)
        self.assertIn("测试规则/1日（留出未通过）", result)
        self.assertIn("不等于生产信号", result)

    def test_research_digest_without_observation_keeps_non_production_boundary(self):
        with patch("report.research_state", return_value={
            "as_of": "day-750",
            "sample_size": 1,
            "observations": [],
            "holdout_failed_observations": [],
        }):
            result = research_digest([{"date": "day-750"}])

        self.assertIn("研究观察名单为空", result)
        self.assertIn("不等于生产信号", result)
        self.assertIn("不自动下单", result)

    def test_advice_is_observation_only_not_a_position_instruction(self):
        from report import build_advice

        advice = build_advice(
            "+2", 10.0,
            {"ma5": 9.0, "ma10": 9.0, "ma20": 8.0},
            {"bull_intact": True},
        )
        self.assertNotIn("可持", advice)
        self.assertNotIn("失效离场", advice)
        self.assertIn("观察", advice)
        self.assertIn("不构成交易", advice)

    def test_signal_tag_avoids_buy_sell_wording_for_observation_only_report(self):
        from report import signal_tag

        label = signal_tag("+2", 10.0, {"ma10": 9.0})
        self.assertNotIn("买", label)
        self.assertNotIn("卖", label)
        self.assertIn("技术偏多", label)
        self.assertIn("非交易指令", label)

    def test_signal_tag_marks_technical_direction_as_observation_only(self):
        from report import signal_tag

        label = signal_tag("+2", 10.0, {"ma10": 9.0})
        self.assertIn("观察", label)
        self.assertIn("非交易指令", label)

    def test_build_report_uses_one_750_bar_fetch_for_technical_and_research_views(self):
        from report import build_report

        bars = [
            {
                "date": f"day-{i:03d}",
                "open": 14.0,
                "close": 14.0,
                "high": 14.0,
                "low": 14.0,
                "volume": 1,
            }
            for i in range(750)
        ]
        with patch("report.get_realtime", return_value={
            "name": "世纪华通", "code": "002602", "price": 14.0,
            "change_pct": 0.0, "open": 14.0, "high": 14.0, "low": 14.0,
        }), patch("report.get_daily_kline", return_value=bars) as get_kline, patch(
            "report.cross_check", return_value=(True, []),
        ), patch("report.research_digest", return_value="研究摘要") as research_digest, patch(
            "report.generate_signal", return_value={
                "score": 0, "direction": "0", "reasons": [],
                "metrics": {"ma5": 14.0, "ma10": 14.0, "ma20": 14.0, "ma60": 14.0,
                            "hist": 0.0, "rsi14": 50.0, "kdj": (50.0, 50.0, 50.0)},
                "invalidation": {},
            }), patch("report.fund_snapshot", return_value=("业务", "估值")), patch(
            "report.news_line", return_value=None,
        ), patch("report.corp_actions_line", return_value=None):
            result = build_report()

        get_kline.assert_called_once_with(750)
        research_digest.assert_called_once_with(bars)
        self.assertIn("研究摘要", result)
    def test_build_report_uses_previous_complete_daily_bar_during_open_session(self):
        from report import build_report

        bars = [
            {
                "date": f"day-{i:03d}",
                "open": 14.0,
                "close": 14.0,
                "high": 14.0,
                "low": 14.0,
                "volume": 1,
            }
            for i in range(750)
        ]
        realtime = {
            "name": "世纪华通", "code": "002602", "price": 14.0,
            "change_pct": 0.0, "open": 14.0, "high": 14.0, "low": 14.0,
        }
        signal = {
            "score": 0, "direction": "0", "reasons": [],
            "metrics": {"ma5": 14.0, "ma10": 14.0, "ma20": 14.0, "ma60": 14.0,
                        "hist": 0.0, "rsi14": 50.0, "kdj": (50.0, 50.0, 50.0)},
            "invalidation": {},
        }
        with patch("report.get_realtime", return_value=realtime), patch(
            "report.get_daily_kline", return_value=bars
        ), patch("report.session_state", return_value="open"), patch(
            "report.cross_check", return_value=(True, [])
        ), patch("report.generate_signal", return_value=signal) as generate, patch(
            "report.research_digest", return_value="研究摘要"
        ), patch("report.fund_snapshot", return_value=("业务", "估值")), patch(
            "report.news_line", return_value=None
        ), patch("report.corp_actions_line", return_value=None):
            result = build_report()

        generate.assert_called_once_with(bars[-121:-1])
        self.assertIn("技术面", result)


if __name__ == "__main__":
    unittest.main()
