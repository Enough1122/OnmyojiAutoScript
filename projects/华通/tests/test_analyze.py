# -*- coding: utf-8 -*-
"""华通技术评分去重与稳健研究接入测试。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyze import generate_signal, macd


class AnalyzeTests(unittest.TestCase):
    def test_macd_cross_and_histogram_flip_score_only_once(self):
        # 构造能产生 MACD 金叉及同根红柱翻正的数据；不依赖外部数据。
        closes = [10.0] * 26 + [9.8, 9.6, 9.5, 9.6, 9.8, 10.1, 10.5]
        klines = [
            {"date": f"day-{i:03d}", "open": c, "close": c, "high": c, "low": c, "volume": 1}
            for i, c in enumerate(closes, 1)
        ]
        dif, dea, hist = macd(closes)
        self.assertTrue(dif[-1] > dea[-1])
        self.assertTrue(hist[-1] > 0 and hist[-2] <= 0)

        result = generate_signal(klines)
        macd_reasons = [reason for reason in result["reasons"] if reason.startswith("MACD")]
        self.assertIn("MACD 金叉", macd_reasons)
        self.assertIn("MACD 红柱翻正", macd_reasons)

        # 同一 MACD 拐点只能贡献一次分数；柱体翻正只作为解释。
        neutral_ma = patch("analyze.ma_series", return_value=[0.0, 0.0])
        neutral_rsi = patch("analyze.rsi_series", return_value=[50.0, 50.0])
        neutral_kdj = patch("analyze.kdj_series", return_value=([50.0, 50.0], [50.0, 50.0], [50.0, 50.0]))
        neutral_boll = patch("analyze.boll", return_value=(-10.0, 0.0, 10.0))
        cross = ([-1.0, -0.1], [-0.5, -0.2], [-1.0, 1.0])
        with neutral_ma, neutral_rsi, neutral_kdj, neutral_boll, patch("analyze.macd", return_value=cross):
            result = generate_signal(
                [{"date": "day-001", "open": 1.0, "close": 1.0, "high": 1.0, "low": 1.0, "volume": 1},
                 {"date": "day-002", "open": 1.0, "close": 1.0, "high": 1.0, "low": 1.0, "volume": 1}],
                price_mode="off",
            )
        self.assertEqual(result["score"], 1)
        self.assertIn("MACD 金叉", result["reasons"])
        self.assertIn("MACD 红柱翻正", result["reasons"])


if __name__ == "__main__":
    unittest.main()
