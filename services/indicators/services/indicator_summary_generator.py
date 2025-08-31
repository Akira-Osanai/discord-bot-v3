"""
インジケータサマリー生成処理
分析結果からサマリーと推奨事項を生成します
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class IndicatorSummaryGenerator:
    """インジケータサマリー生成クラス"""

    def generate_summary(
        self,
        indicator_states: Dict,
        buy_score: float,
        sell_score: float
    ) -> Dict:
        """サマリーを生成"""
        # 状態別カウント
        up_count = sum(1 for s in indicator_states.values()
                       if s["status"] == "up")
        down_count = sum(1 for s in indicator_states.values()
                         if s["status"] == "down")
        neutral_count = sum(1 for s in indicator_states.values()
                            if s["status"] == "neutral")

        # シグナル別カウント
        bullish_signals = ["bullish", "oversold"]
        bullish_count = sum(1 for s in indicator_states.values()
                            if s["signal"] in bullish_signals)
        bearish_count = sum(1 for s in indicator_states.values()
                            if s["signal"] in ["bearish", "overbought"])
        neutral_signal_count = sum(
            1 for s in indicator_states.values() if s["signal"] == "neutral")

        # タイプ別集計
        type_scores = self._calculate_type_scores(indicator_states)

        return {
            "counts": {
                "total": len(indicator_states),
                "up": up_count,
                "down": down_count,
                "neutral": neutral_count,
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral_signal": neutral_signal_count
            },
            "scores": type_scores,
            "overall_sentiment": self._get_overall_sentiment(
                buy_score, sell_score)
        }

    def _calculate_type_scores(self, indicator_states: Dict) -> Dict:
        """タイプ別スコアを計算"""
        trend_score = 0.0
        momentum_score = 0.0
        volatility_score = 0.0
        volume_score = 0.0

        for state in indicator_states.values():
            if state["type"] == "trend":
                trend_score += state["weight"] * \
                    (1 if state["signal"] == "bullish" else -1)
            elif state["type"] == "momentum":
                momentum_score += state["weight"] * \
                    (1 if state["signal"] in ["bullish", "oversold"] else -1)
            elif state["type"] == "volatility":
                volatility_score += state["weight"] * \
                    (1 if state["status"] == "up" else -1)
            elif state["type"] == "volume":
                volume_score += state["weight"] * \
                    (1 if state["status"] == "up" else -1)

        return {
            "trend": round(trend_score, 2),
            "momentum": round(momentum_score, 2),
            "volatility": round(volatility_score, 2),
            "volume": round(volume_score, 2)
        }

    def _get_overall_sentiment(self, buy_score: float, sell_score: float) -> str:
        """全体的なセンチメントを判定"""
        diff = buy_score - sell_score

        if diff > 20:
            return "強力な買い"
        elif diff > 10:
            return "買い"
        elif diff > -10:
            return "中立"
        elif diff > -20:
            return "売り"
        else:
            return "強力な売り"

    def get_recommendation(self, buy_score: float, sell_score: float) -> str:
        """売買推奨を生成"""
        diff = buy_score - sell_score

        if diff > 30:
            return "強力な買い推奨"
        elif diff > 15:
            return "買い推奨"
        elif diff > 5:
            return "弱い買い推奨"
        elif diff > -5:
            return "ホールド"
        elif diff > -15:
            return "弱い売り推奨"
        elif diff > -30:
            return "売り推奨"
        else:
            return "強力な売り推奨"
